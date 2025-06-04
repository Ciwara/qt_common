#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QPushButton

from ..models import Owner
from .common import (
    EnterTabbedLineEdit,
    ErrorLabel,
    FDialog,
    FormLabel,
    FWidget,
    LineEdit,
)
from .util import check_is_empty, field_error

try:
    from ..cstatic import CConstants
except Exception as exc:
    print(f"Erreur lors de l'importation de CConstants: {exc}")


class LoginWidget(FDialog, FWidget):
    title_page = "Identification"

    def __init__(self, parent=None, hibernate=False, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.hibernate = hibernate

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.title = FormLabel(
            f"<h4>{CConstants.APP_NAME}</h4><strong>Ver: {CConstants.APP_VERSION}</strong>"
        )
        self.title.setStyleSheet(
            f"""background: url({CConstants.APP_LOGO}) #DAF7A6;
                border-radius: 14px 14px 8px 8px; border: 10px double #128a76;
                width: 100%; height: auto; padding: 1em;
                font: 8pt 'Arial';"""
        )
        vbox = QHBoxLayout()

        self.loginUserGroupBox()
        vbox.addWidget(self.title)
        vbox.addWidget(self.topLeftGroupBox)
        # Set focus to username field
        self.setFocusProxy(self.password_field)
        self.setLayout(vbox)

    def loginUserGroupBox(self):
        self.topLeftGroupBox = QGroupBox(self.tr("Identification"))
        self.liste_username = Owner.select().where(Owner.isactive == True)

        # Combobox widget
        self.box_username = QComboBox()
        for index in self.liste_username:
            self.box_username.addItem(f"{index.username}")

        # Username field
        self.username_field = self.box_username
        # Password field
        self.password_field = EnterTabbedLineEdit()
        self.password_field.setEchoMode(LineEdit.Password)
        self.password_field.setFocus()
        # Login button
        self.login_button = QPushButton("&S'identifier")
        self.login_button.setIcon(
            QIcon.fromTheme("save", QIcon(f"{CConstants.img_cmedia}login.png"))
        )
        self.login_button.clicked.connect(self.login)

        self.cancel_button = QPushButton("&Quitter")
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setFlat(True)

        # Login error
        self.login_error = ErrorLabel("")

        formbox = QFormLayout()
        formbox.addRow(FormLabel("Identifiant"), self.username_field)
        formbox.addRow(FormLabel("Mot de passe"), self.password_field)
        formbox.addRow(FormLabel(""), self.login_button)
        formbox.addRow(FormLabel(""), self.cancel_button)
        if self.hibernate:
            self.cancel_button.setEnabled(False)

        self.topLeftGroupBox.setLayout(formbox)

    def is_valide(self):
        return not check_is_empty(self.password_field)

    def cancel(self):
        self.close()

    def login(self):
        """Handle login logic"""
        if not self.is_valide():
            print("Login details are not valid.")
            return

        username = str(self.liste_username[self.box_username.currentIndex()].username)
        password = Owner().crypt_password(self.password_field.text().strip())

        # Check completeness
        for ow in Owner.select().where(Owner.islog == True):
            ow.islog = False
            ow.save()

        try:
            owner = Owner.get(Owner.username == username, Owner.password == password)
            owner.islog = True
            owner.save()
        except Exception as e:
            print(f"Login error: {e}")
            field_error(self.password_field, "Mot de passe incorrect")
            return False

        self.accept()
