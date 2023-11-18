#!usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad
from __future__ import absolute_import, division, print_function, unicode_literals

from peewee import IntegrityError
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QVBoxLayout,
)

from ..exports import import_backup
from ..models import Owner
from .common import Button, EnterTabbedLineEdit, FLabel, FormLabel, FWidget, LineEdit
from .util import check_is_empty, field_error, is_valide_codition_field

try:
    from ..cstatic import CConstants
except Exception as e:
    print(e)

try:
    unicode
except:
    unicode = str


class RestorationViewWidget(QDialog, FWidget):
    def __init__(self, pp=None, owner=None, parent=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.setWindowTitle("Restoration de Données")
        vbox = QVBoxLayout()
        # self.online_resto_box()
        self.label = FLabel()
        self.label.setStyleSheet(
            "background: url('{}center.png') no-repeat scroll 0 0;"
            "height: 50px;width:50px; margin: 0; padding: 0;".format(
                CConstants.img_media
            )
        )

        # ==== Box of restor online ====
        self.onlineRestorBoxBtt = QGroupBox(self.tr("Restoration de données en line"))
        self.bn_resto_onligne = Button("Connexion")
        self.bn_resto_onligne.setIcon(
            QIcon.fromTheme("", QIcon("{}cloud.png".format(CConstants.img_cmedia)))
        )
        self.bn_resto_onligne.clicked.connect(self.resto_onligne)

        self.bn_resto_l = Button("Import de sauvegarde locale")
        self.bn_resto_l.setIcon(
            QIcon.fromTheme("", QIcon("{}db.png".format(CConstants.img_cmedia)))
        )
        self.bn_resto_l.clicked.connect(self.resto_local_db)

        self.bn_ignore = Button("Première installation")
        self.bn_ignore.setIcon(
            QIcon.fromTheme("", QIcon("{}go-next.png".format(CConstants.img_cmedia)))
        )
        self.bn_ignore.clicked.connect(self.ignore_resto)

        self.mail_field = LineEdit()
        self.password_field = EnterTabbedLineEdit()
        self.password_field.setEchoMode(LineEdit.Password)
        self.password_field.setFocus()

        formbox = QFormLayout()

        # formbox.addRow(FormLabel("<i>les données sauvegardé en ligne</i>"))
        formbox.addRow(FormLabel("E-mail"), self.mail_field)
        formbox.addRow(FormLabel("Mot de passe"), self.password_field)
        formbox.addRow(FormLabel(""), self.bn_resto_onligne)
        self.onlineRestorBoxBtt.setLayout(formbox)
        vbox.addWidget(self.onlineRestorBoxBtt)

        # ==== Box of restor online ====
        self.onLocaleRestorBoxBtt = QGroupBox(
            self.tr("Restoration de données en locale.")
        )

        l_formbox = QFormLayout()
        # l_formbox.addRow(FormLabel("<i>Une copie de la base de données exportée.</i>"))
        l_formbox.addRow(FormLabel(""), self.bn_resto_l)
        self.onLocaleRestorBoxBtt.setLayout(l_formbox)
        vbox.addWidget(self.onLocaleRestorBoxBtt)

        i_formbox = QFormLayout()
        i_formbox.addRow(FLabel("<h2></h2>"), self.bn_ignore)
        vbox.addLayout(i_formbox)
        self.setLayout(vbox)

    def resto_onligne(self):
        # self.open_dialog()
        self.vbox.removeWidget(self.topLeftGroupBoxBtt)
        # return

    def ignore_resto(self):
        print("ignore_resto")
        self.accept()

    def resto_local_db(self):
        import_backup(folder="C://", dst_folder=CConstants.ARMOIRE)
        self.accept()
