#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import absolute_import, division, print_function, unicode_literals

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
)

from ..models import Owner
from .common import (
    EnterTabbedLineEdit,
    ErrorLabel,
    FDialog,
    FMainWindow,
    FormLabel,
    FWidget,
    LineEdit,
)
from .util import check_is_empty, field_error

try:
    from ..cstatic import CConstants
except Exception as exc:
    print(exc)


class LoginWidget(FDialog, FWidget):
    title_page = "Identification"

    def __init__(self, parent=None, hibernate=False, *args, **kwargs):
        QDialog.__init__(self, parent=parent, *args, **kwargs)
        self.hibernate = hibernate

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.title = FormLabel(
            "<h4>{app_name}</h4><stromg>Ver: {version}</stromg>".format(
                app_name=CConstants.APP_NAME, version=CConstants.APP_VERSION
            )
        )
        self.title.setStyleSheet(
            """ background: url({}) #DAF7A6;
                border-radius: 14px 14px 8px 8px; border: 10px double #128a76 ;
                width: 100%; height: auto; padding: 1em;
                font: 8pt 'URW Bookman L';""".format(
                CConstants.APP_LOGO
            )
        )
        vbox = QHBoxLayout()

        self.loginUserGroupBox()
        vbox.addWidget(self.title)
        vbox.addWidget(self.topLeftGroupBox)
        # set focus to username field
        self.setFocusProxy(self.password_field)
        self.setLayout(vbox)

    def loginUserGroupBox(self):
        self.topLeftGroupBox = QGroupBox(self.tr("Identification"))
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
        self.login_button = QPushButton("&S'identifier")
        self.login_button.setIcon(
            QIcon.fromTheme("save", QIcon("{}login.png".format(CConstants.img_cmedia)))
        )
        self.login_button.clicked.connect(self.login)

        self.cancel_button = QPushButton("&Quiter")
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setFlat(True)

        # login error
        self.login_error = ErrorLabel("")

        formbox = QFormLayout()

        # grid layout
        formbox.addRow(FormLabel("Identifiant"), self.username_field)
        formbox.addRow(FormLabel("Mot de passe"), self.password_field)
        formbox.addRow(FormLabel(""), self.login_button)
        formbox.addRow(FormLabel(""), self.cancel_button)
        if self.hibernate:
            self.cancel_button.setEnabled(False)

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
        for ow in Owner.select().where(Owner.islog == True):
            ow.islog = False
            ow.save()
        try:
            owner = Owner.get(Owner.username == username, Owner.password == password)
            owner.islog = True
            owner.save()
        except Exception as e:
            print(e)
            field_error(self.password_field, "Mot de passe incorrect")
            return False
        self.accept()
