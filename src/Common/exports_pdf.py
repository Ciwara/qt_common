#!usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga

"""Export PDF (ReportLab) — aligné sur exports_xlsx ; aperçu avant enregistrement."""

from __future__ import annotations

import base64
import os
import shutil
import tempfile
from datetime import datetime
from html import escape
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.platypus.tables import Table, TableStyle

from .cstatic import CConstants, logger
from .models import Organization
from .ui.util import openFile


def _rp(text) -> str:
    """Texte sûr pour ReportLab Paragraph (sous-ensemble HTML)."""
    if text is None:
        return ""
    return escape(str(text), quote=False).replace("\n", "<br/>")


def _decode_org_logo_bytes(logo_field) -> bytes | None:
    """logo_orga : chemin fichier, data URL base64 ou chaîne base64 (comme l’écran login)."""
    if not logo_field:
        return None
    if isinstance(logo_field, (bytes, bytearray)):
        return bytes(logo_field)
    s = str(logo_field).strip()
    if not s:
        return None
    # Data URL en premier : évite Path(...) sur une chaîne énorme → Errno 63 (nom trop long).
    if s.startswith("data:") and "," in s:
        b64_part = "".join(s.split(",", 1)[1].split())
        try:
            return base64.b64decode(b64_part, validate=False)
        except Exception:
            return None
    try:
        if len(s) <= 8192:
            p = Path(s)
            if p.is_file():
                return p.read_bytes()
    except OSError:
        pass
    compact = "".join(s.split())
    try:
        return base64.b64decode(compact, validate=False)
    except Exception:
        return None


def _build_org_logo_flowable(logo_field, max_width: float) -> RLImage | None:
    """Image ReportLab redimensionnée (ratio conservé si Pillow disponible)."""
    raw = _decode_org_logo_bytes(logo_field)
    if not raw:
        return None
    try:
        from PIL import Image as PILImage

        pil = PILImage.open(BytesIO(raw))
        pil.load()
        wi, hi = pil.size
        if wi > 0 and hi > 0:
            h = max_width * hi / float(wi)
            return RLImage(BytesIO(raw), width=max_width, height=h)
    except Exception:
        pass
    try:
        return RLImage(BytesIO(raw), width=max_width, height=max_width)
    except Exception:
        # logger.debug("Logo organisation non utilisable dans le PDF: %s", e)
        return None


def _default_col_widths(ncols: int, usable: float) -> list[float]:
    if ncols <= 0:
        return []
    if ncols == 5:
        ratios = [0.13, 0.37, 0.17, 0.17, 0.16]
    else:
        ratios = [1.0 / ncols] * ncols
    return [usable * r for r in ratios]


