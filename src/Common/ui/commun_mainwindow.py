#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow, 
    QToolBar, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QPushButton, 
    QLineEdit, 
    QCheckBox, 
    QTextEdit,
    QGroupBox,
    QFormLayout,
    QMessageBox,
    QDialog
)

from ..cstatic import CConstants, logger
from .cmenubar import FMenuBar
from .cmenutoolbar import FMenuToolBar
from .common import FMainWindow, FWidget
from .statusbar import GStatusBar
from ..updater import UpdaterInit


class TestViewWidget(FWidget):
    """Shows the home page"""

    def __init__(self, parent=0, *args, **kwargs):
        super(TestViewWidget, self).__init__(parent=parent, *args, **kwargs)
        self.parent = parent
        self.parentWidget().setWindowTitle(" Test")
        self.title = "Common page"
        logger.debug("Initialisation de TestViewWidget")


class ExamplePageWidget(FWidget):
    """Page exemple avec différents widgets de démonstration"""

    def __init__(self, parent=0, *args, **kwargs):
        super(ExamplePageWidget, self).__init__(parent=parent, *args, **kwargs)
        self.parent = parent
        self.parentWidget().setWindowTitle("Page Exemple")
        self.title = "Page Exemple"
        
        self.setup_ui()
        logger.debug("Initialisation de ExamplePageWidget")

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        main_layout = QVBoxLayout()
        
        # Titre principal
        title_label = QLabel("Page Exemple - Démonstration des Widgets")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Groupe de widgets de base
        self.create_basic_widgets_group(main_layout)
        
        # Groupe de formulaire
        self.create_form_group(main_layout)
        
        # Groupe de boutons d'action
        self.create_action_buttons_group(main_layout)
        
        self.setLayout(main_layout)

    def create_basic_widgets_group(self, parent_layout):
        """Créer le groupe des widgets de base"""
        group_box = QGroupBox("Widgets de Base")
        layout = QVBoxLayout()
        
        # Checkbox
        self.checkbox = QCheckBox("Option activée")
        self.checkbox.setChecked(True)
        layout.addWidget(self.checkbox)
        
        # Champ de texte simple
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Texte simple:"))
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Saisissez du texte ici...")
        h_layout.addWidget(self.line_edit)
        layout.addLayout(h_layout)
        
        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)

    def create_form_group(self, parent_layout):
        """Créer le groupe de formulaire"""
        group_box = QGroupBox("Formulaire Exemple")
        form_layout = QFormLayout()
        
        # Champ nom
        self.name_field = QLineEdit()
        form_layout.addRow("Nom:", self.name_field)
        
        # Champ email
        self.email_field = QLineEdit()
        self.email_field.setPlaceholderText("exemple@email.com")
        form_layout.addRow("Email:", self.email_field)
        
        # Zone de texte
        self.text_area = QTextEdit()
        self.text_area.setMaximumHeight(100)
        self.text_area.setPlaceholderText("Commentaires ou notes...")
        form_layout.addRow("Commentaires:", self.text_area)
        
        group_box.setLayout(form_layout)
        parent_layout.addWidget(group_box)

    def create_action_buttons_group(self, parent_layout):
        """Créer le groupe de boutons d'action"""
        group_box = QGroupBox("Actions")
        layout = QHBoxLayout()
        
        # Bouton de validation
        validate_btn = QPushButton("Valider")
        validate_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        validate_btn.clicked.connect(self.on_validate)
        layout.addWidget(validate_btn)
        
        # Bouton d'effacement
        clear_btn = QPushButton("Effacer")
        clear_btn.setStyleSheet("background-color: #f44336; color: white;")
        clear_btn.clicked.connect(self.on_clear)
        layout.addWidget(clear_btn)
        
        # Bouton d'information
        info_btn = QPushButton("Info")
        info_btn.setStyleSheet("background-color: #2196F3; color: white;")
        info_btn.clicked.connect(self.on_info)
        layout.addWidget(info_btn)
        
        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)

    def on_validate(self):
        """Action de validation"""
        name = self.name_field.text()
        email = self.email_field.text()
        comments = self.text_area.toPlainText()
        is_checked = self.checkbox.isChecked()
        
        if not name:
            QMessageBox.warning(self, "Attention", "Le champ nom est requis!")
            return
        
        message = f"Données validées:\n\nNom: {name}\nEmail: {email}\nOption activée: {'Oui' if is_checked else 'Non'}"
        if comments:
            message += f"\nCommentaires: {comments}"
        
        QMessageBox.information(self, "Validation", message)
        logger.info(f"Données validées pour {name}")

    def on_clear(self):
        """Action d'effacement"""
        self.name_field.clear()
        self.email_field.clear()
        self.text_area.clear()
        self.line_edit.clear()
        self.checkbox.setChecked(False)
        
        QMessageBox.information(self, "Effacement", "Tous les champs ont été effacés!")
        logger.info("Champs effacés dans ExamplePageWidget")

    def on_info(self):
        """Action d'information"""
        info_text = """
        Cette page exemple démontre l'utilisation de différents widgets PyQt5:
        
        • QGroupBox pour organiser les widgets
        • QLabel pour afficher du texte
        • QLineEdit pour la saisie de texte simple
        • QTextEdit pour la saisie de texte multiligne
        • QCheckBox pour les options booléennes
        • QPushButton pour les actions
        • QFormLayout pour les formulaires
        • QMessageBox pour les dialogues
        
        Développé avec PyQt5 et Python.
        """
        
        QMessageBox.about(self, "À propos de cette page", info_text)
        logger.info("Information affichée dans ExamplePageWidget")


