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
    print(f"⚠️ Erreur lors de l'importation de CConstants: {exc}")


class LoginWidget(FDialog, FWidget):
    title_page = "🔐 Connexion Sécurisée"

    def __init__(self, parent=None, hibernate=False, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.hibernate = hibernate

        self.setWindowFlags(Qt.FramelessWindowHint)
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
        
        # Définir le focus APRÈS la création des champs
        if hasattr(self, 'password_field') and self.password_field:
            self.setFocusProxy(self.password_field)
        self.setLayout(vbox)

    def loginUserGroupBox(self):
        self.topLeftGroupBox = QGroupBox(self.tr("🔐 Authentification"))
        self.liste_username = Owner.get_active_non_superusers()

        # Vérifier s'il y a des utilisateurs actifs
        if not self.liste_username.exists():
            print("❌ Erreur: Aucun utilisateur actif trouvé")
            return

        # Combobox widget avec amélioration visuelle
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
            # Améliorer l'affichage avec icônes selon le groupe
            icon = "👑" if index.group == Owner.ADMIN else "👤"
            self.box_username.addItem(f"{icon} {index.username}")

        # Username field
        self.username_field = self.box_username
        
        # Password field amélioré
        self.password_field = EnterTabbedLineEdit()
        self.password_field.setEchoMode(LineEdit.Password)
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
        self.password_field.setFocus()
        # Login button moderne
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

        # Login error amélioré
        self.login_error = ErrorLabel("")
        # self.login_error.setStyleSheet("""
        #     QLabel {
        #         color: #dc3545;
        #         background-color: #f8d7da;
        #         border: 1px solid #f5c6cb;
        #         border-radius: 6px;
        #         padding: 8px 12px;
        #         font-weight: 500;
        #     }
        # """)

        formbox = QFormLayout()
        formbox.setSpacing(16)
        formbox.setContentsMargins(20, 20, 20, 20)
        
        formbox.addRow(FormLabel("👤 Utilisateur"), self.username_field)
        formbox.addRow(FormLabel("🔒 Mot de passe"), self.password_field)
        formbox.addRow(FormLabel(""), self.login_button)
        formbox.addRow(FormLabel(""), self.cancel_button)
        formbox.addRow(FormLabel(""), self.login_error)
        if self.hibernate:
            self.cancel_button.setEnabled(False)
            self.cancel_button.setToolTip("❄️ Mode hibernation - Fermeture désactivée")

        # Style moderne pour la boîte de groupe
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
        """Validation des champs de connexion"""
        return not check_is_empty(self.password_field)

    def cancel(self):
        """Fermeture de l'application"""
        print("❌ Fermeture de l'application demandée par l'utilisateur")
        self.close()

    def login(self):
        """Gestion de la logique de connexion sécurisée"""
        # Réinitialiser le message d'erreur
        self.login_error.setText("")
        
        if not self.is_valide():
            self.login_error.setText("❌ Veuillez saisir votre mot de passe")
            return

        # Vérifier que la liste n'est pas vide et que l'index est valide
        current_index = self.box_username.currentIndex()
        if current_index < 0 or current_index >= len(self.liste_username):
            self.login_error.setText("❌ Erreur: Utilisateur sélectionné invalide")
            return

        # Convertir la requête en liste pour accéder par index de manière sécurisée
        users_list = list(self.liste_username)
        if current_index >= len(users_list):
            self.login_error.setText("❌ Erreur: Index utilisateur invalide")
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
            
            # Messages de succès
            user_type = "👑 Administrateur" if owner.group == Owner.ADMIN else "👤 Utilisateur"
            print(f"✅ Connexion réussie - {user_type}: {username}")
            
            self.accept()
        except Owner.DoesNotExist:
            print(f"❌ Échec de connexion - Mot de passe incorrect pour: {username}")
            self.login_error.setText("❌ Identifiants incorrects")
            field_error(self.password_field, "🔒 Mot de passe incorrect")
            # Vider le champ de mot de passe pour sécurité
            self.password_field.clear()
            self.password_field.setFocus()
            return False
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            self.login_error.setText("❌ Erreur de connexion système")
            return False