def _compose_pdf_story(dict_data: dict) -> tuple[list, str]:
    """Construit la liste de flowables ReportLab + titre pour métadonnées PDF."""
    title = str(dict_data.get("title") or "Export")
    date_raw = dict_data.get("date")
    if date_raw is None or str(date_raw) == "None":
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    else:
        date_str = str(date_raw)

    headers = list(dict_data.get("headers") or [])
    rows = dict_data.get("data") or []
    period = dict_data.get("period") or ""

    try:
        org = Organization.get(id=1)
    except Exception:
        org = None

    style_sheet = getSampleStyleSheet()
    style_cell = ParagraphStyle(
        "Cell",
        parent=style_sheet["Normal"],
        fontSize=8,
        leading=10,
        alignment=TA_LEFT,
    )
    style_title = ParagraphStyle(
        "DocTitle",
        parent=style_sheet["Heading1"],
        fontSize=15,
        leading=18,
        spaceAfter=6,
        textColor=HexColor("#1a237e"),
    )
    style_meta = ParagraphStyle(
        "Meta",
        parent=style_sheet["Normal"],
        fontSize=9,
        leading=12,
        textColor=HexColor("#424242"),
    )
    style_org = ParagraphStyle(
        "OrgHdr",
        parent=style_sheet["Normal"],
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
        textColor=HexColor("#212121"),
    )
    style_foot = ParagraphStyle(
        "GenFoot",
        parent=style_sheet["Normal"],
        fontSize=7,
        leading=9,
        textColor=colors.grey,
    )

    story: list = []

    if org:
        logo_max = 1.45 * inch
        logo_img = _build_org_logo_flowable(getattr(org, "logo_orga", None), logo_max)
        if logo_img:
            logo_wrap = Table(
                [[logo_img]],
                colWidths=[6.4 * inch],
            )
            logo_wrap.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            story.append(logo_wrap)
            story.append(Spacer(1, 10))
        story.append(Paragraph(_rp(org.name_orga), style_org))
        if getattr(org, "adress_org", None):
            story.append(Paragraph(_rp(org.adress_org), style_org))
        bits = []
        if getattr(org, "bp", None):
            bits.append(f"BP : {org.bp}")
        if getattr(org, "email_org", None):
            bits.append(f"E-mail : {org.email_org}")
        if bits:
            story.append(Paragraph(_rp("  ·  ".join(bits)), style_org))
        if getattr(org, "phone", None):
            story.append(Paragraph(_rp(f"Tél. : {org.phone}"), style_org))
        story.append(Spacer(1, 12))

    story.append(Paragraph(_rp(title), style_title))
    story.append(Paragraph(_rp(date_str), style_meta))

    for item in dict_data.get("others") or []:
        if len(item) >= 3 and item[2]:
            story.append(Paragraph(_rp(item[2]), style_meta))

    if period:
        story.append(Paragraph(_rp(period), style_meta))

    story.append(
        Paragraph(
            _rp(
                f"{CConstants.APP_NAME} — document généré le "
                f"{datetime.now().strftime('%d/%m/%Y à %H:%M')}"
            ),
            style_foot,
        )
    )
    story.append(Spacer(1, 12))

    if not headers:
        if not story:
            # logger.warning("Export PDF : document vide")
            pass
        return story, title

    ldata = [[Paragraph(_rp(h), style_cell) for h in headers]]
    for r in rows:
        row_table = []
        for cell in r:
            row_table.append(Paragraph(_rp(cell), style_cell))
        ldata.append(row_table)

    ncols = len(headers)
    usable_w = 6.35 * inch
    col_widths = _default_col_widths(ncols, float(usable_w))

    btable = Table(ldata, colWidths=col_widths, repeatRows=1)
    btable.hAlign = "LEFT"

    nrows = len(ldata)
    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E8EAF6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#1a237e")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#BDBDBD")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if nrows > 2:
        ts.append(
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -2),
                [colors.white, HexColor("#FAFAFA")],
            )
        )
    if nrows >= 2:
        ts += [
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, -1), (-1, -1), 9),
            ("BACKGROUND", (0, -1), (-1, -1), HexColor("#E8F5E9")),
            ("LINEABOVE", (0, -1), (-1, -1), 0.75, HexColor("#388E3C")),
        ]

    btable.setStyle(TableStyle(ts))
    story.append(btable)

    return story, title


def _render_pdf_bytes(dict_data: dict) -> bytes:
    story, doc_title = _compose_pdf_story(dict_data)
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.55 * inch,
        title=str(doc_title)[:120],
        author=str(CConstants.APP_NAME),
    )
    doc.build(story)
    return buf.getvalue()


