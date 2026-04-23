#!usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad


from peewee import IntegrityError
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QComboBox, QDialog, QFormLayout, QLineEdit, QVBoxLayout

from ..models import Owner
from .common import Button, ButtonSave, FLabel, FWidget, IntLineEdit, LineEdit
from .util import check_is_empty, field_error, is_valide_codition_field


class NewOrEditUserViewWidget(QDialog, FWidget):
    def __init__(self, pp=None, owner=None, parent=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.setWindowTitle("Nouvel utilisateur")
        self.parent = parent
        self.pp = pp
        self.owner = owner

        vbox = QVBoxLayout()
        formbox = QFormLayout()
        self.checked = QCheckBox("Compte actif (peut se connecter)")
        self.checked.setToolTip(
            "Décochez pour bloquer la connexion sans supprimer le compte."
        )
        self.error_mssg = ""
        
        if self.owner:
            self.new = False
            self.title = f"Modifier l'utilisateur « {self.owner.username} »"
            self.succes_msg = f"L'utilisateur « {self.owner.username} » a été mis à jour."
            if self.owner.isactive:
                self.checked.setCheckState(Qt.CheckState.Checked)
        else:
            self.checked.setCheckState(Qt.CheckState.Checked)
            self.new = True
            self.succes_msg = "Nouvel utilisateur enregistré."
            self.title = "Créer un utilisateur"
            self.owner = Owner()
        self.setWindowTitle(self.title)

        self.head_label = FLabel(
            f"<div style='font-size:15px;font-weight:600;color:#2c3e50;'>{self.title}</div>"
        )
        self.head_label.setTextFormat(Qt.TextFormat.RichText)

        self.username_field = LineEdit(self.owner.username)
        self.username_field.setEnabled(self.new)
        self.username_field.setPlaceholderText(
            "Identifiant de connexion (unique)" if self.new else ""
        )
        self.username_field.setToolTip(
            "Identifiant unique pour la connexion"
            if self.new
            else "L'identifiant ne peut pas être modifié après création."
        )

        self.password_field = LineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        if self.new:
            self.password_field.setPlaceholderText("Mot de passe")
            self.password_field.setToolTip(
                "Au moins 8 caractères, majuscule, minuscule, chiffre et signe recommandés."
            )
        else:
            self.password_field.setPlaceholderText(
                "Laisser vide pour ne pas changer le mot de passe"
            )
            self.password_field.setToolTip(
                "Renseignez un nouveau mot de passe uniquement si vous souhaitez le remplacer."
            )

        self.password_field_v = LineEdit()
        self.password_field_v.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.password_field_v.setPlaceholderText(
            "Confirmer le mot de passe" if self.new else "Confirmer le nouveau mot de passe"
        )
        self.password_field_v.setToolTip(
            "Même saisie que le champ mot de passe."
        )
        self.password_field_v.textChanged.connect(self.check_password_is_valide)
        self.password_field.textChanged.connect(self.check_password_is_valide)
        
        self.phone_field = IntLineEdit(self.owner.phone)
        self.phone_field.setPlaceholderText("Numéro de téléphone")
        self.phone_field.setToolTip("Numéro de téléphone de l'utilisateur (optionnel)")

        self.liste_group = [Owner.ADMIN, Owner.USER]
        # Combobox widget avec icônes
        self.box_group = QComboBox()
        group_labels = {
            Owner.ADMIN: "Administrateur (accès complet)",
            Owner.USER: "Utilisateur (accès standard)",
        }
        
        for index in self.liste_group:
            self.box_group.addItem(group_labels.get(index, index))
        
        self.box_group.setToolTip(
            "Choisissez le niveau d'accès :\n"
            "• Administrateur : Accès complet au système\n"
            "• Utilisateur standard : Accès limité aux fonctionnalités de base"
        )

        butt = ButtonSave("Enregistrer")
        butt.setToolTip("Enregistrer le compte utilisateur")
        butt.clicked.connect(self.add_or_edit_user)
        butt.setDefault(True)

        cancel_but = Button("Annuler")
        cancel_but.setToolTip("Fermer sans enregistrer")
        cancel_but.clicked.connect(self.cancel)

        vbox.addWidget(self.head_label)
        vbox.addWidget(self.checked)
        formbox.addRow(FLabel("Identifiant"), self.username_field)
        formbox.addRow(FLabel("Mot de passe"), self.password_field)
        formbox.addRow(FLabel("Confirmation"), self.password_field_v)
        formbox.addRow(FLabel("Téléphone"), self.phone_field)
        formbox.addRow(FLabel("Rôle"), self.box_group)
        formbox.addRow(cancel_but, butt)
        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def cancel(self):
        """Annulation avec confirmation si des modifications ont été faites"""
        from PyQt6.QtWidgets import QMessageBox
        
        # Vérifier s'il y a des modifications non sauvegardées
        has_changes = (
            self.username_field.text().strip() != (self.owner.username or "") or
            self.password_field.text().strip() != "" or
            self.phone_field.text().strip() != (str(self.owner.phone) if self.owner.phone else "")
        )
        
        if has_changes:
            reply = QMessageBox.question(
                self,
                "Modifications non enregistrées",
                "Fermer sans enregistrer les changements ?\n\n"
                "Choisissez « Non » pour revenir au formulaire.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                print("❌ Fermeture sans sauvegarde confirmée")
                self.close()
            else:
                print("↩️ Retour au formulaire pour sauvegarde")
        else:
            print("❌ Fermeture du formulaire utilisateur - aucune modification")
            self.close()

    def is_valide(self):
        """Validation complète du formulaire"""
        from PyQt6.QtWidgets import QMessageBox

        if check_is_empty(self.username_field):
            QMessageBox.warning(
                self,
                "Champ obligatoire",
                "L'identifiant de connexion est obligatoire.",
            )
            return False

        password = str(self.password_field.text()).strip()

        if self.new:
            if not password:
                QMessageBox.warning(
                    self,
                    "Champ obligatoire",
                    "Le mot de passe est obligatoire pour un nouvel utilisateur.",
                )
                return False
            if check_is_empty(self.password_field_v):
                QMessageBox.warning(
                    self,
                    "Champ obligatoire",
                    "Veuillez confirmer le mot de passe.",
                )
                return False
        elif password:
            if str(self.password_field_v.text()).strip() != password:
                QMessageBox.warning(
                    self,
                    "Confirmation",
                    "Le mot de passe et sa confirmation ne correspondent pas.",
                )
                return False

        if not self.check_password_is_valide():
            return False

        # Avertissement mot de passe faible (ne bloque pas)
        if password:
            is_valid, message = Owner.validate_password(password)
        else:
            is_valid, message = True, ""

        if password and not is_valid:
            # Afficher seulement un avertissement, ne pas bloquer la création
            QMessageBox.warning(
                self,
                "Mot de passe faible",
                f"{message}\n\n"
                "Recommandations : au moins 8 caractères, une majuscule, une minuscule, "
                "un chiffre et un caractère spécial.\n\n"
                "Vous pouvez continuer, mais un mot de passe plus robuste est conseillé.",
            )

        return True

    def check_password_is_valide(self):
        """Vérifie la correspondance mot de passe / confirmation."""
        pwd = str(self.password_field.text()).strip()
        pwd_v = str(self.password_field_v.text()).strip()

        if not pwd and not self.new:
            return True

        if self.new:
            err = "Les mots de passe ne correspondent pas."
            if is_valide_codition_field(
                self.password_field_v, err, pwd != pwd_v
            ):
                return False
            return True

        if pwd:
            err = "La confirmation ne correspond pas au nouveau mot de passe."
            if is_valide_codition_field(self.password_field_v, err, pwd != pwd_v):
                return False
        return True

    def add_or_edit_user(self):
        """Sauvegarde de l'utilisateur (création ou modification)"""
        if not self.is_valide():
            print("❌ Formulaire non valide - sauvegarde annulée")
            return

        username = str(self.username_field.text()).strip()
        password = str(self.password_field.text()).strip()
        phone = str(self.phone_field.text())
        group = self.liste_group[self.box_group.currentIndex()]
        status = self.checked.checkState() == Qt.CheckState.Checked

        ow = self.owner
        ow.username = username
        if self.new or password:
            ow.password = ow.crypt_password(password)
        ow.phone = phone
        ow.group = group
        ow.isactive = status

        try:
            ow.save()
            self.accept()
            
            # 🎉 Messages de succès et rafraîchissement
            if self.pp:
                # Rafraîchir la liste des utilisateurs
                if hasattr(self.pp, 'refresh_'):
                    self.pp.refresh_()
                # Si pp est InfoTableWidget, rafraîchir aussi la liste parente
                if hasattr(self.pp, 'parent') and hasattr(self.pp.parent, 'table_owner'):
                    self.pp.parent.table_owner.refresh_()
                    # Mettre à jour les statistiques
                    if hasattr(self.pp.parent, 'update_stats'):
                        self.pp.parent.update_stats()
                    # Rafraîchir les détails si l'utilisateur modifié est sélectionné
                    if hasattr(self.pp, 'owner') and self.pp.owner and self.pp.owner.id == ow.id:
                        self.pp.refresh_(ow)
                
                print(f"✅ Utilisateur sauvegardé avec succès - parent: {self.parent}")
                
                if self.parent:
                    status_text = "activé" if status else "désactivé"
                    group_text = (
                        "Administrateur" if group == Owner.ADMIN else "Utilisateur"
                    )
                    verb = "créé" if self.new else "mis à jour"
                    success_message = (
                        f"Utilisateur « {username} » {verb}.\n"
                        f"Téléphone : {phone or '—'} ; rôle : {group_text} ; compte {status_text}."
                    )
                    self.parent.Notify(success_message, "success")
                    
                    # Mettre à jour les statistiques si disponible (via la fenêtre principale)
                    if hasattr(self.parent, 'update_stats'):
                        self.parent.update_stats()
                    
        except IntegrityError:
            print(f"❌ Erreur d'intégrité - utilisateur '{username}' existe déjà")
            field_error(
                self.username_field,
                f"L'identifiant « {username} » est déjà utilisé. "
                f"Choisissez un autre nom.",
            )
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            if self.parent:
                self.parent.Notify(
                    f"Erreur lors de l'enregistrement du compte.\nDétail : {e}",
                    "error",
                )
        # else:
        #     self.parent.Notify(
        #         "<h3>Formulaire non valide</h3> " + self.error_mssg, u"error")
