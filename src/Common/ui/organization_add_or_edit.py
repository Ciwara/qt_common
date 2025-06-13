#!usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad

import base64
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QWidget,
    QLabel,
    QMessageBox,
)
from PyQt5.QtGui import QPixmap

from ..models import Organization
from .common import ButtonSave, FormLabel, FWidget, IntLineEdit, LineEdit
from .util import check_is_empty


def image_to_base64(file_path):
    """Convertit une image en base64"""
    try:
        if not os.path.exists(file_path):
            return None
            
        # Vérifier la taille du fichier (max 2MB pour éviter les problèmes)
        file_size = os.path.getsize(file_path)
        if file_size > 2 * 1024 * 1024:  # 2MB
            return "TROP_GROS"
            
        with open(file_path, "rb") as image_file:
            # Encoder en base64
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Ajouter le préfixe data: avec le type MIME
            file_ext = os.path.splitext(file_path)[1].lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.svg': 'image/svg+xml'
            }
            
            mime_type = mime_types.get(file_ext, 'image/png')
            data_url = f"data:{mime_type};base64,{encoded_string}"
            
            return data_url
            
    except Exception as e:
        print(f"❌ Erreur lors de la conversion en base64: {e}")
        return None


def base64_to_pixmap(base64_data, max_size=100):
    """Convertit une chaîne base64 en QPixmap pour l'affichage"""
    try:
        if not base64_data or not base64_data.startswith('data:'):
            return None
            
        # Extraire les données base64 pure
        base64_part = base64_data.split(',')[1]
        image_data = base64.b64decode(base64_part)
        
        # Créer un QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        
        # Redimensionner si nécessaire
        if not pixmap.isNull() and max_size > 0:
            pixmap = pixmap.scaled(max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
        return pixmap
        
    except Exception as e:
        print(f"❌ Erreur lors de la conversion base64 vers pixmap: {e}")
        return None


class LogoSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal vertical
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Layout horizontal pour le sélecteur
        selector_layout = QHBoxLayout()
        
        self.path_edit = LineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("Aucun logo base64 sélectionné")
        
        self.browse_button = QPushButton("📂 Parcourir...")
        self.browse_button.clicked.connect(self.browse_file)
        self.browse_button.setToolTip("Sélectionner une image pour le logo de l'organisation")
        
        selector_layout.addWidget(self.path_edit)
        selector_layout.addWidget(self.browse_button)
        
        # Widget d'aperçu amélioré
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #007bff;
                border-radius: 12px;
                background-color: #f8f9fa;
                background-image: linear-gradient(45deg, #f8f9fa 25%, transparent 25%, transparent 75%, #f8f9fa 75%);
                background-size: 20px 20px;
                padding: 15px;
                min-height: 120px;
                max-height: 120px;
                min-width: 120px;
                max-width: 120px;
                color: #6c757d;
                font-weight: bold;
                font-size: 12px;
            }
            QLabel:hover {
                border-color: #0056b3;
                background-color: #e9ecef;
            }
        """)
        self.preview_label.setText("🖼️\nAperçu du logo")
        self.preview_label.setScaledContents(True)
        
        # Variable pour stocker le base64
        self.base64_data = None
        
        main_layout.addLayout(selector_layout)
        main_layout.addWidget(self.preview_label)
        
        self.setLayout(main_layout)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une image pour conversion en base64",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg);;Tous les fichiers (*)"
        )
        
        if file_path:
            # Convertir en base64
            base64_result = image_to_base64(file_path)
            
            if base64_result == "TROP_GROS":
                QMessageBox.warning(
                    self,
                    "🚫 Fichier trop volumineux",
                    "⚠️ Le fichier sélectionné est trop volumineux (max 2MB).\n\n"
                    "💡 Conseil : Utilisez un outil de compression d'image\n"
                    "ou choisissez une image plus petite."
                )
                return
            elif base64_result is None:
                QMessageBox.critical(
                    self,
                    "❌ Erreur de lecture",
                    "Impossible de lire le fichier image sélectionné.\n\n"
                    "Vérifiez que :\n"
                    "• Le fichier n'est pas corrompu\n"
                    "• Le format est supporté (PNG, JPG, GIF, BMP, SVG)\n"
                    "• Vous avez les droits de lecture sur le fichier"
                )
                return
            
            # Stocker les données
            self.base64_data = base64_result
            self.path_edit.setText(f"Logo base64 ({len(base64_result)} caractères)")
            
            # Afficher l'aperçu
            pixmap = base64_to_pixmap(base64_result, 90)
            if pixmap and not pixmap.isNull():
                self.preview_label.setPixmap(pixmap)
                self.preview_label.setText("")
            else:
                self.preview_label.clear()
                self.preview_label.setText("⚠️\nAperçu\nindisponible")
    
    def text(self):
        """Retourne les données base64 du logo"""
        return self.base64_data
    
    def setText(self, base64_data):
        """Configure le widget avec des données base64 existantes"""
        if base64_data:
            self.base64_data = base64_data
            self.path_edit.setText(f"Logo base64 existant ({len(base64_data)} caractères)")
            
            # Afficher l'aperçu
            pixmap = base64_to_pixmap(base64_data, 90)
            if pixmap and not pixmap.isNull():
                self.preview_label.setPixmap(pixmap)
                self.preview_label.setText("")
            else:
                self.preview_label.clear()
                self.preview_label.setText("⚠️\nAperçu\nindisponible")
        else:
            self.base64_data = None
            self.path_edit.setText("")
            self.preview_label.clear()
            self.preview_label.setText("🖼️\nAperçu du logo")


class NewOrEditOrganizationViewWidget(QDialog, FWidget):
    def __init__(self, pp=None, owner=None, parent=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.setWindowTitle("🏢 Nouvelle Organisation")
        self.parent = parent
        self.pp = pp
        self.owner = owner

        vbox = QVBoxLayout()

        self.organization_group_box()
        vbox.addWidget(self.organGroupBoxBtt)
        self.setLayout(vbox)

    def organization_group_box(self):
        self.organGroupBoxBtt = QGroupBox(self.tr("🏢 Configuration de l'organisation"))

        self.checked = QCheckBox("🔐 Activer l'authentification")
        self.checked.setChecked(True)
        self.checked.setToolTip(
            "Cocher pour activer la saisie de mot de passe.\n"
            "Si désactivé, l'accès à l'application sera libre."
        )
        self.logo_orga = LogoSelector()
        self.name_orga = LineEdit()
        self.name_orga.setPlaceholderText("Nom complet de votre organisation")
        
        self.phone = IntLineEdit()
        self.phone.setPlaceholderText("Numéro de téléphone principal")
        
        self.bp = LineEdit()
        self.bp.setPlaceholderText("Boîte postale (optionnel)")
        
        self.adress_org = QTextEdit()
        self.adress_org.setPlaceholderText("Adresse complète de l'organisation\n(rue, ville, code postal, pays)")
        
        self.email_org = LineEdit()
        self.email_org.setPlaceholderText("adresse@organisation.com")

        formbox = QFormLayout()
        formbox.addRow(FormLabel("🖼️ Logo de l'organisation *"), self.logo_orga)
        formbox.addRow(FormLabel("🏢 Nom de l'organisation *"), self.name_orga)
        formbox.addRow(FormLabel("📞 Téléphone *"), self.phone)
        formbox.addRow(FormLabel("🔐 Sécurité"), self.checked)
        formbox.addRow(FormLabel("📮 Boîte postale"), self.bp)
        formbox.addRow(FormLabel("📧 Email"), self.email_org)
        formbox.addRow(FormLabel("📍 Adresse complète"), self.adress_org)

        butt = ButtonSave("💾 Enregistrer l'organisation")
        butt.clicked.connect(self.save_edit)
        butt.setToolTip("Sauvegarder les informations de l'organisation")
        formbox.addRow("", butt)

        self.organGroupBoxBtt.setLayout(formbox)

    def save_edit(self):
        """Sauvegarde des informations de l'organisation"""
        if check_is_empty(self.name_orga):
            QMessageBox.warning(
                self, 
                "⚠️ Champ obligatoire", 
                "🏢 Le nom de l'organisation est requis.\n\n"
                "Veuillez saisir le nom complet de votre organisation."
            )
            return
        if check_is_empty(self.phone):
            QMessageBox.warning(
                self, 
                "⚠️ Champ obligatoire", 
                "📞 Le numéro de téléphone est requis.\n\n"
                "Veuillez saisir le numéro de téléphone principal."
            )
            return
        name_orga = str(self.name_orga.text())
        logo_base64 = self.logo_orga.text()  # Maintenant retourne le base64
        bp = str(self.bp.text())
        email_org = str(self.email_org.text())
        phone = str(self.phone.text())
        adress_org = str(self.adress_org.toPlainText())
        
        # 🔍 Validation et préparation des données
        print(f"🏢 Nom organisation: {name_orga}")
        print(f"📞 Téléphone: {phone}")
        print(f"🖼️ Logo base64 présent: {logo_base64 is not None}")
        print(f"🖼️ Logo widget base64_data: {self.logo_orga.base64_data is not None}")
        
        if logo_base64:
            print(f"📊 Taille logo base64: {len(logo_base64)} caractères")
            print(f"✅ Logo commence par data: {logo_base64.startswith('data:') if logo_base64 else False}")
        elif self.logo_orga.base64_data:
            print(f"📊 Taille logo widget: {len(self.logo_orga.base64_data)} caractères")
            logo_base64 = self.logo_orga.base64_data  # Utiliser directement les données du widget
        
        print(f"💾 Logo final à sauvegarder: {logo_base64 is not None}")

        org = Organization()
        org.phone = phone
        org.name_orga = name_orga
        org.logo_orga = logo_base64  # Sauvegarde du code base64 complet (pas l'URL)
        org.email_org = email_org
        org.bp = bp
        org.adress_org = adress_org
        
        # ✅ Confirmation : nous stockons bien le code base64, pas l'URL
        if logo_base64:
            print(f"💾 Stockage du logo en base64 (taille: {len(logo_base64)} caractères)")
            print(f"✅ Format valide data:image: {logo_base64.startswith('data:image')}")
        else:
            print("⚠️ Aucun logo base64 à sauvegarder")
        
        # Les champs after_cam et auth_required appartiennent à Settings, pas à Organization
        # Mettre à jour les paramètres séparément
        from ..models import Settings
        settings = Settings.get(id=1)
        settings.auth_required = True if self.checked.checkState() == Qt.Checked else False
        settings.save()
        try:
            org.save()
            
            # ✅ Vérification de la sauvegarde
            saved_org = Organization.get(id=org.id)
            print(f"🆔 Organisation sauvegardée ID: {saved_org.id}")
            print(f"🖼️ Logo sauvegardé présent: {saved_org.logo_orga is not None}")
            if saved_org.logo_orga:
                print(f"📊 Taille logo sauvegardé: {len(saved_org.logo_orga)} caractères")
                print(f"✅ Format valide: {saved_org.logo_orga.startswith('data:')}")
            
            # 🎉 Message de succès avec informations détaillées
            logo_info = ""
            if saved_org.logo_orga:
                logo_info = f"\n🖼️ Logo sauvegardé ({len(saved_org.logo_orga)} caractères)"
            else:
                logo_info = "\n📷 Aucun logo sélectionné"
            
            QMessageBox.information(
                self,
                "🎉 Succès",
                f"✅ Organisation '{name_orga}' créée avec succès !\n\n"
                f"📋 Informations enregistrées :\n"
                f"• Nom : {name_orga}\n"
                f"• Téléphone : {phone}\n"
                f"• Email : {email_org or 'Non renseigné'}\n"
                f"• B.P. : {bp or 'Non renseigné'}"
                f"{logo_info}"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Erreur de sauvegarde",
                f"Une erreur est survenue lors de la sauvegarde :\n\n"
                f"Détails techniques : {e}\n\n"
                f"Veuillez réessayer ou contacter le support technique."
            )
            print(f"❌ Erreur sauvegarde organisation: {e}")
