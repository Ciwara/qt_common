#!usr/bin/env python
# -*- coding= UTF-8 -*-
# maintainer: Fadiga

"""Export XLSX (xlsxwriter) — même flux que exports_pdf : fichier temporaire, dialogue, enregistrer sous, ouverture."""

from __future__ import annotations

import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import xlsxwriter

from .cstatic import CConstants, logger
from .models import Organization
from .org_logo import write_org_logo_temp_file
from .ui.util import openFile

style_org = {
    "align": "center",
    "valign": "vcenter",
    "font_size": 26,
    "border": 1,
    "font_color": "blue",
    "bold": True,
}

style_title = {
    "border": 1,
}
style_value = {"border": 0}
style_label = {"border": 0}
style_headers = {"border": 1}

# Zone d’affichage du logo (organisation ou APP_LOGO) dans l’export Excel, en pixels (~96 dpi).
ORG_LOGO_XLSX_WIDTH_PX = 200
ORG_LOGO_XLSX_HEIGHT_PX = 72


def _org_logo_xlsx_image_options(image_path: str) -> dict:
    """Échelle xlsxwriter pour afficher le logo dans une zone de taille fixe (ratio conservé)."""
    opts = {"x_offset": 2, "y_offset": 2}
    tw, th = ORG_LOGO_XLSX_WIDTH_PX, ORG_LOGO_XLSX_HEIGHT_PX
    try:
        from PIL import Image

        with Image.open(image_path) as im:
            im.load()
            nw, nh = im.size
    except Exception:
        return {**opts, "x_scale": 1.0, "y_scale": 1.0}
    if nw < 1 or nh < 1:
        return {**opts, "x_scale": 1.0, "y_scale": 1.0}
    scale = min(tw / float(nw), th / float(nh))
    return {**opts, "x_scale": scale, "y_scale": scale}


def _write_xlsx_to_path(dict_data: dict, output_path: str) -> None:
    """
    Écrit le classeur à ``output_path`` (fichier ou chemin pour xlsxwriter).
    Même logique qu’historiquement, sans dialogue ni ouverture.
    """
    organization = Organization.get(id=1)

    headers = dict_data.get("headers") or []
    sheet_name = str(dict_data.get("sheet") or "Feuil1")
    data = dict_data.get("data") or []
    widths = dict_data.get("widths")
    date_ = str(dict_data.get("date"))
    extend_rows = dict_data.get("extend_rows")
    others = dict_data.get("others")
    footers = dict_data.get("footers")
    format_money = dict_data.get("format_money")

    dict_alph = {
        1: "A",
        2: "C",
        3: "D",
        4: "E",
        5: "F",
        6: "G",
        7: "H",
        8: "I",
    }

    if date_ == "None":
        date_ = datetime.now()

    logo_tmp: str | None = None
    try:
        logo_tmp = write_org_logo_temp_file(getattr(organization, "logo_orga", None))
        image_path: str | None = logo_tmp
        if not image_path and CConstants.APP_LOGO:
            app_logo_p = Path(str(CConstants.APP_LOGO))
            if app_logo_p.is_file():
                image_path = str(app_logo_p)

        workbook = xlsxwriter.Workbook(output_path, {"default_date_format": "dd/mm/yy"})
        try:
            worksheet = workbook.add_worksheet(sheet_name)

            date_format = workbook.add_format({"num_format": "d-mmm-yy"})
            format1 = workbook.add_format()
            format1.set_num_format("0.000")
            money = workbook.add_format({"num_format": "#,## "})
            style_def = workbook.add_format({})
            rowx = 1
            end_colx = len(headers) - 1
            if image_path:
                worksheet.insert_image(
                    0,
                    0,
                    image_path,
                    _org_logo_xlsx_image_options(image_path),
                )
                rowx += 6
            else:
                worksheet.merge_range(
                    "A{}:E{}".format(rowx, rowx),
                    organization.name_orga,
                    workbook.add_format(style_org),
                )
                rowx += 1
                worksheet.merge_range(
                    "A{}:E{}".format(rowx, rowx),
                    "Adresse : {}".format(organization.adress_org),
                    style_def,
                )
                rowx += 1
                worksheet.merge_range(
                    "A{}:B{}".format(rowx, rowx),
                    "BP : {}".format(organization.bp),
                    style_def,
                )
                worksheet.merge_range(
                    "{}{}:{}{}".format(
                        dict_alph.get(end_colx - 1), rowx, dict_alph.get(end_colx), rowx
                    ),
                    "E-mail : {}".format(organization.email_org),
                    style_def,
                )
                rowx += 1
                worksheet.merge_range(
                    "A{}:{}{}".format(rowx, dict_alph.get(end_colx - 1), rowx),
                    "Tel : {}".format(organization.phone),
                    style_def,
                )
                rowx += 2
            if widths:
                for col in widths:
                    w = 120 / len(headers) if headers else 15
                    worksheet.set_column(col, col, w)
            columns = [({"header": item}) for item in headers]
            end_row_table = len(data) + rowx + 3
            if format_money:
                for col_str in format_money:
                    worksheet.set_column(col_str, 18, money)
            rowx += 1
            worksheet.merge_range(
                "D{}:{}{}".format(rowx, dict_alph.get(end_colx), rowx),
                date_,
                date_format,
            )
            rowx += 2
            worksheet.add_table(
                "A{}:{}{}".format(rowx, dict_alph.get(end_colx), end_row_table),
                {"autofilter": 0, "data": data, "columns": columns},
            )
            rowx = end_row_table
            if extend_rows:
                for elt in extend_rows:
                    col, val = elt
                    worksheet.write(rowx, col, val, money)
                rowx += 1
            if footers:
                rowx += 1
                for s_col, e_col, val in footers:
                    worksheet.merge_range(
                        "{}{}:{}{}".format(s_col, rowx, e_col, rowx),
                        val,
                        workbook.add_format(style_label),
                    )
                    rowx += 1
                rowx += 1
            if others:
                rowx += 1
                for _pos, _pos2, val in others:
                    if val is None or str(val).strip() == "":
                        continue
                    worksheet.merge_range(
                        rowx,
                        0,
                        rowx,
                        end_colx,
                        str(val),
                        workbook.add_format(style_label),
                    )
                    rowx += 1
        finally:
            workbook.close()
    finally:
        if logo_tmp:
            try:
                os.unlink(logo_tmp)
            except OSError:
                pass


