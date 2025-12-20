#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QPushButton

from ..models import Owner
from .common import (
    EnterTabbedLineEdit,
    ErrorLabel,
    FDialog,
    FormLabel,
    FWidget,
    LineEdit,
    Button,
)
from .util import check_is_empty, field_error

try:
    from ..cstatic import CConstants
except Exception as exc:
    print(f"⚠️ Erreur lors de l'importation de CConstants: {exc}")

import datetime


class LoginWidget(FDialog, FWidget):
    title_page = "🔐 Connexion Sécurisée"
    login_successful = pyqtSignal()  # Signal émis lors d'une connexion réussie

    def __init__(self, parent=None, hibernate=False, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.hibernate = hibernate

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.title = FormLabel(
            f"""<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;'>
                <h2>🚀 {CConstants.APP_NAME}</h2>
                <p style='margin: 8px 0; font-size: 14px; opacity: 0.9;'>Version {CConstants.APP_VERSION}</p>
                <p style='margin: 0; font-size: 12px; opacity: 0.8;'>Connexion sécurisée</p>
            </div>"""
        )
        vbox = QHBoxLayout()

        self.loginUserGroupBox()
        vbox.addWidget(self.title)
        vbox.addWidget(self.topLeftGroupBox)
        self.setLayout(vbox)

        if hasattr(self, 'password_field') and self.password_field:
            self.password_field.setFocus()

    def loginUserGroupBox(self):
        self.topLeftGroupBox = QGroupBox(self.tr("🔐 Authentification"))
        self.liste_username = Owner.get_active_non_superusers()

        if not self.liste_username.exists():
            print("❌ Erreur: Aucun utilisateur actif trouvé")
            return

        self.box_username = QComboBox()
        self.box_username.setToolTip("👤 Sélectionnez votre nom d'utilisateur")
        self.box_username.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #0d6efd;
            }
        """)

        for index in self.liste_username:
            icon = "👑" if index.group == Owner.ADMIN else "👤"
            self.box_username.addItem(f"{icon} {index.username}")

        self.username_field = self.box_username

        self.password_field = EnterTabbedLineEdit()
        self.password_field.setEchoMode(LineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("Saisissez votre mot de passe")
        self.password_field.setToolTip("🔒 Mot de passe de votre compte utilisateur")
        self.password_field.setStyleSheet("""
            QLineEdit {
                padding: 10px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #0d6efd;
                box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
            }
        """)

        self.login_button = QPushButton("🔐 &Se connecter")
        self.login_button.setIcon(
            QIcon.fromTheme("save", QIcon(f"{CConstants.img_cmedia}login.png"))
        )
        self.login_button.setToolTip("Se connecter avec vos identifiants")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #218838;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.login_button.clicked.connect(self.login)

        self.cancel_button = QPushButton("❌ &Quitter")
        self.cancel_button.setToolTip("Fermer l'application")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel)

        self.login_error = ErrorLabel("")

        formbox = QFormLayout()
        formbox.setSpacing(16)
        formbox.setContentsMargins(20, 20, 20, 20)

        formbox.addRow(FormLabel("👤 Utilisateur"), self.username_field)
        formbox.addRow(FormLabel("🔒 Mot de passe"), self.password_field)
        formbox.addRow(FormLabel(""), self.login_button)
        formbox.addRow(FormLabel(""), self.cancel_button)
        formbox.addRow(FormLabel(""), self.login_error)

        self.reset_button = Button("🔑 Mot de passe oublié ?")
        self.reset_button.setToolTip("Cliquez ici si vous avez oublié votre mot de passe")
        self.reset_button.clicked.connect(self.show_reset_dialog)
        formbox.addRow(FormLabel(""), self.reset_button)

        if self.hibernate:
            self.cancel_button.setEnabled(False)
            self.cancel_button.setToolTip("❄️ Mode hibernation - Fermeture désactivée")

        self.topLeftGroupBox.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 16px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 8px 0 8px;
                background-color: #ffffff;
                color: #2c3e50;
            }
        """)
        self.topLeftGroupBox.setLayout(formbox)

    def is_valide(self):
        return not check_is_empty(self.password_field)

    def cancel(self):
        print("❌ Fermeture de l'application demandée par l'utilisateur")
        self.close()

    def login(self):
        self.login_error.setText("")
        if not self.is_valide():
            self.login_error.setText("❌ Veuillez saisir votre mot de passe")
            return

        current_index = self.box_username.currentIndex()
        if current_index < 0 or current_index >= len(self.liste_username):
            self.login_error.setText("❌ Erreur: Utilisateur sélectionné invalide")
            return

        users_list = list(self.liste_username)
        username = str(users_list[current_index].username)
        password = self.password_field.text().strip()

        try:
            owner = Owner.get(Owner.username == username)

            if not owner.check_login_attempts():
                remaining_time = owner.get_remaining_lockout_time()
                minutes = int(remaining_time / 60)
                seconds = int(remaining_time % 60)
                self.login_error.setText(
                    f"🔒 Compte temporairement bloqué\nVeuillez réessayer dans {minutes} min {seconds} s"
                )
                return False

            if not owner.verify_password(password):
                owner.increment_login_attempts()
                if not owner.check_login_attempts():
                    remaining_time = owner.get_remaining_lockout_time()
                    minutes = int(remaining_time / 60)
                    seconds = int(remaining_time % 60)
                    self.login_error.setText(
                        f"🔒 Trop de tentatives échouées\nCompte bloqué pour {minutes} min {seconds} s"
                    )
                else:
                    remaining = owner.MAX_LOGIN_ATTEMPTS - owner.login_attempts
                    self.login_error.setText(
                        f"❌ Identifiants incorrects\nIl vous reste {remaining} tentative(s)"
                    )
                field_error(self.password_field, "🔒 Mot de passe incorrect")
                self.password_field.clear()
                self.password_field.setFocus()
                return False

            owner.reset_login_attempts()
            Owner.update(is_identified=False).where(Owner.is_identified == True).execute()
            owner.is_identified = True
            owner.last_login = datetime.datetime.now()
            owner.login_count += 1
            owner.save()

            self.connected_owner = owner
            print(f"✅ Connexion réussie: {username}")
            if owner.is_identified:
                print(f"✅ Connexion réussie: {username}")
                # self.parent.on_login_success()
                self.login_successful.emit()
            self.accept()

        except Owner.DoesNotExist:
            self.login_error.setText("❌ Identifiants incorrects")
            field_error(self.password_field, "🔒 Mot de passe incorrect")
            self.password_field.clear()
            self.password_field.setFocus()
            return False
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            self.login_error.setText("❌ Erreur de connexion système")
            return False

    def show_reset_dialog(self):
        from .reset_password import ResetPasswordWidget
        dialog = ResetPasswordWidget(self)
        dialog.exec()