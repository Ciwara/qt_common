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

        # Boutons
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close_btn = Button("Fermer")
        close_btn.clicked.connect(self.accept)
        buttons.addWidget(close_btn)
        root.addLayout(buttons)

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

