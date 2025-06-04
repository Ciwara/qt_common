#!usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad

import os
import shutil
from datetime import datetime

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
)

from ..models import DB_FILE, Owner
from .common import (
    DeletedBtt,
    EnterTabbedLineEdit,
    ErrorLabel,
    FormLabel,
    FPageTitle,
    FWidget,
    LineEdit,
)
from .util import check_is_empty, field_error

try:
    from ..cstatic import CConstants
except Exception as exc:
    print(exc)

DATETIME = "{}".format(datetime.now().strftime("%d-%m-%Y-%Hh%M"))


class DBCleanerWidget(QDialog, FWidget):
    def __init__(self, parent=0, *args, **kwargs):
        QDialog.__init__(self, parent=parent, *args, **kwargs)
        self.parent = parent

        self.setWindowTitle("Confirmation de le suppression")
        vbox = QVBoxLayout()

        self.loginUserGroupBox()
        vbox.addWidget(
            FPageTitle("<h1 style='color: red;'>Suppression des enregistrements<h1>")
        )
        vbox.addWidget(self.topLeftGroupBox)
        self.setLayout(vbox)

    def loginUserGroupBox(self):
        self.topLeftGroupBox = QGroupBox(
            self.tr("Suppression de tout les enregistrements")
        )

        self.liste_username = Owner.select().where(Owner.isactive == True)
        # Combobox widget
        self.box_username = QComboBox()
        for index in self.liste_username:
            self.box_username.addItem("%(username)s" % {"username": index})

        # username field
        self.username_field = self.box_username
        # password field
        self.password_field = EnterTabbedLineEdit()
        self.password_field.setEchoMode(LineEdit.Password)
        self.password_field.setFocus()
        # login button
        self.login_button = DeletedBtt("&Supprimer")
        self.login_button.setIcon(
            QIcon.fromTheme(
                "delete", QIcon("{}login.png".format(CConstants.img_cmedia))
            )
        )
        self.login_button.clicked.connect(self.login)

        self.cancel_button = QPushButton("&Annuler")
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setFlat(True)

        # login error
        self.login_error = ErrorLabel("")

        formbox = QFormLayout()

        # grid layout
        formbox.addRow(FormLabel("Identifiant"), self.username_field)
        formbox.addRow(FormLabel("Mot de passe"), self.password_field)
        formbox.addRow(self.cancel_button, self.login_button)

        self.topLeftGroupBox.setLayout(formbox)

    def is_valide(self):
        if check_is_empty(self.password_field):
            return False
        return True

    def cancel(self):
        self.close()

    def login(self):
        """ """
        if not self.is_valide():
            print("is not valide")
            return

        username = str(self.liste_username[self.box_username.currentIndex()])
        password = Owner().crypt_password(str(self.password_field.text()).strip())
        # check completeness

        try:
            Owner.get(Owner.username == username, Owner.password == password)
            self.cleaner_db()
        except Exception as e:
            print(e)
            field_error(self.password_field, "Mot de passe incorrect")
            return False

    def cleaner_db(self):
        path_db_file = os.path.join(
            os.path.dirname(os.path.abspath("__file__")), DB_FILE
        )
        shutil.copy(path_db_file, "{}__{}.old".format(DB_FILE, DATETIME))

        for mod in CConstants.list_models:
            print(mod)
            for m in mod:
                print(m)
                m.delete_instance()

        self.parent.update()
        self.cancel()
        self.parent.Notify("Les données ont été bien supprimé", "error")
