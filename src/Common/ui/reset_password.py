#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

"""Flux « mot de passe oublié » : assistant en 2 étapes (compte → code + nouveau MDP)."""

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QFont, QGuiApplication
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
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

class ResetPasswordWidget(FDialog, FWidget):
    """Assistant : 1) choisir le compte  2) code + nouveau mot de passe."""

    title_page = "Mot de passe oublié"

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.setModal(True)
        self.setWindowTitle(self.title_page)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setMinimumSize(460, 520)
        self.resize(500, 560)
        self._drag_anchor = None
        self.owner = None
        self._token = ""

        self.setObjectName("ResetPwdRoot")
        self.setStyleSheet(
            """
            #ResetPwdRoot { background-color: palette(alternate-base); }
            #ResetPwdCard {
                background-color: palette(base);
                border: 1px solid palette(midlight);
                border-radius: 12px;
            }
            #StepHint {
                color: palette(mid);
                font-size: 11px;
            }
            #CodeDisplay {
                font-family: 'Menlo', 'Consolas', monospace;
                font-size: 28px;
                font-weight: 700;
                letter-spacing: 6px;
                padding: 14px;
                background: palette(alternate-base);
                border: 1px dashed palette(mid);
                border-radius: 8px;
            }
            QPushButton#linkBtn {
                border: none;
                background: transparent;
                color: palette(highlight);
                text-decoration: underline;
                padding: 2px 6px;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        card = QFrame()
        card.setObjectName("ResetPwdCard")
        cv = QVBoxLayout(card)
        cv.setContentsMargins(22, 18, 22, 18)
        cv.setSpacing(12)

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
        hl.setContentsMargins(0, 4, 0, 4)
        self.title_label = QLabel("Mot de passe oublié")
        tf = QFont()
        tf.setPointSize(18)
        tf.setBold(True)
        self.title_label.setFont(tf)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_label = QLabel("Étape 1 sur 2 — Choisir le compte")
        self.step_label.setObjectName("StepHint")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(self.title_label)
        hl.addWidget(self.step_label)
        cv.addWidget(self.header)
        self.header.installEventFilter(self)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_step_account())
        self.stack.addWidget(self._build_step_password())
        cv.addWidget(self.stack, 1)

        root.addWidget(card)
        self._fill_users_combo()

    # —— Construction des étapes ——

    def _build_step_account(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 8, 0, 0)

        hint = QLabel(
            "Sélectionnez le compte à débloquer. Un code à 6 chiffres "
            "valable 1 heure sera généré pour confirmer le changement."
        )
        hint.setWordWrap(True)
        hint.setObjectName("StepHint")
        layout.addWidget(hint)

        form = QFormLayout()
        form.setSpacing(10)
        self.box_username = QComboBox()
        form.addRow(FormLabel("Compte"), self.box_username)
        layout.addLayout(form)

        self.error_step1 = ErrorLabel("")
        self.error_step1.setWordWrap(True)
        layout.addWidget(self.error_step1)

        layout.addStretch(1)

        row = QHBoxLayout()
        cancel = Button("Annuler")
        cancel.clicked.connect(self.reject)
        cont = Button("Continuer")
        cont.setDefault(True)
        cont.clicked.connect(self._go_step_password)
        self.btn_continue = cont
        row.addWidget(cancel)
        row.addWidget(cont)
        layout.addLayout(row)
        return page

    def _build_step_password(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 8, 0, 0)

        self.account_banner = QLabel("")
        self.account_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.account_banner.setStyleSheet("font-weight: 600;")
        layout.addWidget(self.account_banner)

        code_hint = QLabel("Votre code de confirmation (valable 1 heure) :")
        code_hint.setObjectName("StepHint")
        layout.addWidget(code_hint)

        code_row = QHBoxLayout()
        self.code_display = QLabel("")
        self.code_display.setObjectName("CodeDisplay")
        self.code_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.code_display.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        code_row.addWidget(self.code_display, 1)
        self.copy_btn = QPushButton("Copier")
        self.copy_btn.setObjectName("linkBtn")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy_code)
        code_row.addWidget(self.copy_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(code_row)

        self.expiry_label = QLabel("")
        self.expiry_label.setObjectName("StepHint")
        self.expiry_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.expiry_label)

        # Saisie manuelle du code (modifiable si recopié ailleurs)
        form = QFormLayout()
        form.setSpacing(8)
        self.token_field = LineEdit()
        self.token_field.setPlaceholderText("Saisir ou coller le code")
        self.token_field.setMaxLength(8)
        self.token_field.setStyleSheet("QLineEdit { font-family: monospace; letter-spacing: 2px; }")
        form.addRow(FormLabel("Code"), self.token_field)

        self.password_field = EnterTabbedLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("Nouveau mot de passe")
        form.addRow(FormLabel("Mot de passe"), self.password_field)

        self.confirm_field = EnterTabbedLineEdit()
        self.confirm_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_field.setPlaceholderText("Confirmer le mot de passe")
        self.confirm_field.returnPressed.connect(self._save_password)
        form.addRow(FormLabel("Confirmer"), self.confirm_field)

        self.show_pwd = QCheckBox("Afficher les mots de passe")
        self.show_pwd.toggled.connect(self._toggle_echo)
        form.addRow(FormLabel(""), self.show_pwd)

        layout.addLayout(form)

        self.error_step2 = ErrorLabel("")
        self.error_step2.setWordWrap(True)
        layout.addWidget(self.error_step2)

        layout.addStretch(1)

        row = QHBoxLayout()
        back = Button("Retour")
        back.clicked.connect(self._go_step_account)
        save = Button("Enregistrer")
        save.setDefault(True)
        save.clicked.connect(self._save_password)
        self.btn_save = save
        row.addWidget(back)
        row.addWidget(save)
        layout.addLayout(row)
        return page

    # —— Navigation ——

    def _fill_users_combo(self):
        self.box_username.clear()
        qs = Owner.get_active_non_superusers()
        if not qs.exists():
            self.box_username.addItem("— Aucun compte éligible —")
            self.box_username.setEnabled(False)
            self.btn_continue.setEnabled(False)
            self.error_step1.setText(
                "Aucun compte actif disponible. Contactez un administrateur."
            )
            return
        for o in qs.order_by(Owner.username):
            role = "Admin" if o.group == Owner.ADMIN else "Utilisateur"
            self.box_username.addItem(f"{o.username}  ({role})", o.id)

    def _go_step_account(self):
        self.stack.setCurrentIndex(0)
        self.step_label.setText("Étape 1 sur 2 — Choisir le compte")
        self.error_step1.setText("")

    def _go_step_password(self):
        self.error_step1.setText("")
        if not self.box_username.isEnabled() or self.box_username.count() == 0:
            self.error_step1.setText("Aucun utilisateur disponible.")
            return
        oid = self.box_username.currentData()
        if oid is None:
            self.error_step1.setText("Sélectionnez un utilisateur.")
            return
        try:
            owner = Owner.get(Owner.id == oid)
        except Owner.DoesNotExist:
            self.error_step1.setText("Compte introuvable.")
            return
        if not owner.isactive:
            self.error_step1.setText(
                "Ce compte est désactivé. Contactez un administrateur."
            )
            return

        try:
            token = owner.generate_reset_token(digits=6)
        except Exception as e:
            self.error_step1.setText(f"Impossible de générer le code : {e}")
            return

        self.owner = owner
        self._token = token
        self.account_banner.setText(f"Compte : {owner.username}")
        self.code_display.setText(token)
        self.token_field.setText(token)
        mins = owner.reset_token_remaining_minutes()
        self.expiry_label.setText(f"Expire dans environ {mins} min")
        self.password_field.clear()
        self.confirm_field.clear()
        self.error_step2.setText("")
        self.stack.setCurrentIndex(1)
        self.step_label.setText("Étape 2 sur 2 — Code et nouveau mot de passe")
        self.password_field.setFocus()

    def _copy_code(self):
        code = (self.code_display.text() or self._token or "").strip()
        if not code:
            return
        QGuiApplication.clipboard().setText(code)
        self.copy_btn.setText("Copié ✓")
        self.token_field.setText(code)

    def _toggle_echo(self, checked):
        mode = (
            QLineEdit.EchoMode.Normal
            if checked
            else QLineEdit.EchoMode.Password
        )
        self.password_field.setEchoMode(mode)
        self.confirm_field.setEchoMode(mode)

    def _save_password(self):
        self.error_step2.setText("")
        if self.owner is None:
            self.error_step2.setText("Compte manquant. Revenez à l'étape 1.")
            return

        # Recharger depuis la DB (token / expiry à jour)
        try:
            self.owner = Owner.get(Owner.id == self.owner.id)
        except Owner.DoesNotExist:
            self.error_step2.setText("Compte introuvable.")
            return

        password = self.password_field.text().strip()
        confirm = self.confirm_field.text().strip()
        token = (self.token_field.text() or self._token).strip()

        if not token:
            self.error_step2.setText("Saisissez le code de confirmation.")
            self.token_field.setFocus()
            return
        if not password:
            self.error_step2.setText("Saisissez un mot de passe.")
            self.password_field.setFocus()
            return
        if not confirm:
            self.error_step2.setText("Confirmez le mot de passe.")
            self.confirm_field.setFocus()
            return
        if password != confirm:
            self.error_step2.setText("Les deux mots de passe ne correspondent pas.")
            self.confirm_field.setFocus()
            return

        ok_rules, msg_rules = Owner.validate_password(password)
        if not ok_rules:
            self.error_step2.setText(msg_rules)
            self.password_field.setFocus()
            return

        if not self.owner.verify_reset_token(token):
            self.error_step2.setText(
                "Code invalide ou expiré. Revenez à l'étape 1 pour en générer un nouveau."
            )
            return

        success, message = self.owner.reset_password(password)
        if not success:
            self.error_step2.setText(message)
            return

        QMessageBox.information(
            self,
            "Mot de passe mis à jour",
            f"Le mot de passe de « {self.owner.username} » a été modifié.\n"
            "Vous pouvez vous connecter avec le nouveau mot de passe.",
        )
        self.accept()

    # —— Fenêtre (drag / Escape) ——

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
            if self.stack.currentIndex() > 0:
                self._go_step_account()
            else:
                self.reject()
            event.accept()
            return
        super().keyPressEvent(event)


# Alias conservé pour d'éventuels imports anciens
class ResetPasswordDialog(ResetPasswordWidget):
    """Compatibilité : ancien nom de la boîte de dialogue."""

    def __init__(self, owner=None, token=None, parent=None):
        super().__init__(parent=parent)
        if owner is not None and token:
            self.owner = owner
            self._token = str(token).strip()
            self.account_banner.setText(f"Compte : {owner.username}")
            self.code_display.setText(self._token)
            self.token_field.setText(self._token)
            self.stack.setCurrentIndex(1)
            self.step_label.setText("Étape 2 sur 2 — Code et nouveau mot de passe")
