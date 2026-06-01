#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

import datetime

from PyQt6.QtCore import QEvent, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QFrame,
    QSizePolicy,
    QToolButton,
    QGraphicsDropShadowEffect,
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


class LoginWidget(FDialog, FWidget):
    title_page = "Connexion"
    login_successful = pyqtSignal()

    def __init__(self, parent=None, hibernate=False, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.hibernate = hibernate
        self.is_loading = False
        self._drag_anchor = None
        self._no_users = False

        self.setObjectName("LoginRoot")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(480, 560)
        self.resize(520, 640)
        self.setStyleSheet(
            """
            #LoginRoot { background-color: palette(alternate-base); }
            """
        )

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(28, 28, 28, 28)
        root_layout.setSpacing(0)

        row = QHBoxLayout()
        row.addStretch(1)
        self._card = QFrame()
        self._card.setObjectName("loginCard")
        self._card.setMaximumWidth(440)
        self._card.setStyleSheet(
            """
            #loginCard {
                background-color: palette(base);
                border: 1px solid palette(midlight);
                border-radius: 14px;
            }
            """
        )
        try:
            shadow = QGraphicsDropShadowEffect(self._card)
            shadow.setBlurRadius(22)
            shadow.setOffset(0, 8)
            shadow.setColor(self.palette().color(self.palette().ColorRole.Shadow))
            self._card.setGraphicsEffect(shadow)
        except Exception:
            pass
        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        accent = QFrame()
        accent.setFixedHeight(4)
        accent.setStyleSheet(
            """
            QFrame {
                background-color: palette(highlight);
                border: none;
                border-top-left-radius: 13px;
                border-top-right-radius: 13px;
            }
            """
        )
        card_layout.addWidget(accent)

        inner = QWidget()
        inner_l = QVBoxLayout(inner)
        inner_l.setContentsMargins(24, 22, 24, 20)
        inner_l.setSpacing(18)

        self.create_header()
        self.header_widget.installEventFilter(self)
        inner_l.addWidget(self.header_widget)

        self.loginUserGroupBox()
        inner_l.addWidget(self.topLeftGroupBox)

        self.create_footer()
        inner_l.addWidget(self.footer_widget)

        card_layout.addWidget(inner)
        row.addWidget(self._card, 0, Qt.AlignmentFlag.AlignHCenter)
        row.addStretch(1)
        root_layout.addLayout(row)

        if getattr(self, "password_field", None) is not None:
            self.password_field.setFocus()

    def eventFilter(self, watched, event):
        et = event.type()
        if watched is self.header_widget:
            if et == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self._drag_anchor = (
                        event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    )
            elif et == QEvent.Type.MouseMove:
                if (
                    self._drag_anchor is not None
                    and event.buttons() & Qt.MouseButton.LeftButton
                ):
                    self.move(event.globalPosition().toPoint() - self._drag_anchor)
            elif et == QEvent.Type.MouseButtonRelease:
                self._drag_anchor = None

        if watched is getattr(self, "password_field", None):
            if et in (
                QEvent.Type.KeyPress,
                QEvent.Type.KeyRelease,
                QEvent.Type.FocusIn,
            ):
                self._update_capslock_warning()
        return super().eventFilter(watched, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and not self.hibernate:
            self.cancel()
            event.accept()
            return
        super().keyPressEvent(event)

    def _get_org_display_name(self):
        try:
            from ..models import Organization

            org = Organization.get_or_none(Organization.id == 1)
            if org is not None:
                name_orga = (getattr(org, "name_orga", None) or "").strip()
                if name_orga:
                    return name_orga
        except Exception:
            pass

        try:
            from ..models import Settings

            st = Settings().get(id=1)
            org_name = (getattr(st, "org_name", None) or "").strip()
            if org_name:
                return org_name
        except Exception:
            pass

        return getattr(CConstants, "APP_NAME", None) or "Application"

    def _get_org_logo_pixmap(self):
        try:
            import base64

            from ..models import Organization

            org = Organization.get_or_none(Organization.id == 1)
            if org is not None:
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
                if hasattr(org, "logo") and org.logo:
                    pixmap = QPixmap()
                    if pixmap.loadFromData(org.logo):
                        return pixmap
        except Exception:
            pass
        return None

    @staticmethod
    def _format_org_phone(phone):
        if phone is None or phone == "":
            return ""
        return str(phone).strip()

    def _get_org_info(self):
        org_name = self._get_org_display_name()
        org_logo = self._get_org_logo_pixmap()

        org_address = ""
        org_phone = ""
        org_email = ""

        try:
            from ..models import Organization

            org = Organization.get_or_none(Organization.id == 1)
            if org is not None:
                org_address = (getattr(org, "adress_org", None) or "").strip()
                org_phone = self._format_org_phone(getattr(org, "phone", None))
                org_email = (getattr(org, "email_org", None) or "").strip()
        except Exception:
            pass

        return {
            "name": org_name,
            "logo": org_logo,
            "address": org_address,
            "phone": org_phone,
            "email": org_email,
        }

    def create_header(self):
        self.header_widget = QWidget()
        self.header_widget.setCursor(Qt.CursorShape.OpenHandCursor)
        header_layout = QVBoxLayout(self.header_widget)
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(0, 4, 0, 0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.addStretch(1)
        self.close_btn = QToolButton()
        self.close_btn.setText("×")
        self.close_btn.setToolTip("Fermer")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setStyleSheet(
            """
            QToolButton {
                border: 1px solid palette(midlight);
                border-radius: 6px;
                background-color: palette(base);
                color: palette(text);
                font-size: 16px;
            }
            QToolButton:hover { background-color: palette(alternate-base); }
            QToolButton:pressed { background-color: palette(midlight); }
            """
        )
        self.close_btn.clicked.connect(self.cancel)
        top_row.addWidget(self.close_btn, 0, Qt.AlignmentFlag.AlignRight)
        header_layout.addLayout(top_row)

        org_info = self._get_org_info()

        if org_info["logo"] and not org_info["logo"].isNull():
            logo_label = QLabel()
            logo_pixmap = org_info["logo"].scaled(
                96,
                96,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(logo_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(logo_label)

        title_label = QLabel(org_info["name"])
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(
            """
            QLabel {
                color: palette(text);
                padding: 4px 8px;
            }
            """
        )
        header_layout.addWidget(title_label)

        org_details = []
        if org_info["address"]:
            org_details.append(f"📍 {org_info['address']}")
        if org_info["phone"]:
            org_details.append(f"📞 {org_info['phone']}")
        if org_info["email"]:
            org_details.append(f"📧 {org_info['email']}")

        subtitle_text = (
            f"{getattr(CConstants, 'APP_NAME', 'App')} · v{CConstants.APP_VERSION}\n"
            "Veuillez vous identifier"
        )
        if org_details:
            subtitle_text += "\n" + " · ".join(org_details[:2])

        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet(
            """
            QLabel {
                color: palette(mid);
                font-size: 11px;
                padding: 2px 6px;
                line-height: 1.45;
            }
            """
        )
        header_layout.addWidget(subtitle_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Plain)
        separator.setFixedHeight(1)
        separator.setStyleSheet(
            "QFrame { background-color: palette(midlight); border: none; max-height: 1px; }"
        )
        header_layout.addWidget(separator)

    def create_footer(self):
        self.footer_widget = QWidget()
        footer_layout = QVBoxLayout(self.footer_widget)
        footer_layout.setSpacing(4)
        footer_layout.setContentsMargins(0, 8, 0, 0)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if not self.hibernate:
            hint = QLabel(
                "Échap · quitter   ·   Glisser l’en-tête pour déplacer la fenêtre"
            )
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint.setStyleSheet(
                "QLabel { color: palette(mid); font-size: 10px; padding: 2px; }"
            )
            footer_layout.addWidget(hint)
        else:
            hint_h = QLabel("Glisser l’en-tête pour déplacer la fenêtre")
            hint_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint_h.setStyleSheet(
                "QLabel { color: palette(mid); font-size: 10px; padding: 2px; }"
            )
            footer_layout.addWidget(hint_h)

        security_label = QLabel("Mot de passe chiffré · tentatives limitées")
        security_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        security_label.setStyleSheet(
            "QLabel { color: palette(mid); font-size: 10px; padding: 2px; }"
        )
        footer_layout.addWidget(security_label)

    def _toggle_password_visibility(self, checked: bool):
        self.password_field.setEchoMode(
            QLineEdit.EchoMode.Normal
            if checked
            else QLineEdit.EchoMode.Password
        )
        self._pwd_toggle_action.setToolTip(
            "Masquer le mot de passe" if checked else "Afficher le mot de passe"
        )

    def loginUserGroupBox(self):
        # Préférer l'utilisateur le plus récent en haut de liste
        try:
            self.liste_username = Owner.get_active_non_superusers().order_by(
                Owner.last_login.desc()
            )
        except Exception:
            self.liste_username = Owner.get_active_non_superusers()

        if not self.liste_username.exists():
            print("❌ Erreur: Aucun utilisateur actif trouvé")
            self._no_users = True
            self.topLeftGroupBox = QGroupBox()
            self.topLeftGroupBox.setTitle("⚠️ Aucun utilisateur actif")
            lv = QVBoxLayout(self.topLeftGroupBox)
            msg = QLabel(
                "Il n’y a aucun compte utilisateur actif.\n"
                "Configurez la base ou restaurez une sauvegarde, puis relancez l’application."
            )
            msg.setWordWrap(True)
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lv.addWidget(msg)
            b = QPushButton("Fermer")
            b.clicked.connect(self.cancel)
            lv.addWidget(b)
            self.login_error = ErrorLabel("")
            self.box_username = None
            self.password_field = None
            self.login_button = None
            self.cancel_button = None
            self.reset_button = None
            return

        self.topLeftGroupBox = QGroupBox()
        self.topLeftGroupBox.setTitle("Authentification")

        formbox = QFormLayout()
        formbox.setSpacing(16)
        formbox.setContentsMargins(4, 8, 4, 12)
        formbox.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        formbox.setHorizontalSpacing(12)

        self.box_username = QComboBox()
        self.box_username.setToolTip("Compte utilisateur")

        for index in self.liste_username:
            badge = "Admin" if index.group == Owner.ADMIN else "Utilisateur"
            self.box_username.addItem(f"{index.username}  ·  {badge}")

        self.username_field = self.box_username
        formbox.addRow(FormLabel("Utilisateur"), self.username_field)

        self.password_field = EnterTabbedLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("Mot de passe")
        self.password_field.setToolTip("Mot de passe du compte sélectionné")
        self.password_field.setAccessibleName("Mot de passe")
        self.password_field.returnPressed.connect(self.login)
        self.password_field.installEventFilter(self)

        self._pwd_toggle_action = QAction("👁", self.password_field)
        self._pwd_toggle_action.setCheckable(True)
        self._pwd_toggle_action.setToolTip("Afficher le mot de passe")
        self._pwd_toggle_action.toggled.connect(self._toggle_password_visibility)
        self.password_field.addAction(
            self._pwd_toggle_action, QLineEdit.ActionPosition.TrailingPosition
        )

        formbox.addRow(FormLabel("Mot de passe"), self.password_field)

        self.capslock_warning = QLabel("")
        self.capslock_warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.capslock_warning.setStyleSheet(
            "QLabel { color: palette(mid); font-size: 11px; padding: 0 4px; }"
        )
        formbox.addRow(FormLabel(""), self.capslock_warning)

        self.login_error = ErrorLabel("")
        self.login_error.setWordWrap(True)
        self.login_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_error.setStyleSheet(
            """
            QLabel {
                padding: 8px;
                border-radius: 6px;
                background-color: palette(alternate-base);
                min-height: 18px;
            }
            """
        )
        formbox.addRow(FormLabel(""), self.login_error)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.login_button = QPushButton("Se connecter")
        self.login_button.setObjectName("primaryButton")
        self.login_button.setIcon(
            QIcon.fromTheme("unlock", QIcon(f"{CConstants.img_cmedia}login.png"))
        )
        self.login_button.setToolTip("Valider (Entrée)")
        self.login_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.login_button.clicked.connect(self.login)
        self.login_button.setDefault(True)
        buttons_layout.addWidget(self.login_button, 2)

        self.cancel_button = QPushButton("Quitter")
        self.cancel_button.setToolTip("Fermer l’application (Échap)")
        self.cancel_button.clicked.connect(self.cancel)

        if self.hibernate:
            self.cancel_button.setEnabled(False)
            self.cancel_button.setToolTip("Fermeture désactivée (mode veille)")

        buttons_layout.addWidget(self.cancel_button, 1)
        formbox.addRow(FormLabel(""), buttons_layout)

        self.reset_button = Button("Mot de passe oublié ?")
        self.reset_button.setObjectName("linkButton")
        self.reset_button.setToolTip("Réinitialisation du mot de passe")
        self.reset_button.clicked.connect(self.show_reset_dialog)
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()
        reset_layout.addWidget(self.reset_button)
        reset_layout.addStretch()
        formbox.addRow(FormLabel(""), reset_layout)

        self.topLeftGroupBox.setStyleSheet(
            """
            QGroupBox {
                font-weight: 600;
                font-size: 15px;
                border: none;
                margin-top: 4px;
                padding-top: 12px;
                background-color: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 2px;
                padding: 0 4px 8px 0;
                color: palette(text);
            }
            """
        )
        self.topLeftGroupBox.setLayout(formbox)

    def is_valide(self):
        if self.password_field is None:
            return False
        return not check_is_empty(self.password_field)

    def cancel(self):
        print("❌ Fermeture de l'application demandée par l'utilisateur")
        self.close()

    def _update_capslock_warning(self):
        try:
            mods = self.keyboardModifiers()
            caps_on = bool(mods & Qt.KeyboardModifier.CapsLockModifier)
        except Exception:
            caps_on = False
        if getattr(self, "capslock_warning", None) is None:
            return
        self.capslock_warning.setText("Attention: Verr. Maj activée" if caps_on else "")

    def login(self):
        if self._no_users or self.login_button is None:
            return
        if self.is_loading:
            return

        self.login_error.setText("")
        self._update_capslock_warning()
        if not self.is_valide():
            self.login_error.setText("❌ Saisissez votre mot de passe")
            field_error(self.password_field, "Mot de passe requis")
            return

        users_list = list(self.liste_username)
        current_index = self.box_username.currentIndex()
        if current_index < 0 or current_index >= len(users_list):
            self.login_error.setText("❌ Utilisateur invalide")
            return

        username = str(users_list[current_index].username)
        password = self.password_field.text().strip()

        self.set_loading_state(True)

        try:
            owner = Owner.get(Owner.username == username)

            if not owner.check_login_attempts():
                remaining_time = owner.get_remaining_lockout_time()
                minutes = int(remaining_time / 60)
                seconds = int(remaining_time % 60)
                self.login_error.setText(
                    f"🔒 Compte temporairement bloqué\nRéessayez dans {minutes} min {seconds} s"
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
                        f"🔒 Trop de tentatives\nCompte bloqué {minutes} min {seconds} s"
                    )
                else:
                    remaining = owner.MAX_LOGIN_ATTEMPTS - owner.login_attempts
                    self.login_error.setText(
                        f"❌ Mot de passe incorrect\nEncore {remaining} tentative(s)"
                    )
                field_error(self.password_field, "Mot de passe incorrect")
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
            self.login_successful.emit()
            self.set_loading_state(False)
            self.accept()

        except Owner.DoesNotExist:
            self.login_error.setText("❌ Utilisateur ou mot de passe incorrect")
            field_error(self.password_field, "Vérifiez vos identifiants")
            self.password_field.clear()
            self.password_field.setFocus()
            self.set_loading_state(False)
            return False
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            self.login_error.setText("❌ Erreur système lors de la connexion")
            self.set_loading_state(False)
            return False

    def set_loading_state(self, loading):
        self.is_loading = loading
        if self.login_button is not None:
            self.login_button.setEnabled(not loading)
            self.login_button.setText("Connexion…" if loading else "Se connecter")
        if self.cancel_button is not None:
            self.cancel_button.setEnabled(not loading and not self.hibernate)
        if self.password_field is not None:
            self.password_field.setEnabled(not loading)
        if self.box_username is not None:
            self.box_username.setEnabled(not loading)

    def show_reset_dialog(self):
        from .reset_password import ResetPasswordWidget

        dialog = ResetPasswordWidget(self)
        dialog.exec()