def _show_pdf_preview_dialog(temp_path: str, file_base: str) -> str | None:
    """
    Aperçu du PDF puis « Enregistrer sous… ».
    Retourne le chemin choisi ou None (annulé).
    """
    try:
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import (
            QApplication,
            QDialog,
            QFileDialog,
            QHBoxLayout,
            QLabel,
            QPushButton,
            QVBoxLayout,
        )
    except ImportError:
        return None

    app = QApplication.instance()
    parent = app.activeWindow() if app else None

    dlg = QDialog(parent)
    dlg.setWindowTitle("Aperçu — PDF")
    dlg.resize(920, 720)
    dlg.setWindowModality(Qt.WindowModality.ApplicationModal)

    layout = QVBoxLayout(dlg)

    pdf_doc = None
    view = None
    try:
        from PyQt6.QtPdf import QPdfDocument
        from PyQt6.QtPdfWidgets import QPdfView

        pdf_doc = QPdfDocument(dlg)
        err = pdf_doc.load(temp_path)
        if err == QPdfDocument.Error.None_:
            view = QPdfView(dlg)
            view.setDocument(pdf_doc)
            try:
                view.setZoomMode(QPdfView.ZoomMode.FitInView)
            except Exception:
                pass
            layout.addWidget(view)
        else:
            raise RuntimeError(f"load pdf: {err}")
    except Exception:
        # logger.debug("Aperçu intégré QtPdf indisponible: %s", e)
        layout.addWidget(
            QLabel(
                "Aperçu intégré indisponible (installez PyQt6-QtPdf et PyQt6-QtPdfWidgets).\n"
                "Utilisez le bouton ci-dessous pour ouvrir le fichier dans votre lecteur PDF."
            )
        )
        btn_ext = QPushButton("Ouvrir dans le lecteur PDF…")
        btn_ext.clicked.connect(lambda: openFile(temp_path))
        layout.addWidget(btn_ext)

    btn_row = QHBoxLayout()
    btn_save = QPushButton("💾 Enregistrer sous…")
    btn_cancel = QPushButton("Annuler")
    btn_row.addStretch()
    btn_row.addWidget(btn_save)
    btn_row.addWidget(btn_cancel)
    layout.addLayout(btn_row)

    chosen: list[str | None] = [None]

    def _save():
        docs = Path.home() / "Documents"
        if not docs.is_dir():
            docs = Path.home()
        default = str(docs / f"{Path(str(file_base)).name}.pdf")
        path, _ = QFileDialog.getSaveFileName(
            dlg,
            "Enregistrer le PDF",
            default,
            "Documents PDF (*.pdf)",
        )
        if path:
            chosen[0] = path
            dlg.accept()

    btn_save.clicked.connect(_save)
    btn_cancel.clicked.connect(dlg.reject)

    dlg.exec()
    return chosen[0]


def export_dynamic_data(dict_data):
    """
    Génère le PDF, affiche l’aperçu, puis enregistre au chemin choisi.
    Même structure que ``exports_xlsx.export_dynamic_data``.
    """
    file_base = dict_data.get("file_name") or "export"

    try:
        pdf_bytes = _render_pdf_bytes(dict_data)
    except Exception as e:
        logger.exception("Erreur génération PDF: %s", e)
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox

            if QApplication.instance() is not None:
                QMessageBox.critical(
                    None,
                    "Export PDF",
                    "La génération du PDF a échoué.\n\n"
                    f"Détail : {e!s}",
                )
        except Exception:
            pass
        return

    fd, tmp_path = tempfile.mkstemp(suffix=".pdf", prefix="mpreview_")
    try:
        os.close(fd)
        with open(tmp_path, "wb") as f:
            f.write(pdf_bytes)

        dest = _show_pdf_preview_dialog(tmp_path, str(file_base))
        if not dest:
            logger.info("Export PDF : enregistrement annulé après aperçu")
            return

        shutil.copy2(tmp_path, dest)
        logger.info("PDF enregistré : %s", dest)
        abs_dest = os.path.abspath(os.path.normpath(dest))
        opened = False
        try:
            from PyQt6.QtCore import QUrl
            from PyQt6.QtGui import QDesktopServices
            from PyQt6.QtWidgets import QApplication

            if QApplication.instance() is not None:
                opened = bool(
                    QDesktopServices.openUrl(QUrl.fromLocalFile(abs_dest))
                )
        except Exception as e:
            logger.debug("QDesktopServices.openUrl PDF: %s", e)
        if not opened and openFile(abs_dest) != 0:
            logger.warning(
                "Impossible d’ouvrir le PDF automatiquement : %s", abs_dest
            )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
