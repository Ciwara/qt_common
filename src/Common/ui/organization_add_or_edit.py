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
)

from ..models import Organization
from .common import ButtonSave, FormLabel, FWidget, IntLineEdit, LineEdit
from .util import check_is_empty


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

        # self.liste_devise = Organization.DEVISE
        # Combobox widget
        # self.box_devise = QComboBox()
        # for index in self.liste_devise:
        #     self.box_devise.addItem("{} {}".format(self.liste_devise[index], index))

        self.checked = QCheckBox("Active")
        self.checked.setChecked(True)
        self.checked.setToolTip(
            """Cocher si vous voulez pour deactive
                                le login continue à utiliser le systeme"""
        )
        self.logo_orga = LineEdit()
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
        # formbox.addRow(FormLabel(u"Devise"), self.box_devise)
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
        # device = str(self.box_devise.currentText().split()[1])
        bp = str(self.bp.text())
        email_org = str(self.email_org.text())
        phone = str(self.phone.text())
        adress_org = str(self.adress_org.toPlainText())

        org = Organization()
        org.phone = phone
        # org.device = device
        org.name_orga = name_orga
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
