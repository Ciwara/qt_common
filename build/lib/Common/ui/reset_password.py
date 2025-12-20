#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QFormLayout, QGroupBox, QVBoxLayout, QMessageBox

from ..models import Owner
from .common import (
    Button,
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


class ResetPasswordWidget(FDialog, FWidget):
    title_page = "🔑 Réinitialisation du mot de passe"

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Création de l'interface
        self.create_ui()
        
        # Définir le focus sur le champ de nom d'utilisateur
        self.username_field.setFocus()

    def create_ui(self):
        """Création de l'interface utilisateur"""
        vbox = QVBoxLayout()
        
        # Titre
        self.title = FormLabel(
            f"""<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;'>
                <h2>🔑 Réinitialisation du mot de passe</h2>
                <p style='margin: 8px 0; font-size: 14px; opacity: 0.9;'>Entrez votre nom d'utilisateur pour commencer</p>
            </div>"""
        )
        
        # Groupe principal
        self.main_group = QGroupBox("🔐 Réinitialisation")
        formbox = QFormLayout()
        
        # Champ nom d'utilisateur
        self.username_field = LineEdit()
        self.username_field.setPlaceholderText("Votre nom d'utilisateur")
        self.username_field.setToolTip("Entrez votre nom d'utilisateur")
        
        # Boutons
        self.reset_button = Button("🔑 Réinitialiser")
        self.reset_button.clicked.connect(self.start_reset)
        
        self.cancel_button = Button("❌ Annuler")
        self.cancel_button.clicked.connect(self.close)
        
        # Message d'erreur
        self.error_label = ErrorLabel("")
        
        # Ajout des widgets au formulaire
        formbox.addRow(FormLabel("👤 Nom d'utilisateur"), self.username_field)
        formbox.addRow(self.error_label)
        formbox.addRow(self.cancel_button, self.reset_button)
        
        self.main_group.setLayout(formbox)
        
        # Ajout des widgets au layout principal
        vbox.addWidget(self.title)
        vbox.addWidget(self.main_group)
        
        self.setLayout(vbox)

    def start_reset(self):
        """Démarre le processus de réinitialisation"""
        username = self.username_field.text().strip()
        
        if not username:
            self.error_label.setText("❌ Veuillez saisir votre nom d'utilisateur")
            return
            
        try:
            # Rechercher l'utilisateur
            owner = Owner.get(Owner.username == username)
            
            # Générer le token de réinitialisation
            token = owner.generate_reset_token()
            
            # TODO: Envoyer le token par email ou SMS
            # Pour l'instant, on l'affiche dans une boîte de dialogue
            QMessageBox.information(
                self,
                "🔑 Token de réinitialisation",
                f"Votre token de réinitialisation est :\n\n{token}\n\n"
                "Ce token est valide pendant 1 heure.\n"
                "Veuillez le conserver précieusement."
            )
            
            # Ouvrir la fenêtre de réinitialisation
            self.open_reset_dialog(owner, token)
            
        except Owner.DoesNotExist:
            self.error_label.setText("❌ Utilisateur non trouvé")
        except Exception as e:
            self.error_label.setText(f"❌ Erreur : {str(e)}")

    def open_reset_dialog(self, owner, token):
        """Ouvre la fenêtre de réinitialisation du mot de passe"""
        dialog = ResetPasswordDialog(owner, token, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.accept()


class ResetPasswordDialog(QDialog, FWidget):
    def __init__(self, owner, token, parent=None):
        super().__init__(parent)
        self.owner = owner
        self.token = token
        
        self.setWindowTitle("🔑 Nouveau mot de passe")
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Création de l'interface
        self.create_ui()

    def create_ui(self):
        """Création de l'interface utilisateur"""
        vbox = QVBoxLayout()
        
        # Groupe principal
        self.main_group = QGroupBox("🔐 Nouveau mot de passe")
        formbox = QFormLayout()
        
        # Champ token
        self.token_field = LineEdit()
        self.token_field.setPlaceholderText("Token de réinitialisation")
        self.token_field.setToolTip("Entrez le token reçu")
        
        # Champ nouveau mot de passe
        self.password_field = EnterTabbedLineEdit()
        self.password_field.setEchoMode(LineEdit.Password)
        self.password_field.setPlaceholderText("Nouveau mot de passe")
        self.password_field.setToolTip("Entrez votre nouveau mot de passe")
        
        # Champ confirmation
        self.confirm_field = EnterTabbedLineEdit()
        self.confirm_field.setEchoMode(LineEdit.Password)
        self.confirm_field.setPlaceholderText("Confirmez le mot de passe")
        self.confirm_field.setToolTip("Confirmez votre nouveau mot de passe")
        
        # Boutons
        self.save_button = Button("💾 Enregistrer")
        self.save_button.clicked.connect(self.save_password)
        
        self.cancel_button = Button("❌ Annuler")
        self.cancel_button.clicked.connect(self.reject)
        
        # Message d'erreur
        self.error_label = ErrorLabel("")
        
        # Ajout des widgets au formulaire
        formbox.addRow(FormLabel("🔑 Token"), self.token_field)
        formbox.addRow(FormLabel("🔒 Nouveau mot de passe"), self.password_field)
        formbox.addRow(FormLabel("🔐 Confirmation"), self.confirm_field)
        formbox.addRow(self.error_label)
        formbox.addRow(self.cancel_button, self.save_button)
        
        self.main_group.setLayout(formbox)
        vbox.addWidget(self.main_group)
        
        self.setLayout(vbox)

    def save_password(self):
        """Sauvegarde le nouveau mot de passe"""
        token = self.token_field.text().strip()
        password = self.password_field.text().strip()
        confirm = self.confirm_field.text().strip()
        
        # Validation des champs
        if not token:
            self.error_label.setText("❌ Veuillez saisir le token")
            return
            
        if not password:
            self.error_label.setText("❌ Veuillez saisir un nouveau mot de passe")
            return
            
        if not confirm:
            self.error_label.setText("❌ Veuillez confirmer le mot de passe")
            return
            
        if password != confirm:
            self.error_label.setText("❌ Les mots de passe ne correspondent pas")
            return
            
        # Vérification du token
        if not self.owner.verify_reset_token(token):
            self.error_label.setText("❌ Token invalide ou expiré")
            return
            
        # Réinitialisation du mot de passe
        success, message = self.owner.reset_password(password)
        if not success:
            self.error_label.setText(f"❌ {message}")
            return
            
        # Succès
        QMessageBox.information(
            self,
            "✅ Succès",
            "Votre mot de passe a été réinitialisé avec succès.\n"
            "Vous pouvez maintenant vous connecter avec votre nouveau mot de passe."
        )
        
        self.accept() 