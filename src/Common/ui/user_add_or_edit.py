#!usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad


from peewee import IntegrityError
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QComboBox, QDialog, QFormLayout, QVBoxLayout

from ..models import Owner
from .common import Button, ButtonSave, FLabel, FWidget, IntLineEdit, LineEdit
from .util import check_is_empty, field_error, is_valide_codition_field


class NewOrEditUserViewWidget(QDialog, FWidget):
    def __init__(self, pp=None, owner=None, parent=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.setWindowTitle("👤 Nouvel utilisateur")
        self.parent = parent
        self.pp = pp
        self.owner = owner

        vbox = QVBoxLayout()
        formbox = QFormLayout()
        self.checked = QCheckBox("✅ Compte actif")
        self.checked.setToolTip("Cocher pour activer le compte utilisateur.\nUn compte inactif ne peut pas se connecter.")
        self.error_mssg = ""
        
        if self.owner:
            self.new = False
            self.title = f"✏️ Modification de l'utilisateur {self.owner.username}"
            self.succes_msg = f"✅ L'utilisateur '{self.owner.username}' a été mis à jour avec succès"
            if self.owner.isactive:
                self.checked.setCheckState(Qt.Checked)
        else:
            self.checked.setCheckState(Qt.Checked)
            self.new = True
            self.succes_msg = "🎉 Nouvel utilisateur créé avec succès"
            self.title = "👤 Création d'un nouvel utilisateur"
            self.owner = Owner()
        # self.checked.setToolTip(msg)
        self.setWindowTitle(self.title)

        self.username_field = LineEdit(self.owner.username)
        self.username_field.setEnabled(self.new)
        self.username_field.setPlaceholderText("Nom d'utilisateur unique" if self.new else "Nom d'utilisateur (non modifiable)")
        self.username_field.setToolTip("Identifiant unique pour la connexion" if self.new else "L'identifiant ne peut pas être modifié")
        
        self.password_field = LineEdit()
        self.password_field.setEchoMode(LineEdit.PasswordEchoOnEdit)
        self.password_field.setPlaceholderText("Mot de passe sécurisé")
        self.password_field.setToolTip("Saisissez un mot de passe fort (min. 6 caractères recommandés)")
        
        self.password_field_v = LineEdit()
        self.password_field_v.setEchoMode(LineEdit.PasswordEchoOnEdit)
        self.password_field_v.setPlaceholderText("Confirmer le mot de passe")
        self.password_field_v.setToolTip("Resaisissez le même mot de passe pour confirmation")
        self.password_field_v.textChanged.connect(self.check_password_is_valide)
        
        self.phone_field = IntLineEdit(self.owner.phone)
        self.phone_field.setPlaceholderText("Numéro de téléphone")
        self.phone_field.setToolTip("Numéro de téléphone de l'utilisateur (optionnel)")

        self.liste_group = [Owner.ADMIN, Owner.USER]
        # Combobox widget avec icônes
        self.box_group = QComboBox()
        group_labels = {
            Owner.ADMIN: "👑 Administrateur",
            Owner.USER: "👤 Utilisateur standard"
        }
        
        for index in self.liste_group:
            self.box_group.addItem(group_labels.get(index, index))
        
        self.box_group.setToolTip(
            "Choisissez le niveau d'accès :\n"
            "• Administrateur : Accès complet au système\n"
            "• Utilisateur standard : Accès limité aux fonctionnalités de base"
        )

        butt = ButtonSave("💾 Enregistrer l'utilisateur")
        butt.setToolTip("Sauvegarder les informations de l'utilisateur")
        butt.clicked.connect(self.add_or_edit_user)
        
        cancel_but = Button("❌ Annuler")
        cancel_but.setToolTip("Fermer sans sauvegarder")
        cancel_but.clicked.connect(self.cancel)

        formbox.addRow(FLabel("👤 Identifiant"), self.username_field)
        formbox.addRow(FLabel("🔒 Mot de passe"), self.password_field)
        if self.new:
            formbox.addRow(
                FLabel("🔐 Confirmation mot de passe"), self.password_field_v
            )
        formbox.addRow(FLabel("📞 Numéro de téléphone"), self.phone_field)
        formbox.addRow(FLabel("🎭 Groupe d'accès"), self.box_group)
        formbox.addRow(cancel_but, butt)
        vbox.addWidget(self.checked)
        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def cancel(self):
        """Annulation avec confirmation si des modifications ont été faites"""
        from PyQt5.QtWidgets import QMessageBox
        
        # Vérifier s'il y a des modifications non sauvegardées
        has_changes = (
            self.username_field.text().strip() != (self.owner.username or "") or
            self.password_field.text().strip() != "" or
            self.phone_field.text().strip() != (str(self.owner.phone) if self.owner.phone else "")
        )
        
        if has_changes:
            reply = QMessageBox.question(
                self,
                "⚠️ Modifications non enregistrées",
                "Vous avez apporté des modifications qui ne sont pas sauvegardées.\n\n"
                "Voulez-vous vraiment fermer sans enregistrer ?\n\n"
                "💡 Cliquez sur 'Non' pour revenir au formulaire\n"
                "et sauvegarder vos modifications.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                print("❌ Fermeture sans sauvegarde confirmée")
                self.close()
            else:
                print("↩️ Retour au formulaire pour sauvegarde")
        else:
            print("❌ Fermeture du formulaire utilisateur - aucune modification")
            self.close()

    def is_valide(self):
        """Validation complète du formulaire"""
        from PyQt5.QtWidgets import QMessageBox
        
        if check_is_empty(self.username_field):
            QMessageBox.warning(
                self,
                "⚠️ Champ obligatoire",
                "👤 L'identifiant utilisateur est requis.\n\n"
                "Veuillez saisir un nom d'utilisateur unique."
            )
            return False
            
        if check_is_empty(self.password_field):
            QMessageBox.warning(
                self,
                "⚠️ Champ obligatoire",
                "🔒 Le mot de passe est requis.\n\n"
                "Veuillez saisir un mot de passe sécurisé."
            )
            return False
            
        if self.new and check_is_empty(self.password_field_v):
            QMessageBox.warning(
                self,
                "⚠️ Champ obligatoire",
                "🔐 La confirmation du mot de passe est requise.\n\n"
                "Veuillez confirmer votre mot de passe."
            )
            return False
            
        if not self.check_password_is_valide():
            return False
            
        # Validation supplémentaire de la force du mot de passe
        password = str(self.password_field.text()).strip()
        if len(password) < 4:
            QMessageBox.warning(
                self,
                "⚠️ Mot de passe faible",
                "🔒 Le mot de passe est trop court.\n\n"
                "Recommandation : Utilisez au moins 6 caractères\n"
                "pour un mot de passe plus sécurisé."
            )
            
        return True

    def check_password_is_valide(self):
        """Vérification de la correspondance des mots de passe"""
        self.password = str(self.password_field.text())
        self.password_v = (
            str(self.password_field_v.text()) if self.new else self.owner.password
        )

        error_message = (
            "🔐 Les mots de passe ne correspondent pas.\n\nVérifiez votre saisie et réessayez."
            if self.new
            else "🔒 Mot de passe incorrect pour cet utilisateur."
        )

        if is_valide_codition_field(
            self.password_field_v,
            error_message,
            self.password != self.password_v,
        ):
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
        status = self.checked.checkState() == Qt.Checked

        # 📋 Logging des informations
        action = "Création" if self.new else "Modification"
        print(f"👤 {action} utilisateur: {username}")
        print(f"📞 Téléphone: {phone}")
        print(f"🎭 Groupe: {group}")
        print(f"✅ Statut actif: {status}")

        ow = self.owner
        ow.username = username
        ow.password = Owner().crypt_password(password) if self.new else password
        ow.phone = phone
        ow.group = group
        ow.isactive = status
        
        try:
            ow.save()
            self.close()
            self.accept()
            
            # 🎉 Messages de succès
            if self.pp:
                self.pp.refresh_()
                print(f"✅ Utilisateur sauvegardé avec succès - parent: {self.parent}")
                
                if self.parent:
                    status_text = "activé" if status else "désactivé"
                    group_text = "👑 Administrateur" if group == Owner.ADMIN else "👤 Utilisateur"
                    
                    success_message = (
                        f"🎉 Utilisateur '{username}' {'créé' if self.new else 'modifié'} avec succès !\n\n"
                        f"📋 Informations :\n"
                        f"• Identifiant : {username}\n"
                        f"• Téléphone : {phone or 'Non renseigné'}\n"
                        f"• Groupe : {group_text}\n"
                        f"• Statut : {status_text}"
                    )
                    
                    self.parent.Notify(success_message, "success")
                    
        except IntegrityError as e:
            print(f"❌ Erreur d'intégrité - utilisateur '{username}' existe déjà")
            field_error(
                self.username_field,
                f"❌ Nom d'utilisateur déjà utilisé\n\n"
                f"L'identifiant '{username}' existe déjà dans la base de données.\n"
                f"Veuillez choisir un autre nom d'utilisateur."
            )
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            if self.parent:
                self.parent.Notify(
                    f"❌ Erreur lors de la sauvegarde de l'utilisateur\n\n"
                    f"Détails techniques : {e}", "error"
                )
        # else:
        #     self.parent.Notify(
        #         "<h3>Formulaire non valide</h3> " + self.error_mssg, u"error")
