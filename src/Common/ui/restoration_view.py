#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QFormLayout, QGroupBox, QVBoxLayout

from ..exports import import_backup
from .common import Button, EnterTabbedLineEdit, FLabel, FormLabel, FWidget, LineEdit

try:
    from ..cstatic import CConstants
except Exception as e:
    print("Erreur lors de l'importation de CConstants:", e)


class RestorationViewWidget(QDialog, FWidget):
    def __init__(self, pp=None, owner=None, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setWindowTitle("Restoration de Données")
        self.vbox = QVBoxLayout()

        # Configure the label with an image
        self.label = FLabel()
        self.label.setStyleSheet(
            f"background: url('{CConstants.img_media}center.png') no-repeat scroll 0 0;"
            "height: 50px; width: 50px; margin: 0; padding: 0;"
        )

        # ==== Online Restoration Box ====
        self.onlineRestorBoxBtt = QGroupBox(self.tr("Restoration de données en ligne"))
        self.bn_resto_onligne = Button("Connexion")
        self.bn_resto_onligne.setIcon(
            QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}cloud.png"))
        )
        self.bn_resto_onligne.clicked.connect(self.resto_onligne)

        self.bn_resto_l = Button("Import de sauvegarde locale")
        self.bn_resto_l.setIcon(
            QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}db.png"))
        )
        self.bn_resto_l.clicked.connect(self.resto_local_db)

        self.bn_ignore = Button("Première installation")
        self.bn_ignore.setIcon(
            QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}go-next.png"))
        )
        self.bn_ignore.clicked.connect(self.ignore_resto)

        self.mail_field = LineEdit()
        self.password_field = EnterTabbedLineEdit()
        self.password_field.setEchoMode(LineEdit.Password)
        self.password_field.setFocus()

        formbox = QFormLayout()
        formbox.addRow(FormLabel("E-mail"), self.mail_field)
        formbox.addRow(FormLabel("Mot de passe"), self.password_field)
        formbox.addRow(FormLabel(""), self.bn_resto_onligne)
        self.onlineRestorBoxBtt.setLayout(formbox)
        self.vbox.addWidget(self.onlineRestorBoxBtt)

        # ==== Local Restoration Box ====
        self.onLocaleRestorBoxBtt = QGroupBox(
            self.tr("Restoration de données en locale.")
        )
        l_formbox = QFormLayout()
        l_formbox.addRow(FormLabel(""), self.bn_resto_l)
        self.onLocaleRestorBoxBtt.setLayout(l_formbox)
        self.vbox.addWidget(self.onLocaleRestorBoxBtt)

        i_formbox = QFormLayout()
        i_formbox.addRow(FLabel("<h2></h2>"), self.bn_ignore)
        self.vbox.addLayout(i_formbox)

        self.setLayout(self.vbox)

    def resto_onligne(self):
        # Placeholder method for online restoration
        print("Online restoration not implemented.")

    def ignore_resto(self):
        print("ignore_resto")
        self.accept()

    def resto_local_db(self):
        import_backup(folder="C://", dst_folder=CConstants.ARMOIRE)
        self.accept()
