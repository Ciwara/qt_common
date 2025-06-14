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

        # Créer d'abord les champs de connexion
        self.loginUserGroupBox()
        
        # Ajouter les widgets au layout
        vbox.addWidget(self.title)
        vbox.addWidget(self.topLeftGroupBox)
        
        # Définir le layout
        self.setLayout(vbox)
        
        # Définir le focus APRÈS la création des champs
        if hasattr(self, 'password_field') and self.password_field:
            self.password_field.setFocus()

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

        formbox = QFormLayout()
        formbox.setSpacing(16)
        formbox.setContentsMargins(20, 20, 20, 20)
        
        formbox.addRow(FormLabel("👤 Utilisateur"), self.username_field)
        formbox.addRow(FormLabel("🔒 Mot de passe"), self.password_field)
        formbox.addRow(FormLabel(""), self.login_button)
        formbox.addRow(FormLabel(""), self.cancel_button)
        formbox.addRow(FormLabel(""), self.login_error)
        
        # Ajout du bouton de réinitialisation
        self.reset_button = Button("🔑 Mot de passe oublié ?")
        self.reset_button.setToolTip("Cliquez ici si vous avez oublié votre mot de passe")
        self.reset_button.clicked.connect(self.show_reset_dialog)
        formbox.addRow(FormLabel(""), self.reset_button)
        
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
        password = self.password_field.text().strip()

        try:
            # Vérifier d'abord les identifiants
            owner = Owner.get(Owner.username == username)
            
            # Vérifier si l'utilisateur n'est pas bloqué
            if not owner.check_login_attempts():
                remaining_time = owner.get_remaining_lockout_time()
                minutes = int(remaining_time / 60)
                seconds = int(remaining_time % 60)
                self.login_error.setText(
                    f"🔒 Compte temporairement bloqué\n"
                    f"Veuillez réessayer dans {minutes} minutes et {seconds} secondes"
                )
                return False
            
            if not owner.verify_password(password):
                # Incrémenter le compteur de tentatives
                owner.increment_login_attempts()
                
                # Vérifier si l'utilisateur est maintenant bloqué
                if not owner.check_login_attempts():
                    remaining_time = owner.get_remaining_lockout_time()
                    minutes = int(remaining_time / 60)
                    seconds = int(remaining_time % 60)
                    self.login_error.setText(
                        f"🔒 Trop de tentatives échouées\n"
                        f"Compte bloqué pour {minutes} minutes et {seconds} secondes"
                    )
                else:
                    remaining = owner.MAX_LOGIN_ATTEMPTS - owner.login_attempts
                    self.login_error.setText(
                        f"❌ Identifiants incorrects\n"
                        f"Il vous reste {remaining} tentative(s)"
                    )
                
                field_error(self.password_field, "🔒 Mot de passe incorrect")
                # Vider le champ de mot de passe pour sécurité
                self.password_field.clear()
                self.password_field.setFocus()
                return False
            
            # Réinitialiser les tentatives de connexion
            owner.reset_login_attempts()
            
            # Déconnecter tous les utilisateurs actuellement connectés
            Owner.update(is_identified=False).where(Owner.is_identified == True).execute()
            
            # Mettre à jour les informations de connexion
            owner.is_identified = True
            owner.last_login = datetime.datetime.now()
            owner.login_count += 1
            owner.save()
            
            # Stocker l'utilisateur connecté
            self.connected_owner = owner
            
            # Messages de succès
            user_type = "👑 Administrateur" if owner.group == Owner.ADMIN else "👤 Utilisateur"
            print(f"✅ Connexion réussie - {user_type}: {username}")
            
            self.accept()
        except Owner.DoesNotExist:
            print(f"❌ Échec de connexion - Utilisateur non trouvé: {username}")
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

    def show_reset_dialog(self):
        """Affiche la fenêtre de réinitialisation de mot de passe"""
        from .reset_password import ResetPasswordWidget
        dialog = ResetPasswordWidget(self)
        dialog.exec_()
