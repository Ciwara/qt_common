#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from __future__ import absolute_import, division, print_function, unicode_literals

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..models import Organization
from .common import Button, FWidget, FormLabel


class PreferencesDialog(QDialog, FWidget):
    """Fenêtre Préférences (qt_common).

    Objectif:
    - regrouper la gestion de l'organisation dans les préférences
    - éviter de laisser cette gestion dans l'écran Administration
    """

    def __init__(self, parent=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)
        FWidget.__init__(self, parent, *args, **kwargs)

        self.setWindowTitle("⚙️ Préférences")
        self.setMinimumWidth(700)

        root = QVBoxLayout(self)
        root.setSpacing(12)

        self.tabs = QTabWidget(self)
        root.addWidget(self.tabs, 1)

        self.tabs.addTab(self._build_organisation_tab(), "🏢 Organisation")
        self.tabs.addTab(self._build_display_tab(), "🖥️ Affichage")

        # Boutons
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close_btn = Button("Fermer")
        close_btn.clicked.connect(self.accept)
        buttons.addWidget(close_btn)
        root.addLayout(buttons)

    def _build_display_tab(self) -> QWidget:
        from PyQt6.QtWidgets import QApplication
        from ..models import Settings
        from .theme import apply_font_scale

        w = QWidget(self)
        lay = QVBoxLayout(w)
        lay.setSpacing(12)

        info = QLabel(
            "Ajustez la taille de police globale (utile pour l'accessibilité). "
            "Le changement est appliqué immédiatement."
        )
        info.setWordWrap(True)
        lay.addWidget(info)

        form_wrap = QWidget(self)
        form = QFormLayout(form_wrap)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.font_scale_combo = QComboBox(self)
        choices = [
            (0.9, "90% (petit)"),
            (1.0, "100% (défaut)"),
            (1.1, "110%"),
            (1.2, "120%"),
            (1.3, "130%"),
            (1.4, "140% (grand)"),
        ]
        for value, label in choices:
            self.font_scale_combo.addItem(label, value)

        try:
            st = Settings.init_settings()
            current = float(getattr(st, "font_scale", 1.0) or 1.0)
        except Exception:
            current = 1.0

        # Positionner l'item le plus proche
        best_idx = 1
        best_dist = 999.0
        for i in range(self.font_scale_combo.count()):
            v = float(self.font_scale_combo.itemData(i))
            d = abs(v - current)
            if d < best_dist:
                best_dist = d
                best_idx = i
        self.font_scale_combo.setCurrentIndex(best_idx)

        def _on_scale_changed():
            app = QApplication.instance()
            if not app:
                return
            try:
                scale = float(self.font_scale_combo.currentData())
            except Exception:
                scale = 1.0
            apply_font_scale(app, scale, save_to_settings=True)

        self.font_scale_combo.currentIndexChanged.connect(lambda *_: _on_scale_changed())

        row = QWidget(self)
        row_lay = QHBoxLayout(row)
        row_lay.setContentsMargins(0, 0, 0, 0)
        row_lay.addWidget(self.font_scale_combo, 1)

        reset_btn = QPushButton("Réinitialiser", self)
        reset_btn.clicked.connect(lambda *_: self._set_font_scale_to_default())
        row_lay.addWidget(reset_btn)

        form.addRow(FormLabel("Taille de police :"), row)
        lay.addWidget(form_wrap)

        lay.addStretch(1)
        return w

    def _set_font_scale_to_default(self):
        from PyQt6.QtWidgets import QApplication
        from .theme import apply_font_scale

        app = QApplication.instance()
        if app:
            apply_font_scale(app, 1.0, save_to_settings=True)
        # Mettre à jour la combo (si présente)
        try:
            if hasattr(self, "font_scale_combo") and self.font_scale_combo:
                for i in range(self.font_scale_combo.count()):
                    if float(self.font_scale_combo.itemData(i)) == 1.0:
                        self.font_scale_combo.setCurrentIndex(i)
                        break
        except Exception:
            pass

    def _build_organisation_tab(self) -> QWidget:
        w = QWidget(self)
        lay = QVBoxLayout(w)
        lay.setSpacing(12)

        info = QLabel(
            "Configurez les informations de votre organisation (logo, nom, contact, adresse)."
        )
        info.setWordWrap(True)
        lay.addWidget(info)

        self.org_summary = QWidget(self)
        form = QFormLayout(self.org_summary)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.lbl_name = QLabel("")
        self.lbl_phone = QLabel("")
        self.lbl_email = QLabel("")
        self.lbl_bp = QLabel("")
        self.lbl_address = QLabel("")
        self.lbl_address.setWordWrap(True)

        form.addRow(FormLabel("Nom :"), self.lbl_name)
        form.addRow(FormLabel("Téléphone :"), self.lbl_phone)
        form.addRow(FormLabel("E-mail :"), self.lbl_email)
        form.addRow(FormLabel("B.P :"), self.lbl_bp)
        form.addRow(FormLabel("Adresse :"), self.lbl_address)

        lay.addWidget(self.org_summary)

        actions = QHBoxLayout()
        actions.addStretch(1)

        edit_btn = Button("Modifier…")
        edit_btn.clicked.connect(self._edit_organisation)
        actions.addWidget(edit_btn)

        refresh_btn = Button("Rafraîchir")
        refresh_btn.clicked.connect(self._refresh_organisation_summary)
        actions.addWidget(refresh_btn)

        lay.addLayout(actions)
        lay.addStretch(1)

        self._refresh_organisation_summary()
        return w

    def _refresh_organisation_summary(self):
        try:
            org = Organization.get(id=1)
        except Exception:
            org = None

        self.lbl_name.setText(getattr(org, "name_orga", "") or "—")
        self.lbl_phone.setText(str(getattr(org, "phone", "") or "—"))
        self.lbl_email.setText(getattr(org, "email_org", "") or "—")
        self.lbl_bp.setText(getattr(org, "bp", "") or "—")
        addr = getattr(org, "adress_org", "") or ""
        self.lbl_address.setText(addr if addr.strip() else "—")

    def _edit_organisation(self):
        # Utiliser le dialogue commun existant
        from .organization_add_or_edit import NewOrEditOrganizationViewWidget

        dlg = NewOrEditOrganizationViewWidget(parent=self)
        dlg.exec()
        self._refresh_organisation_summary()

