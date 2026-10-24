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
    """Assistant clair : 1) choisir le compte  2) noter le code + nouveau MDP."""

    title_page = "Mot de passe oublié"

    def __init__(self, parent=None, preselect_username=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.setModal(True)
        self.setWindowTitle(self.title_page)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setMinimumSize(480, 560)
        self.resize(520, 600)
        self._drag_anchor = None
        self.owner = None
        self._token = ""
        self._preselect_username = (preselect_username or "").strip()

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
                font-size: 12px;
            }
            #InfoBox {
                background-color: palette(alternate-base);
                border: 1px solid palette(midlight);
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
            }
            #CodeDisplay {
                font-family: 'Menlo', 'Consolas', monospace;
                font-size: 28px;
                font-weight: 700;
                letter-spacing: 6px;
                padding: 14px;
                background: palette(alternate-base);
                border: 2px solid palette(highlight);
                border-radius: 8px;
            }
            #StepPill {
                padding: 4px 10px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
            }
            #StepPillActive {
                background-color: palette(highlight);
                color: palette(highlighted-text);
                padding: 4px 10px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
            }
            #StepPillDone {
                background-color: palette(midlight);
                padding: 4px 10px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
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
        self.title_label = QLabel("Réinitialiser mon mot de passe")
        tf = QFont()
        tf.setPointSize(17)
        tf.setBold(True)
        self.title_label.setFont(tf)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(self.title_label)

        self.progress_row = QHBoxLayout()
        self.progress_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pill1 = QLabel("1 · Compte")
        self.pill1.setObjectName("StepPillActive")
        self.pill2 = QLabel("2 · Nouveau mot de passe")
        self.pill2.setObjectName("StepPill")
        self.progress_row.addWidget(self.pill1)
        self.progress_row.addSpacing(8)
        self.progress_row.addWidget(self.pill2)
        hl.addLayout(self.progress_row)

        self.step_label = QLabel("")
        self.step_label.setObjectName("StepHint")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_label.setWordWrap(True)
        hl.addWidget(self.step_label)
        cv.addWidget(self.header)
        self.header.installEventFilter(self)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_step_account())
        self.stack.addWidget(self._build_step_password())
        cv.addWidget(self.stack, 1)

        root.addWidget(card)
        self._fill_users_combo()
        self._set_progress(0)

    def _set_progress(self, step_index):
        if step_index <= 0:
            self.pill1.setObjectName("StepPillActive")
            self.pill2.setObjectName("StepPill")
            self.step_label.setText(
                "Étape 1 sur 2 — Choisissez le compte dont le mot de passe est oublié."
            )
        else:
            self.pill1.setObjectName("StepPillDone")
            self.pill2.setObjectName("StepPillActive")
            self.step_label.setText(
                "Étape 2 sur 2 — Notez le code, puis définissez un nouveau mot de passe."
            )
        # Rafraîchir le style des pastilles
        for pill in (self.pill1, self.pill2):
            pill.style().unpolish(pill)
            pill.style().polish(pill)

    def _build_step_account(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 8, 0, 0)

        info = QLabel(
            "<b>Comment ça marche ?</b><br/>"
            "1. Sélectionnez votre compte<br/>"
            "2. Un code à 6 chiffres s’affiche (valable 1 heure)<br/>"
            "3. Vous recopiez ce code et choisissez un nouveau mot de passe<br/><br/>"
            "<i>Astuce :</i> un administrateur peut aussi changer un mot de passe "
            "depuis <b>Paramètres → Administration → Utilisateurs</b>."
        )
        info.setWordWrap(True)
        info.setObjectName("InfoBox")
        info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info)

        form = QFormLayout()
        form.setSpacing(10)
        self.box_username = QComboBox()
        self.box_username.setToolTip("Compte à débloquer")
        form.addRow(FormLabel("Votre compte"), self.box_username)
        layout.addLayout(form)

        self.error_step1 = ErrorLabel("")
        self.error_step1.setWordWrap(True)
        layout.addWidget(self.error_step1)

        layout.addStretch(1)

        row = QHBoxLayout()
        cancel = Button("Annuler")
        cancel.setToolTip("Fermer sans modifier le mot de passe")
        cancel.clicked.connect(self.reject)
        cont = Button("Continuer →")
        cont.setDefault(True)
        cont.setToolTip("Générer un code de confirmation pour ce compte")
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
        self.account_banner.setStyleSheet("font-weight: 600; font-size: 13px;")
        layout.addWidget(self.account_banner)

        howto = QLabel(
            "<b>À faire maintenant :</b><br/>"
            "① Notez ou copiez le code ci-dessous<br/>"
            "② Recopiez-le dans le champ « Code »<br/>"
            "③ Saisissez deux fois votre nouveau mot de passe<br/>"
            "④ Cliquez sur « Enregistrer le mot de passe »"
        )
        howto.setWordWrap(True)
        howto.setObjectName("InfoBox")
        howto.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(howto)

        code_hint = QLabel("Code de confirmation (valable 1 heure)")
        code_hint.setObjectName("StepHint")
        layout.addWidget(code_hint)

        code_row = QHBoxLayout()
        self.code_display = QLabel("")
        self.code_display.setObjectName("CodeDisplay")
        self.code_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.code_display.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.code_display.setToolTip("Code à recopier dans le champ ci-dessous")
        code_row.addWidget(self.code_display, 1)
        self.copy_btn = QPushButton("Copier")
        self.copy_btn.setObjectName("linkBtn")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.setToolTip("Copier le code dans le presse-papiers")
        self.copy_btn.clicked.connect(self._copy_code)
        code_row.addWidget(self.copy_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(code_row)

        self.expiry_label = QLabel("")
        self.expiry_label.setObjectName("StepHint")
        self.expiry_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.expiry_label)

        form = QFormLayout()
        form.setSpacing(8)
        self.token_field = LineEdit()
        self.token_field.setPlaceholderText("Recopiez le code affiché ci-dessus")
        self.token_field.setMaxLength(8)
        self.token_field.setToolTip("Saisissez exactement le code à 6 chiffres")
        self.token_field.setStyleSheet(
            "QLineEdit { font-family: monospace; letter-spacing: 2px; }"
        )
        form.addRow(FormLabel("Code *"), self.token_field)

        self.password_field = EnterTabbedLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("Nouveau mot de passe")
        self.password_field.setToolTip("Choisissez un mot de passe que vous retiendrez")
        form.addRow(FormLabel("Nouveau mot de passe *"), self.password_field)

        self.confirm_field = EnterTabbedLineEdit()
        self.confirm_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_field.setPlaceholderText("Retapez le même mot de passe")
        self.confirm_field.setToolTip("Doit être identique au champ précédent")
        self.confirm_field.returnPressed.connect(self._save_password)
        form.addRow(FormLabel("Confirmation *"), self.confirm_field)

        self.show_pwd = QCheckBox("Afficher les mots de passe")
        self.show_pwd.toggled.connect(self._toggle_echo)
        form.addRow(FormLabel(""), self.show_pwd)

        layout.addLayout(form)

        self.error_step2 = ErrorLabel("")
        self.error_step2.setWordWrap(True)
        layout.addWidget(self.error_step2)

        layout.addStretch(1)

        row = QHBoxLayout()
        back = Button("← Retour")
        back.setToolTip("Changer de compte (un nouveau code sera généré)")
        back.clicked.connect(self._go_step_account)
        save = Button("Enregistrer le mot de passe")
        save.setDefault(True)
        save.setToolTip("Valider le code et enregistrer le nouveau mot de passe")
        save.clicked.connect(self._save_password)
        self.btn_save = save
        row.addWidget(back)
        row.addWidget(save)
        layout.addLayout(row)
        return page

    def _fill_users_combo(self):
        self.box_username.clear()
        qs = Owner.get_active_non_superusers()
        if not qs.exists():
            self.box_username.addItem("— Aucun compte éligible —")
            self.box_username.setEnabled(False)
            self.btn_continue.setEnabled(False)
            self.error_step1.setText(
                "Aucun compte actif disponible. Demandez à un administrateur "
                "de créer un utilisateur ou de réinitialiser le mot de passe."
            )
            return
        selected = 0
        for i, o in enumerate(qs.order_by(Owner.username)):
            role = "Administrateur" if o.group == Owner.ADMIN else "Utilisateur"
            self.box_username.addItem(f"{o.username}  —  {role}", o.id)
            if self._preselect_username and o.username == self._preselect_username:
                selected = i
        self.box_username.setCurrentIndex(selected)

    def _go_step_account(self):
        self.stack.setCurrentIndex(0)
        self._set_progress(0)
        self.error_step1.setText("")
        self.copy_btn.setText("Copier")

    def _go_step_password(self):
        self.error_step1.setText("")
        if not self.box_username.isEnabled() or self.box_username.count() == 0:
            self.error_step1.setText("Aucun utilisateur disponible.")
            return
        oid = self.box_username.currentData()
        if oid is None:
            self.error_step1.setText("Sélectionnez un compte dans la liste.")
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
        self.account_banner.setText(f"Compte sélectionné : {owner.username}")
        self.code_display.setText(token)
        # Ne pas préremplir : l'utilisateur doit recopier le code (plus clair).
        self.token_field.clear()
        mins = owner.reset_token_remaining_minutes()
        self.expiry_label.setText(
            f"Ce code expire dans environ {mins} minute(s)."
        )
        self.password_field.clear()
        self.confirm_field.clear()
        self.error_step2.setText("")
        self.copy_btn.setText("Copier")
        self.stack.setCurrentIndex(1)
        self._set_progress(1)
        self.token_field.setFocus()

    def _copy_code(self):
        code = (self.code_display.text() or self._token or "").strip()
        if not code:
            return
        QGuiApplication.clipboard().setText(code)
        self.token_field.setText(code)
        self.copy_btn.setText("Copié ✓")
        self.password_field.setFocus()

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

        try:
            self.owner = Owner.get(Owner.id == self.owner.id)
        except Owner.DoesNotExist:
            self.error_step2.setText("Compte introuvable.")
            return

        password = self.password_field.text().strip()
        confirm = self.confirm_field.text().strip()
        token = (self.token_field.text() or "").strip()

        if not token:
            self.error_step2.setText(
                "Recopiez le code affiché en haut dans le champ « Code »."
            )
            self.token_field.setFocus()
            return
        if not password:
            self.error_step2.setText("Saisissez un nouveau mot de passe.")
            self.password_field.setFocus()
            return
        if not confirm:
            self.error_step2.setText("Confirmez le nouveau mot de passe.")
            self.confirm_field.setFocus()
            return
        if password != confirm:
            self.error_step2.setText(
                "Les deux mots de passe ne sont pas identiques."
            )
            self.confirm_field.setFocus()
            return

        ok_rules, msg_rules = Owner.validate_password(password)
        if not ok_rules:
            self.error_step2.setText(msg_rules)
            self.password_field.setFocus()
            return

        if not self.owner.verify_reset_token(token):
            self.error_step2.setText(
                "Code incorrect ou expiré.\n"
                "Vérifiez la saisie, ou cliquez sur « Retour » pour générer un nouveau code."
            )
            self.token_field.setFocus()
            return

        success, message = self.owner.reset_password(password)
        if not success:
            self.error_step2.setText(message)
            return

        QMessageBox.information(
            self,
            "Mot de passe mis à jour",
            f"Le mot de passe du compte « {self.owner.username} » a bien été modifié.\n\n"
            "Vous pouvez maintenant vous connecter avec ce nouveau mot de passe.",
        )
        self.accept()

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


class ResetPasswordDialog(ResetPasswordWidget):
    """Compatibilité : ancien nom de la boîte de dialogue."""

    def __init__(self, owner=None, token=None, parent=None):
        preselect = getattr(owner, "username", None) if owner is not None else None
        super().__init__(parent=parent, preselect_username=preselect)
        if owner is not None and token:
            self.owner = owner
            self._token = str(token).strip()
            self.account_banner.setText(f"Compte sélectionné : {owner.username}")
            self.code_display.setText(self._token)
            self.token_field.clear()
            self.stack.setCurrentIndex(1)
            self._set_progress(1)
