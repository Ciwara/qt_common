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
        vbox = QHBoxLayout()

        self.loginUserGroupBox()
        vbox.addWidget(self.title)
        vbox.addWidget(self.topLeftGroupBox)
        
        # Définir le focus APRÈS la création des champs
        if hasattr(self, 'password_field') and self.password_field:
            self.setFocusProxy(self.password_field)
        self.setLayout(vbox)

    def loginUserGroupBox(self):
        self.topLeftGroupBox = QGroupBox(self.tr("Identification"))
        self.liste_username = Owner.get_active_non_superusers()

        # Vérifier s'il y a des utilisateurs actifs
        if not self.liste_username.exists():
            print("Erreur: Aucun utilisateur actif trouvé")
            return

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
        formbox.addRow(FormLabel(""), self.login_error)  # Ajouter le champ d'erreur au formulaire
        if self.hibernate:
            self.cancel_button.setEnabled(False)

        self.topLeftGroupBox.setLayout(formbox)

    def is_valide(self):
        return not check_is_empty(self.password_field)

    def cancel(self):
        self.close()

    def login(self):
        """Handle login logic"""
        # Réinitialiser le message d'erreur
        self.login_error.setText("")
        
        if not self.is_valide():
            self.login_error.setText("Veuillez saisir votre mot de passe")
            return

        # Vérifier que la liste n'est pas vide et que l'index est valide
        current_index = self.box_username.currentIndex()
        if current_index < 0 or current_index >= len(self.liste_username):
            self.login_error.setText("Erreur: Utilisateur sélectionné invalide")
            return

        # Convertir la requête en liste pour accéder par index de manière sécurisée
        users_list = list(self.liste_username)
        if current_index >= len(users_list):
            self.login_error.setText("Erreur: Index utilisateur invalide")
            return

        username = str(users_list[current_index].username)
        password = Owner().crypt_password(self.password_field.text().strip())

        # Déconnecter tous les utilisateurs actuellement connectés
        for ow in Owner.select().where(Owner.islog):
            ow.islog = False
            ow.save()

        try:
            owner = Owner.get(Owner.username == username, Owner.password == password)
            owner.islog = True
            owner.save()
            self.accept()
        except Owner.DoesNotExist:
            self.login_error.setText("Mot de passe incorrect")
            field_error(self.password_field, "Mot de passe incorrect")
            return False
        except Exception as e:
            print(f"Login error: {e}")
            self.login_error.setText("Erreur de connexion")
            return False
