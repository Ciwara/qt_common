#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QFormLayout, QGroupBox, QVBoxLayout

from ..exports import import_backup
from .common import Button, EnterTabbedLineEdit, FLabel, FormLabel, FWidget, LineEdit

try:
    from ..cstatic import CConstants
except Exception as e:
    print("Erreur lors de l'importation de CConstants:", e)


class RestorationViewWidget(QDialog, FWidget):
    def __init__(self, pp=None, owner=None, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setWindowTitle("🔄 Restauration de données")
        self.vbox = QVBoxLayout()

        # Configure the header with improved styling
        self.label = FLabel()
        self.label.setStyleSheet(
            f"background: url('{CConstants.img_media}center.png') no-repeat center center;"
            "height: 60px; width: 60px; margin: 10px; padding: 10px;"
            "border-radius: 30px; background-color: #f8f9fa; border: 2px solid #dee2e6;"
        )

        # ==== 🌐 Section restauration en ligne ====
        self.onlineRestorBoxBtt = QGroupBox(self.tr("🌐 Restauration depuis le cloud"))
        self.bn_resto_onligne = Button("☁️ Se connecter au cloud")
        self.bn_resto_onligne.setIcon(
            QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}cloud.png"))
        )
        self.bn_resto_onligne.setToolTip("Connectez-vous pour restaurer vos données depuis le cloud")
        self.bn_resto_onligne.clicked.connect(self.resto_onligne)

        self.bn_resto_l = Button("💾 Importer une sauvegarde locale")
        self.bn_resto_l.setIcon(
            QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}db.png"))
        )
        self.bn_resto_l.setToolTip("Sélectionner un fichier .db depuis votre ordinateur")
        self.bn_resto_l.clicked.connect(self.resto_local_db)

        self.bn_ignore = Button("🚀 Nouvelle installation")
        self.bn_ignore.setIcon(
            QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}go-next.png"))
        )
        self.bn_ignore.setToolTip("Commencer avec une installation vierge (aucune donnée à restaurer)")
        self.bn_ignore.clicked.connect(self.ignore_resto)

        self.mail_field = LineEdit()
        self.mail_field.setPlaceholderText("votre.email@exemple.com")
        
        self.password_field = EnterTabbedLineEdit()
        from PyQt6.QtWidgets import QLineEdit
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("Mot de passe de votre compte cloud")
        self.password_field.setFocus()

        formbox = QFormLayout()
        formbox.addRow(FormLabel("📧 Adresse email"), self.mail_field)
        formbox.addRow(FormLabel("🔒 Mot de passe"), self.password_field)
        formbox.addRow(FormLabel(""), self.bn_resto_onligne)
        self.onlineRestorBoxBtt.setLayout(formbox)
        self.vbox.addWidget(self.onlineRestorBoxBtt)

        # ==== 💾 Section restauration locale ====
        self.onLocaleRestorBoxBtt = QGroupBox(
            self.tr("💾 Restauration depuis un fichier local")
        )
        l_formbox = QFormLayout()
        l_formbox.addRow(FormLabel(""), self.bn_resto_l)
        self.onLocaleRestorBoxBtt.setLayout(l_formbox)
        self.vbox.addWidget(self.onLocaleRestorBoxBtt)

        i_formbox = QFormLayout()
        i_formbox.addRow(FLabel("<h2></h2>"), self.bn_ignore)
        self.vbox.addLayout(i_formbox)

        self.setLayout(self.vbox)

    def resto_onligne(self):
        """Restauration des données depuis le cloud"""
        from PyQt6.QtWidgets import QMessageBox
        
        email = self.mail_field.text().strip()
        password = self.password_field.text().strip()
        
        if not email:
            QMessageBox.warning(
                self,
                "⚠️ Champ obligatoire",
                "📧 Veuillez saisir votre adresse email\npour vous connecter au service cloud."
            )
            return
            
        if not password:
            QMessageBox.warning(
                self,
                "⚠️ Champ obligatoire", 
                "🔒 Veuillez saisir votre mot de passe\npour vous connecter au service cloud."
            )
            return
        
        # TODO: Implémenter la restauration en ligne
        QMessageBox.information(
            self,
            "🚧 Fonctionnalité en développement",
            "☁️ La restauration depuis le cloud n'est pas encore disponible.\n\n"
            "💡 Utilisez la restauration locale en attendant,\n"
            "ou choisissez 'Nouvelle installation'."
        )
        print(f"🌐 Tentative de connexion cloud - Email: {email}")

    def ignore_resto(self):
        """Ignorer la restauration et commencer une nouvelle installation"""
        from PyQt6.QtWidgets import QMessageBox
        from .organization_add_or_edit import NewOrEditOrganizationViewWidget
        
        reply = QMessageBox.question(
            self,
            "🚀 Confirmer la nouvelle installation",
            "Êtes-vous sûr de vouloir commencer une nouvelle installation ?\n\n"
            "⚠️ Attention :\n"
            "• Aucune donnée ne sera restaurée\n"
            "• Vous commencerez avec une base de données vierge\n"
            "• Cette action ne peut pas être annulée\n\n"
            "💡 Si vous avez des sauvegardes, il est recommandé\n"
            "de les restaurer maintenant.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            print("🚀 Nouvelle installation confirmée - aucune restauration")
            
            # Ouvrir le dialogue de création d'organisation
            org_dialog = NewOrEditOrganizationViewWidget(parent=self)
            if org_dialog.exec() == QDialog.DialogCode.Accepted:
                print("✅ Organisation créée avec succès")
                self.accept()
            else:
                print("❌ Création d'organisation annulée")
                # Ne pas fermer le dialogue de restauration si l'organisation n'a pas été créée
        else:
            print("❌ Nouvelle installation annulée")

    def resto_local_db(self):
        """Import local simplifié : choisir un .db → confirmer → importer."""
        ok = import_backup(parent=self, confirm=True)
        if ok:
            self.accept()
