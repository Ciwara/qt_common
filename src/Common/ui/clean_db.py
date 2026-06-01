#!usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad

import os
import shutil
from datetime import datetime

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..models import DB_FILE, Owner
from .common import (
    DeletedBtt,
    EnterTabbedLineEdit,
    ErrorLabel,
    FormLabel,
    FPageTitle,
    FWidget,
)
from .util import check_is_empty, field_error

try:
    from ..cstatic import CConstants
except Exception as exc:
    print(exc)

DATETIME = datetime.now().strftime("%Y%m%d_%H%M%S")


def _expand_delete_order(selected, cleanable, prereqs):
    """Ajoute les prérequis FK puis ordonne selon l’ordre d’affichage (enfants d’abord)."""
    by_index = {cls: i for i, (_, cls) in enumerate(cleanable)}
    expanded = set(selected)
    changed = True
    while changed:
        changed = False
        for m in list(expanded):
            for p in prereqs.get(m, ()) or ():
                if p not in expanded:
                    expanded.add(p)
                    changed = True
    return sorted(expanded, key=lambda c: by_index.get(c, 9999))


class DBCleanerWidget(QDialog, FWidget):
    def __init__(self, parent=0, *args, **kwargs):
        QDialog.__init__(self, parent=parent, *args, **kwargs)
        self.parent = parent

        self.setWindowTitle("Confirmation de la suppression")
        vbox = QVBoxLayout()

        self._owner_list = list(Owner.get_active_non_superusers())
        self._table_rows = []  # (label, model_cls, QCheckBox)

        self.loginUserGroupBox()
        vbox.addWidget(
            FPageTitle("<h1 style='color: red;'>Suppression des enregistrements</h1>")
        )
        vbox.addWidget(self.tables_group)
        vbox.addWidget(self.topLeftGroupBox)
        self.setLayout(vbox)
        self.resize(480, 520)

    def _build_tables_group(self):
        self.tables_group = QGroupBox(self.tr("Tables à vider (cochez celles concernées)"))
        outer = QVBoxLayout()

        warn = QLabel(
            self.tr(
                "Cette action est irréversible après validation. "
                "Une copie de sauvegarde du fichier base sera créée avant suppression."
            )
        )
        warn.setWordWrap(True)
        outer.addWidget(warn)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)

        cleanable = list(CConstants.CLEANABLE_MODELS)
        if cleanable:
            for label, model_cls in cleanable:
                cb = QCheckBox(label)
                self._table_rows.append((label, model_cls, cb))
                inner_layout.addWidget(cb)
        else:
            inner_layout.addWidget(
                QLabel(
                    self.tr(
                        "Aucune table n’est enregistrée pour le nettoyage. "
                        "Configurez CLEANABLE_MODELS dans l’application."
                    )
                )
            )

        inner_layout.addStretch()
        scroll.setWidget(inner)
        outer.addWidget(scroll)

        btn_row = QHBoxLayout()
        all_on = QPushButton(self.tr("Tout cocher"))
        all_on.clicked.connect(self._check_all)
        all_off = QPushButton(self.tr("Tout décocher"))
        all_off.clicked.connect(self._uncheck_all)
        btn_row.addWidget(all_on)
        btn_row.addWidget(all_off)
        btn_row.addStretch()
        outer.addLayout(btn_row)

        self.tables_group.setLayout(outer)

    def _check_all(self):
        for _, _, cb in self._table_rows:
            cb.setChecked(True)

    def _uncheck_all(self):
        for _, _, cb in self._table_rows:
            cb.setChecked(False)

    def loginUserGroupBox(self):
        self._build_tables_group()

        self.topLeftGroupBox = QGroupBox(
            self.tr("Authentification (mot de passe du compte sélectionné)")
        )

        self.box_username = QComboBox()
        for owner in self._owner_list:
            self.box_username.addItem(owner.username)

        self.username_field = self.box_username
        self.password_field = EnterTabbedLineEdit()
        from PyQt6.QtWidgets import QLineEdit

        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setFocus()

        self.login_button = DeletedBtt("&Supprimer")
        self.login_button.setIcon(
            QIcon.fromTheme(
                "delete", QIcon("{}login.png".format(CConstants.img_cmedia))
            )
        )
        self.login_button.clicked.connect(self.login)

        self.cancel_button = QPushButton("&Annuler")
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setFlat(True)

        self.login_error = ErrorLabel("")

        formbox = QFormLayout()
        formbox.addRow(FormLabel("Identifiant"), self.username_field)
        formbox.addRow(FormLabel("Mot de passe"), self.password_field)
        formbox.addRow(self.cancel_button, self.login_button)

        self.topLeftGroupBox.setLayout(formbox)

    def is_valide(self):
        if check_is_empty(self.password_field):
            return False
        return True

    def cancel(self):
        self.close()

    def login(self):
        if not self.is_valide():
            return

        if not self._owner_list:
            QMessageBox.warning(
                self,
                self.tr("Compte"),
                self.tr("Aucun utilisateur actif disponible pour confirmer la suppression."),
            )
            return

        idx = self.box_username.currentIndex()
        if idx < 0 or idx >= len(self._owner_list):
            return
        owner = self._owner_list[idx]
        password = str(self.password_field.text()).strip()

        try:
            db_owner = Owner.get(Owner.id == owner.id)
            if not db_owner.verify_password(password):
                field_error(self.password_field, "Mot de passe incorrect")
                return
            self.cleaner_db()
        except Exception as e:
            print(f"❌ Erreur: {e}")
            field_error(self.password_field, "Mot de passe incorrect")

    def _selected_models(self):
        return [model_cls for _, model_cls, cb in self._table_rows if cb.isChecked()]

    def _labels_for_models(self, model_classes, cleanable):
        labels = []
        by_cls = {m: lab for lab, m in cleanable}
        for m in model_classes:
            labels.append(by_cls.get(m, m.__name__))
        return labels

    def cleaner_db(self):
        cleanable = list(CConstants.CLEANABLE_MODELS)
        selected = self._selected_models()

        if cleanable and not selected:
            QMessageBox.warning(
                self,
                self.tr("Tables"),
                self.tr("Cochez au moins une table à vider, ou annulez."),
            )
            return

        prereqs = dict(CConstants.CLEAN_MODEL_PREREQUISITES or {})

        if cleanable:
            to_run = _expand_delete_order(selected, cleanable, prereqs)
            labels = self._labels_for_models(to_run, cleanable)
            owner_selected = any(
                m is Owner for m in selected
            )
            msg = self.tr(
                "Supprimer définitivement les enregistrements des tables suivantes ?\n\n• "
            ) + "\n• ".join(labels)
            if owner_selected:
                msg += "\n\n" + self.tr(
                    "Attention : la suppression des utilisateurs (Owner) peut rendre "
                    "l’application inutilisable jusqu’à une réinitialisation manuelle."
                )
            rep = QMessageBox.question(
                self,
                self.tr("Confirmer la suppression"),
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if rep != QMessageBox.StandardButton.Yes:
                return
        else:
            to_run = []
            if CConstants.list_models:
                rep = QMessageBox.question(
                    self,
                    self.tr("Confirmer la suppression"),
                    self.tr(
                        "Aucune table listée dans CLEANABLE_MODELS. "
                        "Utiliser l’ancien mode (list_models) ?"
                    ),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if rep != QMessageBox.StandardButton.Yes:
                    return
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Configuration"),
                    self.tr("Aucune table à vider n’est configurée."),
                )
                return

        path_db_file = DB_FILE
        if not os.path.isfile(path_db_file):
            QMessageBox.critical(
                self,
                self.tr("Base de données"),
                self.tr("Fichier base introuvable : %s") % path_db_file,
            )
            return

        base, ext = os.path.splitext(os.path.basename(path_db_file))
        backup_name = "{}__{}.old{}".format(base, DATETIME, ext or "")
        backup_path = os.path.join(os.path.dirname(path_db_file), backup_name)
        try:
            shutil.copy2(path_db_file, backup_path)
        except OSError as e:
            QMessageBox.critical(
                self,
                self.tr("Sauvegarde"),
                self.tr("Impossible de copier la base avant suppression : %s") % e,
            )
            return

        try:
            if cleanable:
                for model_cls in to_run:
                    model_cls.delete().execute()
            else:
                for mod in CConstants.list_models:
                    for m in mod:
                        m.delete_instance()
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Erreur"),
                self.tr("Échec pendant la suppression : %s") % e,
            )
            return

        self.parent.update()
        self.cancel()
        self.parent.Notify("Les données ont été bien supprimées", "error")
