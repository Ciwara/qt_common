#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtWidgets import (
    QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QPushButton,
    QVBoxLayout, QWidget, QLabel, QFrame, QSizePolicy
)

from ..models import Owner
from .common import (
    EnterTabbedLineEdit,
    ErrorLabel,
    FDialog,
    FormLabel,
    FWidget,
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
        self.is_loading = False

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(500, 600)
        self.resize(550, 700)
        
        # Layout principal centré
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # En-tête avec logo et titre
        self.create_header()
        main_layout.addWidget(self.header_widget)
        main_layout.addSpacing(30)
        
        # Formulaire de connexion
        self.loginUserGroupBox()
        main_layout.addWidget(self.topLeftGroupBox)
        main_layout.addStretch()
        
        # Footer avec informations
        self.create_footer()
        main_layout.addWidget(self.footer_widget)

        if hasattr(self, 'password_field') and self.password_field:
            self.password_field.setFocus()
    
    def _get_org_display_name(self):
        """Retourne le nom d'organisation si disponible, sinon le nom de l'app"""
        # 1) Organization (prioritaire)
        try:
            from ..models import Organization
            org = Organization.get_or_none(Organization.id == 1)
            if org is not None:
                name_orga = (getattr(org, "name_orga", None) or "").strip()
                if name_orga:
                    return name_orga
        except Exception:
            pass
        
        # 2) Settings
        try:
            from ..models import Settings
            st = Settings().get(id=1)
            org_name = (getattr(st, "org_name", None) or "").strip()
            if org_name:
                return org_name
        except Exception:
            pass
        
        # 3) Fallback sur APP_NAME
        return getattr(CConstants, "APP_NAME", None) or "Application"
    
    def _get_org_logo_pixmap(self):
        """Retourne le logo de l'organisation si disponible"""
        try:
            import base64
            from ..models import Organization
            org = Organization.get_or_none(Organization.id == 1)
            if org is not None:
                # Essayer logo_orga (base64/dataURL)
                logo_b64 = getattr(org, "logo_orga", None)
                if isinstance(logo_b64, str):
                    s = logo_b64.strip()
                    if s:
                        if s.startswith("data:") and "," in s:
                            s = s.split(",", 1)[1].strip()
                        s = "".join(s.split())
                        try:
                            raw = base64.b64decode(s)
                            pixmap = QPixmap()
                            if pixmap.loadFromData(raw):
                                return pixmap
                        except Exception:
                            pass
                # Essayer logo (binaire direct)
                if hasattr(org, 'logo') and org.logo:
                    pixmap = QPixmap()
                    if pixmap.loadFromData(org.logo):
                        return pixmap
        except Exception:
            pass
        return None
    
    def _get_org_info(self):
        """Retourne les informations de l'organisation"""
        org_name = self._get_org_display_name()
        org_logo = self._get_org_logo_pixmap()
        
        # Récupérer d'autres infos si disponibles
        org_address = ""
        org_phone = ""
        org_email = ""
        
        try:
            from ..models import Organization
            org = Organization.get_or_none(Organization.id == 1)
            if org is not None:
                org_address = getattr(org, "address", None) or ""
                org_phone = getattr(org, "phone", None) or ""
                org_email = getattr(org, "email", None) or ""
        except Exception:
            pass
        
        return {
            'name': org_name,
            'logo': org_logo,
            'address': org_address,
            'phone': org_phone,
            'email': org_email
        }
    
    def create_header(self):
        """Crée l'en-tête avec logo et titre"""
        self.header_widget = QWidget()
        header_layout = QVBoxLayout(self.header_widget)
        header_layout.setSpacing(12)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Récupérer les informations de l'organisation
        org_info = self._get_org_info()
        
        # Logo de l'organisation (si disponible)
        if org_info['logo'] and not org_info['logo'].isNull():
            logo_label = QLabel()
            logo_pixmap = org_info['logo'].scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(logo_label)
        
        # Nom de l'organisation
        title_label = QLabel(org_info['name'])
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: palette(text);
                padding: 10px;
            }
        """)
        header_layout.addWidget(title_label)
        
        # Informations supplémentaires de l'organisation
        org_details = []
        if org_info['address']:
            org_details.append(f"📍 {org_info['address']}")
        if org_info['phone']:
            org_details.append(f"📞 {org_info['phone']}")
        if org_info['email']:
            org_details.append(f"📧 {org_info['email']}")
        
        # Sous-titre avec version et détails
        subtitle_text = f"Version {CConstants.APP_VERSION} • Connexion sécurisée"
        if org_details:
            subtitle_text += f"\n{' • '.join(org_details[:2])}"  # Limiter à 2 détails pour ne pas surcharger
        
        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: palette(mid);
                font-size: 12px;
                padding: 5px;
                line-height: 1.4;
            }
        """)
        header_layout.addWidget(subtitle_label)
        
        # Ligne de séparation
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("""
            QFrame {
                color: palette(midlight);
                max-width: 200px;
            }
        """)
        header_layout.addWidget(separator)
    
    def create_footer(self):
        """Crée le footer avec informations"""
        self.footer_widget = QWidget()
        footer_layout = QVBoxLayout(self.footer_widget)
        footer_layout.setSpacing(8)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Message de sécurité
        security_label = QLabel("🔒 Vos données sont protégées")
        security_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        security_label.setStyleSheet("""
            QLabel {
                color: palette(mid);
                font-size: 11px;
                padding: 5px;
            }
        """)
        footer_layout.addWidget(security_label)

    def loginUserGroupBox(self):
        self.topLeftGroupBox = QGroupBox()
        self.topLeftGroupBox.setTitle("🔐 Authentification")
        self.liste_username = Owner.get_active_non_superusers()

        if not self.liste_username.exists():
            print("❌ Erreur: Aucun utilisateur actif trouvé")
            return

        # Layout principal du formulaire
        formbox = QFormLayout()
        formbox.setSpacing(20)
        formbox.setContentsMargins(30, 30, 30, 30)
        formbox.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # Champ utilisateur
        self.box_username = QComboBox()
        self.box_username.setToolTip("👤 Sélectionnez votre nom d'utilisateur")
        self.box_username.setMinimumHeight(45)
        self.box_username.setStyleSheet("""
            QComboBox {
                padding: 12px 15px;
                border: 2px solid palette(midlight);
                border-radius: 8px;
                font-size: 14px;
                background-color: palette(base);
                color: palette(text);
            }
            QComboBox:hover {
                border-color: palette(highlight);
            }
            QComboBox:focus {
                border-color: palette(highlight);
                border-width: 2px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid palette(text);
                margin-right: 5px;
            }
        """)

        for index in self.liste_username:
            icon = "👑" if index.group == Owner.ADMIN else "👤"
            self.box_username.addItem(f"{icon} {index.username}")

        self.username_field = self.box_username
        formbox.addRow(FormLabel("👤 Utilisateur :"), self.username_field)

        # Champ mot de passe
        self.password_field = EnterTabbedLineEdit()
        from PyQt6.QtWidgets import QLineEdit
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("Saisissez votre mot de passe")
        self.password_field.setToolTip("🔒 Mot de passe de votre compte utilisateur")
        self.password_field.setMinimumHeight(45)
        self.password_field.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid palette(midlight);
                border-radius: 8px;
                font-size: 14px;
                background-color: palette(base);
                color: palette(text);
            }
            QLineEdit:hover {
                border-color: palette(highlight);
            }
            QLineEdit:focus {
                border-color: palette(highlight);
                border-width: 2px;
            }
        """)
        # Permettre la connexion avec Enter
        self.password_field.returnPressed.connect(self.login)
        formbox.addRow(FormLabel("🔒 Mot de passe :"), self.password_field)

        # Message d'erreur
        self.login_error = ErrorLabel("")
        self.login_error.setWordWrap(True)
        self.login_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_error.setStyleSheet("""
            QLabel {
                padding: 10px;
                border-radius: 6px;
                background-color: palette(alternate-base);
                min-height: 20px;
            }
        """)
        formbox.addRow(FormLabel(""), self.login_error)

        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self.login_button = QPushButton("🔐 Se connecter")
        self.login_button.setIcon(
            QIcon.fromTheme("save", QIcon(f"{CConstants.img_cmedia}login.png"))
        )
        self.login_button.setToolTip("Se connecter avec vos identifiants")
        self.login_button.setMinimumHeight(50)
        self.login_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border: none;
                border-radius: 8px;
                padding: 14px 24px;
                font-weight: 600;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: palette(highlight);
                opacity: 0.9;
            }
            QPushButton:pressed {
                background-color: palette(highlight);
                opacity: 0.8;
            }
            QPushButton:disabled {
                background-color: palette(mid);
                color: palette(mid-text);
            }
        """)
        self.login_button.clicked.connect(self.login)
        buttons_layout.addWidget(self.login_button)

        self.cancel_button = QPushButton("❌ Quitter")
        self.cancel_button.setToolTip("Fermer l'application")
        self.cancel_button.setMinimumHeight(50)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: palette(mid);
                color: palette(text);
                border: 2px solid palette(midlight);
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: palette(midlight);
            }
            QPushButton:pressed {
                background-color: palette(mid);
            }
            QPushButton:disabled {
                background-color: palette(alternate-base);
                color: palette(mid-text);
            }
        """)
        self.cancel_button.clicked.connect(self.cancel)
        
        if self.hibernate:
            self.cancel_button.setEnabled(False)
            self.cancel_button.setToolTip("❄️ Mode hibernation - Fermeture désactivée")
        
        buttons_layout.addWidget(self.cancel_button)
        formbox.addRow(FormLabel(""), buttons_layout)

        # Lien mot de passe oublié
        self.reset_button = Button("🔑 Mot de passe oublié ?")
        self.reset_button.setToolTip("Cliquez ici si vous avez oublié votre mot de passe")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: palette(link);
                border: none;
                padding: 8px;
                font-size: 12px;
                text-align: center;
            }
            QPushButton:hover {
                color: palette(link);
                text-decoration: underline;
            }
        """)
        self.reset_button.clicked.connect(self.show_reset_dialog)
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()
        reset_layout.addWidget(self.reset_button)
        reset_layout.addStretch()
        formbox.addRow(FormLabel(""), reset_layout)

        # Style du GroupBox
        self.topLeftGroupBox.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 18px;
                border: 2px solid palette(midlight);
                border-radius: 12px;
                margin-top: 20px;
                padding-top: 25px;
                background-color: palette(base);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 20px;
                padding: 0 10px;
                background-color: palette(base);
                color: palette(text);
            }
        """)
        self.topLeftGroupBox.setLayout(formbox)

    def is_valide(self):
        return not check_is_empty(self.password_field)

    def cancel(self):
        print("❌ Fermeture de l'application demandée par l'utilisateur")
        self.close()

    def login(self):
        if self.is_loading:
            return
            
        self.login_error.setText("")
        if not self.is_valide():
            self.login_error.setText("❌ Veuillez saisir votre mot de passe")
            field_error(self.password_field, "Mot de passe requis")
            return

        current_index = self.box_username.currentIndex()
        if current_index < 0 or current_index >= len(self.liste_username):
            self.login_error.setText("❌ Erreur: Utilisateur sélectionné invalide")
            return

        users_list = list(self.liste_username)
        username = str(users_list[current_index].username)
        password = self.password_field.text().strip()

        # Désactiver les boutons pendant la connexion
        self.set_loading_state(True)

        try:
            owner = Owner.get(Owner.username == username)

            if not owner.check_login_attempts():
                remaining_time = owner.get_remaining_lockout_time()
                minutes = int(remaining_time / 60)
                seconds = int(remaining_time % 60)
                self.login_error.setText(
                    f"🔒 Compte temporairement bloqué\nVeuillez réessayer dans {minutes} min {seconds} s"
                )
                self.set_loading_state(False)
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
                self.set_loading_state(False)
                return False

            owner.reset_login_attempts()
            Owner.update(is_identified=False).where(Owner.is_identified).execute()
            owner.is_identified = True
            owner.last_login = datetime.datetime.now()
            owner.login_count += 1
            owner.save()

            self.connected_owner = owner
            print(f"✅ Connexion réussie: {username}")
            if owner.is_identified:
                print(f"✅ Connexion réussie: {username}")
                self.login_successful.emit()
            self.set_loading_state(False)
            self.accept()

        except Owner.DoesNotExist:
            self.login_error.setText("❌ Identifiants incorrects")
            field_error(self.password_field, "🔒 Mot de passe incorrect")
            self.password_field.clear()
            self.password_field.setFocus()
            self.set_loading_state(False)
            return False
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            self.login_error.setText("❌ Erreur de connexion système")
            self.set_loading_state(False)
            return False
    
    def set_loading_state(self, loading):
        """Active ou désactive l'état de chargement"""
        self.is_loading = loading
        self.login_button.setEnabled(not loading)
        self.cancel_button.setEnabled(not loading and not self.hibernate)
        self.password_field.setEnabled(not loading)
        self.box_username.setEnabled(not loading)
        
        if loading:
            self.login_button.setText("⏳ Connexion...")
        else:
            self.login_button.setText("🔐 Se connecter")

    def show_reset_dialog(self):
        from .reset_password import ResetPasswordWidget
        dialog = ResetPasswordWidget(self)
        dialog.exec()