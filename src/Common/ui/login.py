#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

import datetime

from PyQt6.QtCore import QEvent, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect,
)

from ..models import Owner
from .common import (
    EnterTabbedLineEdit,
    ErrorLabel,
    FDialog,
    FWidget,
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
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(720, 460)
        self.resize(780, 500)
        self.setStyleSheet(self._stylesheet())

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(0)

        self._card = QFrame()
        self._card.setObjectName("loginCard")
        try:
            shadow = QGraphicsDropShadowEffect(self._card)
            shadow.setBlurRadius(36)
            shadow.setOffset(0, 10)
            shadow.setColor(self.palette().color(self.palette().ColorRole.Shadow))
            self._card.setGraphicsEffect(shadow)
        except Exception:
            pass

        card_layout = QHBoxLayout(self._card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        self.create_header()
        card_layout.addWidget(self.header_widget, 5)

        self.loginUserGroupBox()
        card_layout.addWidget(self.topLeftGroupBox, 7)

        root_layout.addWidget(self._card)

        if getattr(self, "password_field", None) is not None:
            self.password_field.setFocus()
        self._refresh_user_greeting()

    @staticmethod
    def _stylesheet():
        return """
            #LoginRoot { background: transparent; }
            #loginCard {
                background-color: palette(base);
                border: 1px solid palette(midlight);
                border-radius: 16px;
            }
            #loginBrand {
                background-color: palette(highlight);
                border-top-left-radius: 16px;
                border-bottom-left-radius: 16px;
            }
            #loginBrand QLabel {
                background: transparent;
                color: palette(highlighted-text);
            }
            #loginBrandTitle {
                font-size: 22px;
                font-weight: 700;
            }
            #loginBrandMeta {
                font-size: 12px;
            }
            #loginBrandHint {
                font-size: 11px;
            }
            #loginAvatar {
                background-color: rgba(255, 255, 255, 0.16);
                border: 1px solid rgba(255, 255, 255, 0.28);
                border-radius: 40px;
                color: palette(highlighted-text);
                font-size: 26px;
                font-weight: 700;
            }
            #loginForm {
                background-color: palette(base);
                border-top-right-radius: 16px;
                border-bottom-right-radius: 16px;
            }
            #loginHello {
                font-size: 22px;
                font-weight: 700;
                color: palette(text);
            }
            #loginSub {
                font-size: 13px;
                color: palette(mid);
            }
            #loginFieldLabel {
                font-size: 12px;
                font-weight: 600;
                color: palette(text);
                padding: 0 2px;
            }
            #loginFieldWrap {
                background-color: palette(alternate-base);
                border: 1px solid palette(midlight);
                border-radius: 10px;
            }
            #loginFieldWrap[focused="true"] {
                background-color: palette(base);
                border: 1px solid palette(highlight);
            }
            #loginFieldIcon {
                color: palette(mid);
                font-size: 15px;
                padding: 0 2px 0 4px;
                min-width: 22px;
            }
            #loginForm QLineEdit,
            #loginForm QComboBox {
                border: none;
                background: transparent;
                padding: 10px 8px;
                font-size: 14px;
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
            }
            #loginForm QLineEdit:focus,
            #loginForm QComboBox:focus {
                border: none;
                background: transparent;
            }
            #loginForm QComboBox::drop-down {
                border: none;
                width: 28px;
            }
            #loginForm QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid palette(mid);
                margin-right: 10px;
            }
            #loginForm QComboBox QAbstractItemView {
                background-color: palette(base);
                border: 1px solid palette(midlight);
                border-radius: 8px;
                padding: 4px;
                outline: none;
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
            }
            #loginForm QPushButton#primaryButton {
                padding: 12px 16px;
                border-radius: 10px;
                font-size: 14px;
            }
            #loginHint {
                font-size: 11px;
                color: palette(mid);
            }
            #loginError {
                padding: 8px 10px;
                border-radius: 8px;
                background-color: palette(alternate-base);
            }
            #loginClose {
                border: none;
                border-radius: 8px;
                background: transparent;
                color: palette(mid);
                font-size: 18px;
            }
            #loginClose:hover {
                background-color: palette(alternate-base);
                color: palette(text);
            }
        """

    def eventFilter(self, watched, event):
        if watched is getattr(self, "password_field", None):
            if event.type() in (
                QEvent.Type.KeyPress,
                QEvent.Type.KeyRelease,
                QEvent.Type.FocusIn,
            ):
                self._update_capslock_warning()
        if event.type() in (QEvent.Type.FocusIn, QEvent.Type.FocusOut):
            wrap = watched.parentWidget() if watched is not None else None
            if wrap is not None and wrap.objectName() == "loginFieldWrap":
                wrap.setProperty(
                    "focused", "true" if event.type() == QEvent.Type.FocusIn else "false"
                )
                wrap.style().unpolish(wrap)
                wrap.style().polish(wrap)
        return super().eventFilter(watched, event)

    def _widget_is_interactive(self, widget):
        while widget is not None and widget is not self:
            if isinstance(widget, (QLineEdit, QComboBox, QPushButton, QToolButton)):
                return True
            widget = widget.parentWidget()
        return False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if not self._widget_is_interactive(child):
                self._drag_anchor = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_anchor is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_anchor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_anchor = None
        super().mouseReleaseEvent(event)

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

    @staticmethod
    def _initials(name):
        parts = [p for p in (name or "").split() if p]
        if not parts:
            return "GS"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    @staticmethod
    def _greeting_word():
        hour = datetime.datetime.now().hour
        if hour < 12:
            return "Bonjour"
        if hour < 18:
            return "Bon après-midi"
        return "Bonsoir"

    def create_header(self):
        self.header_widget = QFrame()
        self.header_widget.setObjectName("loginBrand")
        self.header_widget.setCursor(Qt.CursorShape.OpenHandCursor)
        layout = QVBoxLayout(self.header_widget)
        layout.setContentsMargins(28, 32, 28, 28)
        layout.setSpacing(12)

        org_info = self._get_org_info()

        logo = org_info["logo"]
        if logo and not logo.isNull():
            logo_label = QLabel()
            logo_label.setPixmap(
                logo.scaled(
                    88,
                    88,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(logo_label)
        else:
            avatar = QLabel(self._initials(org_info["name"]))
            avatar.setObjectName("loginAvatar")
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setFixedSize(80, 80)
            layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignLeft)

        title = QLabel(org_info["name"])
        title.setObjectName("loginBrandTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        app_name = getattr(CConstants, "APP_NAME", "Application")
        app_ver = getattr(CConstants, "APP_VERSION", "")
        meta = QLabel(f"{app_name}  ·  v{app_ver}" if app_ver else app_name)
        meta.setObjectName("loginBrandMeta")
        layout.addWidget(meta)

        details = []
        if org_info["address"]:
            details.append(org_info["address"])
        if org_info["phone"]:
            details.append(org_info["phone"])
        if org_info["email"]:
            details.append(org_info["email"])
        if details:
            info = QLabel("\n".join(details[:3]))
            info.setObjectName("loginBrandMeta")
            info.setWordWrap(True)
            layout.addWidget(info)

        layout.addStretch(1)

        hint = QLabel("Identifiez-vous pour accéder à votre espace.")
        hint.setObjectName("loginBrandHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

    def create_footer(self):
        self.footer_widget = QWidget()
        footer = QVBoxLayout(self.footer_widget)
        footer.setContentsMargins(0, 8, 0, 0)
        footer.setSpacing(2)

        if self.hibernate:
            text = "Session verrouillée  ·  glisser pour déplacer"
        else:
            text = "Échap pour quitter  ·  glisser pour déplacer"
        hint = QLabel(text)
        hint.setObjectName("loginHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.addWidget(hint)

        app_ver = getattr(CConstants, "APP_VERSION", "") or ""
        if app_ver:
            version = QLabel(f"Version {app_ver}")
            version.setObjectName("loginHint")
            version.setAlignment(Qt.AlignmentFlag.AlignCenter)
            footer.addWidget(version)

    def _toggle_password_visibility(self, checked: bool):
        self.password_field.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )
        self._pwd_toggle_action.setToolTip(
            "Masquer le mot de passe" if checked else "Afficher le mot de passe"
        )

    def _field_label(self, text):
        label = QLabel(text)
        label.setObjectName("loginFieldLabel")
        return label

    def _wrap_field(self, icon_text, widget):
        wrap = QFrame()
        wrap.setObjectName("loginFieldWrap")
        row = QHBoxLayout(wrap)
        row.setContentsMargins(10, 2, 6, 2)
        row.setSpacing(4)
        icon = QLabel(icon_text)
        icon.setObjectName("loginFieldIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(icon, 0)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        row.addWidget(widget, 1)
        return wrap

    def _set_error(self, text=""):
        if getattr(self, "login_error", None) is None:
            return
        self.login_error.setText(text or "")
        self.login_error.setVisible(bool(text))

    def _current_user(self):
        if self.box_username is None:
            return None
        users = list(getattr(self, "liste_username", []) or [])
        idx = self.box_username.currentIndex()
        if 0 <= idx < len(users):
            return users[idx]
        return None

    def _refresh_user_greeting(self):
        if getattr(self, "hello_label", None) is None:
            return
        user = self._current_user()
        word = self._greeting_word()
        if user is not None:
            self.hello_label.setText(f"{word}, {user.username}")
            role = user.group or "Utilisateur"
            last = ""
            if getattr(user, "login_count", 0):
                try:
                    last = user.last_login.strftime("%d/%m/%Y à %H:%M")
                except Exception:
                    last = ""
            if last:
                self.sub_label.setText(f"{role}  ·  dernière connexion {last}")
            else:
                self.sub_label.setText(f"{role}  ·  première connexion")
        else:
            self.hello_label.setText(word)
            self.sub_label.setText("Veuillez vous identifier")

    def loginUserGroupBox(self):
        self.topLeftGroupBox = QFrame()
        self.topLeftGroupBox.setObjectName("loginForm")
        form = QVBoxLayout(self.topLeftGroupBox)
        form.setContentsMargins(32, 22, 32, 24)
        form.setSpacing(10)

        chrome = QHBoxLayout()
        chrome.addStretch(1)
        self.close_btn = QToolButton()
        self.close_btn.setObjectName("loginClose")
        self.close_btn.setText("×")
        self.close_btn.setToolTip("Fermer")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.cancel)
        if self.hibernate:
            self.close_btn.setEnabled(False)
            self.close_btn.setToolTip("Fermeture désactivée (session verrouillée)")
        chrome.addWidget(self.close_btn, 0, Qt.AlignmentFlag.AlignRight)
        form.addLayout(chrome)

        self.hello_label = QLabel(self._greeting_word())
        self.hello_label.setObjectName("loginHello")
        self.hello_label.setWordWrap(True)
        form.addWidget(self.hello_label)

        self.sub_label = QLabel("Veuillez vous identifier")
        self.sub_label.setObjectName("loginSub")
        self.sub_label.setWordWrap(True)
        form.addWidget(self.sub_label)
        form.addSpacing(8)

        try:
            self.liste_username = Owner.get_active_non_superusers().order_by(
                Owner.last_login.desc()
            )
        except Exception:
            self.liste_username = Owner.get_active_non_superusers()

        if not self.liste_username.exists():
            print("❌ Erreur: Aucun utilisateur actif trouvé")
            self._no_users = True
            empty = QLabel(
                "Aucun compte utilisateur actif.\n"
                "Configurez la base ou restaurez une sauvegarde, puis relancez."
            )
            empty.setObjectName("loginSub")
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            form.addStretch(1)
            form.addWidget(empty)
            close_b = QPushButton("Fermer")
            close_b.clicked.connect(self.cancel)
            form.addWidget(close_b)
            form.addStretch(1)
            self.login_error = ErrorLabel("")
            self.login_error.setObjectName("loginError")
            self.login_error.setVisible(False)
            self.box_username = None
            self.password_field = None
            self.login_button = None
            self.cancel_button = None
            self.reset_button = None
            self.create_footer()
            form.addWidget(self.footer_widget)
            return

        form.addWidget(self._field_label("Utilisateur"))
        self.box_username = QComboBox()
        self.box_username.setObjectName("loginInput")
        self.box_username.setToolTip("Compte utilisateur")
        self.box_username.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        for owner in self.liste_username:
            badge = "Admin" if owner.group == Owner.ADMIN else "Utilisateur"
            self.box_username.addItem(f"{owner.username}  ·  {badge}")
        self.box_username.currentIndexChanged.connect(self._refresh_user_greeting)
        self.box_username.installEventFilter(self)
        self.username_field = self.box_username
        form.addWidget(self._wrap_field("👤", self.box_username))

        form.addSpacing(4)
        form.addWidget(self._field_label("Mot de passe"))
        self.password_field = EnterTabbedLineEdit()
        self.password_field.setObjectName("loginInput")
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("Saisissez votre mot de passe")
        self.password_field.setToolTip("Mot de passe du compte sélectionné")
        self.password_field.setAccessibleName("Mot de passe")
        self.password_field.setFrame(False)
        self.password_field.returnPressed.connect(self.login)
        self.password_field.installEventFilter(self)

        self._pwd_toggle_action = QAction("👁", self.password_field)
        self._pwd_toggle_action.setCheckable(True)
        self._pwd_toggle_action.setToolTip("Afficher le mot de passe")
        self._pwd_toggle_action.toggled.connect(self._toggle_password_visibility)
        self.password_field.addAction(
            self._pwd_toggle_action, QLineEdit.ActionPosition.TrailingPosition
        )
        form.addWidget(self._wrap_field("🔒", self.password_field))

        self.capslock_warning = QLabel("")
        self.capslock_warning.setObjectName("loginHint")
        self.capslock_warning.setVisible(False)
        form.addWidget(self.capslock_warning)

        self.login_error = ErrorLabel("")
        self.login_error.setObjectName("loginError")
        self.login_error.setWordWrap(True)
        self.login_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_error.setVisible(False)
        form.addWidget(self.login_error)

        form.addSpacing(6)
        self.login_button = QPushButton("Se connecter")
        self.login_button.setObjectName("primaryButton")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setToolTip("Valider (Entrée)")
        self.login_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.login_button.clicked.connect(self.login)
        self.login_button.setDefault(True)
        form.addWidget(self.login_button)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        self.reset_button = QPushButton("Mot de passe oublié ?")
        self.reset_button.setObjectName("linkButton")
        self.reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_button.setToolTip(
            "Réinitialiser le mot de passe : choisir le compte, noter le code, "
            "puis définir un nouveau mot de passe"
        )
        self.reset_button.clicked.connect(self.show_reset_dialog)
        actions.addWidget(self.reset_button)

        actions.addStretch(1)
        self.cancel_button = QPushButton("Quitter")
        self.cancel_button.setObjectName("linkButton")
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.setToolTip("Fermer l’application (Échap)")
        self.cancel_button.clicked.connect(self.cancel)
        if self.hibernate:
            self.cancel_button.setEnabled(False)
            self.cancel_button.setToolTip("Fermeture désactivée (session verrouillée)")
        actions.addWidget(self.cancel_button)
        form.addLayout(actions)

        form.addStretch(1)
        self.create_footer()
        form.addWidget(self.footer_widget)

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
        self.capslock_warning.setText("Verr. Maj activée" if caps_on else "")
        self.capslock_warning.setVisible(caps_on)

    def login(self):
        if self._no_users or self.login_button is None:
            return
        if self.is_loading:
            return

        self._set_error("")
        self._update_capslock_warning()
        if not self.is_valide():
            self._set_error("Saisissez votre mot de passe")
            field_error(self.password_field, "Mot de passe requis")
            return

        users_list = list(self.liste_username)
        current_index = self.box_username.currentIndex()
        if current_index < 0 or current_index >= len(users_list):
            self._set_error("Utilisateur invalide")
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
                self._set_error(
                    f"Compte temporairement bloqué\nRéessayez dans {minutes} min {seconds} s"
                )
                self.set_loading_state(False)
                return False

            if not owner.verify_password(password):
                owner.increment_login_attempts()
                if not owner.check_login_attempts():
                    remaining_time = owner.get_remaining_lockout_time()
                    minutes = int(remaining_time / 60)
                    seconds = int(remaining_time % 60)
                    self._set_error(
                        f"Trop de tentatives\nCompte bloqué {minutes} min {seconds} s"
                    )
                else:
                    remaining = owner.MAX_LOGIN_ATTEMPTS - owner.login_attempts
                    self._set_error(
                        f"Mot de passe incorrect\nEncore {remaining} tentative(s)"
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
            self._set_error("Utilisateur ou mot de passe incorrect")
            field_error(self.password_field, "Vérifiez vos identifiants")
            self.password_field.clear()
            self.password_field.setFocus()
            self.set_loading_state(False)
            return False
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            self._set_error("Erreur système lors de la connexion")
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
        if getattr(self, "reset_button", None) is not None:
            self.reset_button.setEnabled(not loading)

    def show_reset_dialog(self):
        from .reset_password import ResetPasswordWidget

        preselect = ""
        try:
            users_list = list(self.liste_username)
            idx = self.box_username.currentIndex() if self.box_username else -1
            if 0 <= idx < len(users_list):
                preselect = str(users_list[idx].username)
        except Exception:
            preselect = ""

        dialog = ResetPasswordWidget(self, preselect_username=preselect)
        if dialog.exec() and preselect and self.password_field is not None:
            self.password_field.clear()
            self.password_field.setFocus()
            self._set_error("")