def _show_xlsx_export_dialog(temp_path: str, file_base: str) -> str | None:
    """
    Proposition d’ouverture du fichier temporaire puis « Enregistrer sous… ».
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
    dlg.setWindowTitle("Export — Excel")
    dlg.resize(520, 200)
    dlg.setWindowModality(Qt.WindowModality.ApplicationModal)

    layout = QVBoxLayout(dlg)
    layout.addWidget(
        QLabel(
            "Le classeur Excel a été généré.\n\n"
            "• « Ouvrir dans le tableur… » ouvre le fichier temporaire pour vérification.\n"
            "• « Enregistrer sous… » copie le fichier à l’emplacement de votre choix "
            "(recommandé pour conserver une copie)."
        )
    )

    btn_open = QPushButton("Ouvrir dans le tableur…")
    btn_open.clicked.connect(lambda: openFile(temp_path))
    layout.addWidget(btn_open)

    btn_row = QHBoxLayout()
    btn_save = QPushButton("💾 Enregistrer sous…")
    btn_cancel = QPushButton("Annuler")
    btn_row.addStretch()
    btn_row.addWidget(btn_save)
    btn_row.addWidget(btn_cancel)
    layout.addLayout(btn_row)

    chosen: list[str | None] = [None]
    stem = Path(str(file_base)).name
    if not stem.lower().endswith(".xlsx"):
        stem = f"{stem}.xlsx"

    def _save():
        docs = Path.home() / "Documents"
        if not docs.is_dir():
            docs = Path.home()
        default = str(docs / stem)
        path, _ = QFileDialog.getSaveFileName(
            dlg,
            "Enregistrer le classeur Excel",
            default,
            "Classeur Excel (*.xlsx)",
        )
        if path:
            if not path.lower().endswith(".xlsx"):
                path = f"{path}.xlsx"
            chosen[0] = path
            dlg.accept()

    btn_save.clicked.connect(_save)
    btn_cancel.clicked.connect(dlg.reject)

    dlg.exec()
    return chosen[0]


def export_dynamic_data(dict_data):
    """
    Génère le XLSX dans un fichier temporaire, affiche le dialogue (comme le PDF),
    enregistre au chemin choisi puis ouvre le fichier final.
    """
    file_base = dict_data.get("file_name") or "export"

    fd, tmp_path = tempfile.mkstemp(suffix=".xlsx", prefix="mexport_")
    try:
        os.close(fd)
        try:
            _write_xlsx_to_path(dict_data, tmp_path)
        except Exception as e:
            logger.exception("Erreur génération Excel: %s", e)
            try:
                from PyQt6.QtWidgets import QApplication, QMessageBox

                if QApplication.instance() is not None:
                    QMessageBox.critical(
                        None,
                        "Export Excel",
                        "La génération du classeur Excel a échoué.\n\n"
                        f"Détail : {e!s}",
                    )
            except Exception:
                pass
            return

        dest = _show_xlsx_export_dialog(tmp_path, str(file_base))
        if not dest:
            logger.info("Export Excel : enregistrement annulé après le dialogue")
            return

        shutil.copy2(tmp_path, dest)
        logger.info("Excel enregistré : %s", dest)
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
            logger.debug("QDesktopServices.openUrl Excel: %s", e)
        if not opened and openFile(abs_dest) != 0:
            logger.warning(
                "Impossible d’ouvrir le classeur automatiquement : %s", abs_dest
            )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def xexport_dynamic_data(dict_data):
    from openpyxl import Workbook
    from openpyxl.worksheet.table import Table, TableStyleInfo

    wb = Workbook()
    ws = wb.active

    organization = Organization.get(id=1)

    file_name = "{}.xlsx".format(dict_data.get("file_name"))
    headers = dict_data.get("headers")
    sheet_name = str(dict_data.get("sheet"))
    title = str(dict_data.get("title"))
    data = dict_data.get("data")
    widths = dict_data.get("widths")
    date_ = str(dict_data.get("date"))
    extend_rows = dict_data.get("extend_rows")
    others = dict_data.get("others")
    footers = dict_data.get("footers")
    exclude_row = dict_data.get("exclude_row")
    format_money = dict_data.get("format_money")

    # add column headings. NB. these must be strings
    ws.append(headers)
    for row in data:
        print(row)
        ws.append(row)

    dict_alph = {
        1: "A",
        2: "C",
        3: "D",
        4: "E",
        5: "F",
        6: "G",
        7: "H",
        8: "I",
    }
    REF = "A1:{}{}".format(dict_alph.get(len(headers)), len(data) + 1)
    print(REF)
    tab = Table(displayName="Table1", ref=REF)

    # Add a default style with striped rows and banded columns
    style = TableStyleInfo(
        name="TableStyleMedium9",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=True,
    )
    tab.tableStyleInfo = style
    ws.add_table(tab)
    wb.save(file_name)

    try:
        wb.close()
        openFile(file_name)
    except Exception as e:
        print(e)
