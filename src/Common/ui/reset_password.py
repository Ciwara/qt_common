#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

"""Flux « mot de passe oublié » : choix du compte, code à usage limité, nouveau mot de passe."""

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

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

_PASSWORD_RULES = (
    "Le mot de passe doit contenir : au moins 8 caractères, une majuscule, "
    "une minuscule, un chiffre et un caractère spécial (!@#$%…)."
)


class ResetPasswordWidget(FDialog, FWidget):
    """Étape 1 : choisir un compte actif, générer un code, puis saisir le nouveau mot de passe."""

    title_page = "Mot de passe oublié"

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.setModal(True)
        self.setWindowTitle(self.title_page)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
        )
        self.setMinimumSize(420, 480)
        self.resize(460, 520)
        self._drag_anchor = None

        self.setStyleSheet(
            """
            #ResetPwdRoot {
                background-color: palette(alternate-base);
            }
            #ResetPwdCard {
                background-color: palette(base);
                border: 1px solid palette(midlight);
                border-radius: 12px;
            }
            """
        )
        self.setObjectName("ResetPwdRoot")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        card = QFrame()
        card.setObjectName("ResetPwdCard")
        cv = QVBoxLayout(card)
        cv.setContentsMargins(20, 18, 20, 18)
        cv.setSpacing(14)

        accent = QFrame()
        accent.setFixedHeight(3)
        accent.setStyleSheet(
            "QFrame { background-color: palette(highlight); border: none; "
            "border-top-left-radius: 11px; border-top-right-radius: 11px; }"
        )
        cv.addWidget(accent)

        self.header = QWidget()
        self.header.setCursor(Qt.CursorShape.OpenHandCursor)
        hl = QVBoxLayout(self.header)
        hl.setContentsMargins(0, 4, 0, 8)
        title = QLabel("Mot de passe oublié")
        tf = QFont()
        tf.setPointSize(18)
        tf.setBold(True)
        title.setFont(tf)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub = QLabel(
            "Sélectionnez votre compte. Un code valide 1 h sera affiché, "
            "puis vous choisirez un nouveau mot de passe."
        )
        sub.setWordWrap(True)
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color: palette(mid); font-size: 11px;")
        hl.addWidget(title)
        hl.addWidget(sub)
        cv.addWidget(self.header)
        self.header.installEventFilter(self)

        self.main_group = QGroupBox("Étape 1 — Compte")
        self.main_group.setStyleSheet(
            "QGroupBox { font-weight: 600; margin-top: 8px; }"
        )
        formbox = QFormLayout()
        formbox.setSpacing(12)
        formbox.setHorizontalSpacing(10)

        self.box_username = QComboBox()
        self.box_username.setMinimumHeight(40)

        formbox.addRow(FormLabel("Utilisateur"), self.box_username)

        self.error_label = ErrorLabel("")
        self.error_label.setWordWrap(True)
        formbox.addRow(FormLabel(""), self.error_label)

        row_btn = QHBoxLayout()
        self.cancel_button = Button("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        self.reset_button = Button("Continuer")
        self.reset_button.setDefault(True)
        self.reset_button.clicked.connect(self.start_reset)
        row_btn.addWidget(self.cancel_button)
        row_btn.addWidget(self.reset_button)
        formbox.addRow(FormLabel(""), row_btn)

        self._fill_users_combo()

        self.main_group.setLayout(formbox)
        cv.addWidget(self.main_group)
        root.addWidget(card)

    def eventFilter(self, watched, event):
        if watched is self.header:
            et = event.type()
            if et == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self._drag_anchor = (
                        event.globalPosition().toPoint()
                        - self.frameGeometry().topLeft()
                    )
            elif et == QEvent.Type.MouseMove:
                if (
                    self._drag_anchor is not None
                    and event.buttons() & Qt.MouseButton.LeftButton
                ):
                    self.move(
                        event.globalPosition().toPoint() - self._drag_anchor
                    )
            elif et == QEvent.Type.MouseButtonRelease:
                self._drag_anchor = None
        return super().eventFilter(watched, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)

    def _fill_users_combo(self):
        self.box_username.clear()
        qs = Owner.get_active_non_superusers()
        if not qs.exists():
            self.box_username.addItem("— Aucun compte éligible —")
            self.box_username.setEnabled(False)
            self.reset_button.setEnabled(False)
            return
        for o in qs.order_by(Owner.username):
            role = "Admin" if o.group == Owner.ADMIN else "Utilisateur"
            self.box_username.addItem(f"{o.username}  ({role})", o.id)

    def start_reset(self):
        self.error_label.setText("")
        if self.box_username.count() == 0 or not self.box_username.isEnabled():
            self.error_label.setText("❌ Aucun utilisateur disponible pour la réinitialisation.")
            return

        oid = self.box_username.currentData()
        if oid is None:
            self.error_label.setText("❌ Sélectionnez un utilisateur.")
            return

        try:
            owner = Owner.get(Owner.id == oid)
        except Owner.DoesNotExist:
            self.error_label.setText("❌ Compte introuvable.")
            return

        if not owner.isactive:
            self.error_label.setText("❌ Ce compte est désactivé. Contactez un administrateur.")
            return

        try:
            token = owner.generate_reset_token()
        except Exception as e:
            self.error_label.setText(f"❌ Impossible de générer le code : {e}")
            return

        QMessageBox.information(
            self,
            "Code de réinitialisation",
            "Conservez ce code : il est valable une heure.\n\n"
            f"{token}\n\n"
            "La fenêtre suivante le reprendra automatiquement ; "
            "saisissez votre nouveau mot de passe.",
        )

        dialog = ResetPasswordDialog(owner, token, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.accept()

    def reject(self):
        super().reject()


class ResetPasswordDialog(QDialog, FWidget):
    """Étape 2 : code (prérempli) + nouveau mot de passe + confirmation."""

    def __init__(self, owner, token, parent=None):
        super().__init__(parent)
        self.owner = owner
        self._token = (token or "").strip()

        self.setModal(True)
        self.setWindowTitle("Nouveau mot de passe")
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
        )
        self.setMinimumSize(400, 420)
        self.resize(440, 460)
        self._drag_anchor = None
        self.setObjectName("ResetPwdRoot")
        self.setStyleSheet(
            """
            #ResetPwdRoot {
                background-color: palette(alternate-base);
            }
            #ResetPwdCard2 {
                background-color: palette(base);
                border: 1px solid palette(midlight);
                border-radius: 12px;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setObjectName("ResetPwdCard2")
        cv = QVBoxLayout(card)
        cv.setContentsMargins(18, 16, 18, 16)
        cv.setSpacing(12)

        self.header = QWidget()
        self.header.setCursor(Qt.CursorShape.OpenHandCursor)
        hl = QVBoxLayout(self.header)
        t = QLabel("Nouveau mot de passe")
        tf = QFont()
        tf.setPointSize(16)
        tf.setBold(True)
        t.setFont(tf)
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(t)
        cv.addWidget(self.header)
        self.header.installEventFilter(self)

        self.main_group = QGroupBox(f"Compte : {owner.username}")
        formbox = QFormLayout()
        formbox.setSpacing(10)

        self.token_field = LineEdit()
        self.token_field.setReadOnly(True)
        self.token_field.setText(self._token)
        self.token_field.setPlaceholderText("Code")
        self.token_field.setStyleSheet("QLineEdit { font-family: monospace; }")
        formbox.addRow(FormLabel("Code"), self.token_field)

        rules = QLabel(_PASSWORD_RULES)
        rules.setWordWrap(True)
        rules.setStyleSheet(
            "color: palette(mid); font-size: 10px; padding: 4px 0;"
        )
        formbox.addRow(FormLabel(""), rules)

        self.password_field = EnterTabbedLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("Nouveau mot de passe")
        formbox.addRow(FormLabel("Mot de passe"), self.password_field)

        self.confirm_field = EnterTabbedLineEdit()
        self.confirm_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_field.setPlaceholderText("Confirmation")
        self.confirm_field.returnPressed.connect(self.save_password)
        formbox.addRow(FormLabel("Confirmer"), self.confirm_field)

        self.error_label = ErrorLabel("")
        self.error_label.setWordWrap(True)
        formbox.addRow(FormLabel(""), self.error_label)

        row_btn = QHBoxLayout()
        self.cancel_button = Button("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        self.save_button = Button("Enregistrer")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.save_password)
        row_btn.addWidget(self.cancel_button)
        row_btn.addWidget(self.save_button)
        formbox.addRow(FormLabel(""), row_btn)

        self.main_group.setLayout(formbox)
        cv.addWidget(self.main_group)
        root.addWidget(card)

        self.password_field.setFocus()

    def eventFilter(self, watched, event):
        if watched is self.header:
            et = event.type()
            if et == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self._drag_anchor = (
                        event.globalPosition().toPoint()
                        - self.frameGeometry().topLeft()
                    )
            elif et == QEvent.Type.MouseMove:
                if (
                    self._drag_anchor is not None
                    and event.buttons() & Qt.MouseButton.LeftButton
                ):
                    self.move(
                        event.globalPosition().toPoint() - self._drag_anchor
                    )
            elif et == QEvent.Type.MouseButtonRelease:
                self._drag_anchor = None
        return super().eventFilter(watched, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)

    def save_password(self):
        self.error_label.setText("")
        password = self.password_field.text().strip()
        confirm = self.confirm_field.text().strip()
        token = (self.token_field.text() or self._token).strip()

        if not token:
            self.error_label.setText("❌ Code manquant.")
            return
        if not password:
            self.error_label.setText("❌ Saisissez un mot de passe.")
            return
        if not confirm:
            self.error_label.setText("❌ Confirmez le mot de passe.")
            return
        if password != confirm:
            self.error_label.setText("❌ Les deux mots de passe ne correspondent pas.")
            return

        ok_rules, msg_rules = Owner.validate_password(password)
        if not ok_rules:
            self.error_label.setText(f"❌ {msg_rules}")
            return

        if not self.owner.verify_reset_token(token):
            self.error_label.setText(
                "❌ Code invalide ou expiré. Recommencez depuis « Mot de passe oublié »."
            )
            return

        success, message = self.owner.reset_password(password)
        if not success:
            self.error_label.setText(f"❌ {message}")
            return

        QMessageBox.information(
            self,
            "Mot de passe mis à jour",
            "Vous pouvez vous connecter avec votre nouveau mot de passe.",
        )
        self.accept()
