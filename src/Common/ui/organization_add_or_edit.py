#!usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QWidget,
)

from ..models import Organization
from .common import ButtonSave, FormLabel, FWidget, IntLineEdit, LineEdit
from .util import check_is_empty


class LogoSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.path_edit = LineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("Aucun fichier sélectionné")
        
        self.browse_button = QPushButton("Parcourir...")
        self.browse_button.clicked.connect(self.browse_file)
        
        layout.addWidget(self.path_edit)
        layout.addWidget(self.browse_button)
        
        self.setLayout(layout)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le logo de l'organisation",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg);;Tous les fichiers (*)"
        )
        
        if file_path:
            self.path_edit.setText(file_path)
    
    def text(self):
        return self.path_edit.text()
    
    def setText(self, text):
        self.path_edit.setText(text)


class NewOrEditOrganizationViewWidget(QDialog, FWidget):
    def __init__(self, pp=None, owner=None, parent=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.setWindowTitle("Nouvel Organisation")
        self.parent = parent
        self.pp = pp
        self.owner = owner

        vbox = QVBoxLayout()

        self.organization_group_box()
        vbox.addWidget(self.organGroupBoxBtt)
        self.setLayout(vbox)

    def organization_group_box(self):
        self.organGroupBoxBtt = QGroupBox(self.tr("Nouvelle Organisation"))

        self.checked = QCheckBox("Active")
        self.checked.setChecked(True)
        self.checked.setToolTip(
            """Cocher si vous voulez pour deactive
                                le login continue à utiliser le systeme"""
        )
        self.logo_orga = LogoSelector()
        self.name_orga = LineEdit()
        self.phone = IntLineEdit()
        self.bp = LineEdit()
        self.adress_org = QTextEdit()
        self.email_org = LineEdit()

        formbox = QFormLayout()
        formbox.addRow(FormLabel("logo de l'organisation *"), self.logo_orga)
        formbox.addRow(FormLabel("Nom de l'organisation *"), self.name_orga)
        formbox.addRow(FormLabel("Tel *"), self.phone)
        formbox.addRow(FormLabel("Activer la saisie de mot de passe"), self.checked)
        formbox.addRow(FormLabel("B.P"), self.bp)
        formbox.addRow(FormLabel("E-mail:"), self.email_org)
        formbox.addRow(FormLabel("Adresse complete:"), self.adress_org)

        butt = ButtonSave("Enregistrer")
        butt.clicked.connect(self.save_edit)
        formbox.addRow("", butt)

        self.organGroupBoxBtt.setLayout(formbox)

    def save_edit(self):
        """add operation"""
        if check_is_empty(self.name_orga):
            return
        if check_is_empty(self.phone):
            return
        name_orga = str(self.name_orga.text())
        logo_path = str(self.logo_orga.text())
        bp = str(self.bp.text())
        email_org = str(self.email_org.text())
        phone = str(self.phone.text())
        adress_org = str(self.adress_org.toPlainText())

        org = Organization()
        org.phone = phone
        org.name_orga = name_orga
        org.logo_orga = logo_path
        org.email_org = email_org
        org.bp = bp
        org.after_cam = 0
        org.adress_org = adress_org
        org.is_login = True if self.checked.checkState() == Qt.Checked else False
        try:
            org.save()
            self.accept()
        except Exception as e:
            print(f"name_orga {e}")