class CommonMainWindow(FMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        FMainWindow.__init__(self, parent=parent, *args, **kwargs)

        self.setWindowIcon(QIcon(f"{CConstants.APP_LOGO}"))
        self.setWindowTitle(f"{CConstants.APP_NAME} {CConstants.APP_VERSION}")

        # Vérifier si un utilisateur est connecté
        from ..models import Owner, Settings
        settings = Settings.select().where(Settings.id == 1).first()
        
        if settings and settings.auth_required:
            # Vérifier si un utilisateur est connecté
            if not Owner.select().where(Owner.is_identified == True).exists():
                logger.warning("Aucun utilisateur connecté, affichage de la fenêtre de connexion")
                from .login import LoginWidget
                if LoginWidget().exec_() != QDialog.Accepted:
                    logger.warning("Connexion annulée ou échouée")
                    self.close()
                    return

        self.toolBar = QToolBar()
        self.addToolBar(Qt.LeftToolBarArea, self.toolBar)

        # Pour statusBar
        try:
            self.status_bar = GStatusBar(self)
            self.setStatusBar(self.status_bar)
            # Enregistrer l'instance pour le nettoyage
            try:
                from ..cmain import register_statusbar_instance
                register_statusbar_instance(self.status_bar)
            except ImportError:
                logger.warning("Impossible d'enregistrer la statusbar pour le nettoyage")
        except Exception as exc:
            logger.warning(f"Impossible d'initialiser la barre de statut: {exc}")
            self.status_bar = None

        # Pour l'updater
        try:
            self.updater = UpdaterInit()
            # Enregistrer l'instance pour le nettoyage
            try:
                from ..cmain import register_updater_instance
                register_updater_instance(self.updater)
            except ImportError:
                logger.warning("Impossible d'enregistrer l'updater pour le nettoyage")
        except Exception as exc:
            logger.warning(f"Impossible d'initialiser l'updater: {exc}")
            self.updater = None

        self.menubar = FMenuBar(self)
        self.setMenuBar(self.menubar)
        logger.debug("Barre de menu initialisée")

        self.toolbar = FMenuToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)
        logger.debug("Barre d'outils initialisée")

        # Changer cette ligne pour utiliser ExamplePageWidget au lieu de TestViewWidget
        self.page = ExamplePageWidget  # ou TestViewWidget pour la page de test basique
        self.change_context(self.page)
        logger.debug("Contexte initial changé vers ExamplePageWidget")
        
    def closeEvent(self, event):
        """Override closeEvent pour nettoyer les threads avant fermeture"""
        try:
            logger.info("Fermeture de la fenêtre principale - nettoyage des threads")
            
            # Nettoyer manuellement les instances si elles existent
            if hasattr(self, 'status_bar') and self.status_bar:
                if hasattr(self.status_bar, 'cleanup'):
                    self.status_bar.cleanup()
                    
            if hasattr(self, 'updater') and self.updater:
                if hasattr(self.updater, 'cleanup'):
                    self.updater.cleanup()
                    
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage de la fenêtre principale: {e}")
        finally:
            super().closeEvent(event)

    def page_width(self):
        return self.width() - 100

    # def exit(self):
    #     logger.info("Fermeture de l'application")   
    #     from ..models import Settings
    #     settings = Settings.get(id=1)
    #     if not settings.auth_required:
    #         self.logout()
    #     else:
    #         self.close()