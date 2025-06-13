#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Démonstration Simple du module Common
Version simplifiée et fonctionnelle de la démonstration
"""

import sys
import os
from pathlib import Path

# Ajout du répertoire src au PYTHONPATH
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QLabel, QTextEdit, QGroupBox, QFormLayout,
    QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Test d'import du module Common
try:
    # Import des composants principaux
    from Common.cstatic import logger, CConstants
    from Common.models import Settings, Organization, Owner, dbh
    
    # Import des widgets modernes s'ils sont disponibles
    try:
        from Common.ui.modern_widgets import (
            ModernButton, ModernLineEdit, ModernComboBox, ModernGroupBox,
            ModernCard, LoadingSpinner, StatusIndicator
        )
        MODERN_WIDGETS_AVAILABLE = True
    except ImportError:
        MODERN_WIDGETS_AVAILABLE = False
    
    COMMON_AVAILABLE = True
    print("✅ Module Common importé avec succès")
    logger.info("Module Common importé avec succès pour la démonstration")
    
except ImportError as e:
    print(f"❌ Erreur d'import du module Common: {e}")
    COMMON_AVAILABLE = False

class CommonDemoSimple(QMainWindow):
    """Démonstration simple du module Common"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        if COMMON_AVAILABLE:
            self.apply_theme()
            self.update_database_info()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("Démonstration Simple - Module Common")
        self.setMinimumSize(900, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title_label = QLabel("🔧 Démonstration du Module Common")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Informations système
        self.create_system_info(main_layout)
        
        # Section base de données
        self.create_database_section(main_layout)
        
        # Section thèmes et styles
        if COMMON_AVAILABLE:
            self.create_themes_section(main_layout)
        
        # Section widgets modernes
        if COMMON_AVAILABLE and MODERN_WIDGETS_AVAILABLE:
            self.create_modern_widgets_section(main_layout)
        
        # Section tests
        self.create_tests_section(main_layout)
        
        # Zone de logs
        self.create_logs_section(main_layout)
        
        # Barre de statut
        self.statusBar().showMessage("Module Common - Prêt")
    
    def create_system_info(self, parent_layout):
        """Crée la section d'informations système"""
        group = QGroupBox("📊 Informations Système")
        layout = QFormLayout(group)
        
        if COMMON_AVAILABLE:
            # Informations du module Common
            layout.addRow("Module Common:", QLabel("✅ Disponible"))
            layout.addRow("Debug mode:", QLabel("✅ Activé" if CConstants.DEBUG else "❌ Désactivé"))
            layout.addRow("Base de données:", QLabel("✅ Connectée" if dbh and not dbh.is_closed() else "❌ Déconnectée"))
            layout.addRow("Widgets modernes:", QLabel("✅ Disponibles" if MODERN_WIDGETS_AVAILABLE else "❌ Non disponibles"))
        else:
            layout.addRow("Module Common:", QLabel("❌ Non disponible"))
        
        # Informations Python
        layout.addRow("Version Python:", QLabel(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"))
        layout.addRow("Plateforme:", QLabel(sys.platform))
        
        parent_layout.addWidget(group)
    
    def create_database_section(self, parent_layout):
        """Crée la section de gestion de la base de données"""
        group = QGroupBox("🗃️ Base de Données")
        layout = QVBoxLayout(group)
        
        # Informations sur la base
        self.db_info_label = QLabel("Chargement...")
        layout.addWidget(self.db_info_label)
        
        # Boutons de test
        buttons_layout = QHBoxLayout()
        
        test_db_btn = QPushButton("🔍 Tester Connexion")
        test_db_btn.clicked.connect(self.test_database)
        buttons_layout.addWidget(test_db_btn)
        
        if COMMON_AVAILABLE:
            show_models_btn = QPushButton("📊 Afficher Modèles")
            show_models_btn.clicked.connect(self.show_models)
            buttons_layout.addWidget(show_models_btn)
            
            settings_btn = QPushButton("⚙️ Paramètres")
            settings_btn.clicked.connect(self.show_settings)
            buttons_layout.addWidget(settings_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        parent_layout.addWidget(group)
    
    def create_themes_section(self, parent_layout):
        """Crée la section de gestion des thèmes"""
        group = QGroupBox("🎨 Thèmes et Styles")
        layout = QVBoxLayout(group)
        
        info_label = QLabel("Sélectionnez un thème pour voir les changements:")
        layout.addWidget(info_label)
        
        # Boutons de thèmes
        themes_layout = QHBoxLayout()
        
        try:
            theme_manager = get_theme_manager()
            themes = theme_manager.get_available_themes()
            for theme_key, theme_name in themes.items():
                if MODERN_WIDGETS_AVAILABLE:
                    btn = ModernButton(theme_name, button_type="default")
                else:
                    btn = QPushButton(theme_name)
                btn.clicked.connect(lambda checked, key=theme_key: self.change_theme(key))
                themes_layout.addWidget(btn)
        except Exception as e:
            error_label = QLabel(f"Erreur lors du chargement des thèmes: {e}")
            layout.addWidget(error_label)
        
        themes_layout.addStretch()
        layout.addLayout(themes_layout)
        
        parent_layout.addWidget(group)
    
    def create_modern_widgets_section(self, parent_layout):
        """Crée la section des widgets modernes"""
        group = QGroupBox("🎯 Widgets Modernes")
        layout = QVBoxLayout(group)
        
        # Boutons modernes
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(ModernButton("Primaire", button_type="primary"))
        buttons_layout.addWidget(ModernButton("Succès", button_type="success"))
        buttons_layout.addWidget(ModernButton("Danger", button_type="danger"))
        buttons_layout.addWidget(ModernButton("Défaut", button_type="default"))
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Champs de saisie
        layout.addWidget(ModernLineEdit("Exemple de champ moderne"))
        
        # ComboBox
        combo = ModernComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        layout.addWidget(combo)
        
        # Indicateurs de statut
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Statuts:"))
        status_layout.addWidget(StatusIndicator("active"))
        status_layout.addWidget(StatusIndicator("processing"))
        status_layout.addWidget(StatusIndicator("error"))
        
        spinner = LoadingSpinner(20)
        spinner.start()
        status_layout.addWidget(spinner)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        parent_layout.addWidget(group)
    
    def create_tests_section(self, parent_layout):
        """Crée la section de tests"""
        group = QGroupBox("🧪 Tests")
        layout = QHBoxLayout(group)
        
        # Boutons de test
        if COMMON_AVAILABLE:
            log_test_btn = QPushButton("📝 Test Logs")
            log_test_btn.clicked.connect(self.test_logging)
            layout.addWidget(log_test_btn)
            
            notification_btn = QPushButton("🔔 Test Notification")
            notification_btn.clicked.connect(self.test_notification)
            layout.addWidget(notification_btn)
            
            error_btn = QPushButton("⚠️ Test Erreur")
            error_btn.clicked.connect(self.test_error)
            layout.addWidget(error_btn)
        else:
            no_test_label = QLabel("Tests non disponibles (module Common manquant)")
            layout.addWidget(no_test_label)
        
        layout.addStretch()
        parent_layout.addWidget(group)
    
    def create_logs_section(self, parent_layout):
        """Crée la section d'affichage des logs"""
        group = QGroupBox("📋 Logs")
        layout = QVBoxLayout(group)
        
        self.logs_text = QTextEdit()
        self.logs_text.setMaximumHeight(150)
        self.logs_text.setFont(QFont("Courier", 10))
        self.logs_text.setPlaceholderText("Les logs et messages s'afficheront ici...")
        layout.addWidget(self.logs_text)
        
        # Boutons de contrôle des logs
        logs_buttons = QHBoxLayout()
        
        clear_btn = QPushButton("🗑️ Effacer")
        clear_btn.clicked.connect(self.logs_text.clear)
        logs_buttons.addWidget(clear_btn)
        
        logs_buttons.addStretch()
        layout.addLayout(logs_buttons)
        
        parent_layout.addWidget(group)
    
    def apply_theme(self):
        """Applique le thème actuel"""
        try:
            theme_manager = get_theme_manager()
            theme_manager.apply_theme(theme_manager.get_current_theme())
            self.log_message("✅ Thème appliqué avec succès")
        except Exception as e:
            self.log_message(f"❌ Erreur lors de l'application du thème: {e}")
    
    def change_theme(self, theme_key):
        """Change le thème de l'application"""
        try:
            theme_manager = get_theme_manager()
            theme_manager.apply_theme(theme_key)
            self.log_message(f"🎨 Thème changé vers: {theme_key}")
            self.statusBar().showMessage(f"Thème appliqué: {theme_key}")
        except Exception as e:
            self.log_message(f"❌ Erreur lors du changement de thème: {e}")
    
    def update_database_info(self):
        """Met à jour les informations de la base de données"""
        if not COMMON_AVAILABLE:
            self.db_info_label.setText("❌ Module Common non disponible")
            return
        
        try:
            if dbh and not dbh.is_closed():
                # Compter les enregistrements
                settings_count = Settings.select().count()
                owners_count = Owner.select().count() if Owner.select().count else 0
                orgs_count = Organization.select().count() if Organization.select().count else 0
                
                info_text = f"""
✅ Base de données connectée
📊 Paramètres: {settings_count} enregistrement(s)
👥 Propriétaires: {owners_count} enregistrement(s)
🏢 Organisations: {orgs_count} enregistrement(s)
"""
                self.db_info_label.setText(info_text.strip())
            else:
                self.db_info_label.setText("❌ Base de données déconnectée")
        except Exception as e:
            self.db_info_label.setText(f"❌ Erreur: {e}")
    
    def test_database(self):
        """Teste la connexion à la base de données"""
        if not COMMON_AVAILABLE:
            QMessageBox.warning(self, "Test impossible", "Module Common non disponible")
            return
        
        try:
            if dbh and not dbh.is_closed():
                # Test simple de requête
                count = Settings.select().count()
                QMessageBox.information(self, "Test de Connexion", 
                                      f"✅ Connexion OK!\nNombre de paramètres: {count}")
                self.log_message("✅ Test de base de données réussi")
            else:
                QMessageBox.warning(self, "Test de Connexion", 
                                  "❌ Base de données non connectée")
                self.log_message("❌ Test de base de données échoué")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"❌ Erreur lors du test:\n{e}")
            self.log_message(f"❌ Erreur test DB: {e}")
    
    def show_models(self):
        """Affiche les informations sur les modèles"""
        if not COMMON_AVAILABLE:
            return
        
        try:
            models_info = f"""
📊 Modèles disponibles dans le module Common:

• Settings (Paramètres): {Settings.select().count()} enregistrement(s)
• Owner (Propriétaires): {Owner.select().count()} enregistrement(s)
• Organization (Organisations): {Organization.select().count()} enregistrement(s)

📁 Base de données: database.db
🔧 ORM: Peewee
"""
            QMessageBox.information(self, "Modèles de Données", models_info)
            self.log_message("📊 Informations des modèles affichées")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération:\n{e}")
            self.log_message(f"❌ Erreur modèles: {e}")
    
    def show_settings(self):
        """Affiche les paramètres actuels"""
        if not COMMON_AVAILABLE:
            return
        
        try:
            settings = Settings.get_or_create(id=1)[0]
            settings_info = f"""
⚙️ Paramètres actuels:

• Thème: {settings.theme}
• Login requis: {'Oui' if settings.auth_required else 'Non'}
• Barre d'outils: {'Visible' if settings.toolbar else 'Cachée'}
• Position barre: {settings.toolbar_position}
• URL: {settings.url}
• Devise: {settings.devise}
"""
            QMessageBox.information(self, "Paramètres", settings_info)
            self.log_message("⚙️ Paramètres affichés")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération des paramètres:\n{e}")
            self.log_message(f"❌ Erreur paramètres: {e}")
    
    def test_logging(self):
        """Teste le système de logs"""
        if not COMMON_AVAILABLE:
            self.log_message("❌ Logs Common non disponibles")
            return
        
        try:
            logger.debug("Test de log DEBUG depuis la démonstration")
            logger.info("Test de log INFO depuis la démonstration")
            logger.warning("Test de log WARNING depuis la démonstration")
            logger.error("Test de log ERROR depuis la démonstration")
            
            self.log_message("📝 Logs de test envoyés (vérifiez la console/fichier de log)")
            QMessageBox.information(self, "Test Logs", 
                                  "✅ Logs de test envoyés!\nVérifiez la console ou le fichier de logs.")
        except Exception as e:
            self.log_message(f"❌ Erreur test logs: {e}")
    
    def test_notification(self):
        """Teste les notifications"""
        QMessageBox.information(self, "Test Notification", 
                              "🔔 Ceci est un test de notification!\nLe système de notifications fonctionne.")
        self.log_message("🔔 Test de notification réussi")
    
    def test_error(self):
        """Teste la gestion d'erreur"""
        try:
            # Déclencher une erreur volontairement
            raise ValueError("Ceci est une erreur de test volontaire")
        except Exception as e:
            QMessageBox.critical(self, "Test d'Erreur", 
                               f"⚠️ Erreur capturée avec succès:\n{e}")
            self.log_message(f"⚠️ Test d'erreur: {e}")
    
    def log_message(self, message):
        """Ajoute un message dans la zone de logs"""
        self.logs_text.append(f"[{self.logs_text.document().lineCount():03d}] {message}")
        
        # Faire défiler vers le bas
        cursor = self.logs_text.textCursor()
        cursor.movePosition(cursor.End)
        self.logs_text.setTextCursor(cursor)

def main():
    """Fonction principale"""
    print("🚀 === Démonstration Simple du Module Common ===")
    
    app = QApplication(sys.argv)
    
    # Configuration de l'application
    app.setApplicationName("Common Demo Simple")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Module Common")
    
    print(f"📦 Module Common disponible: {'Oui' if COMMON_AVAILABLE else 'Non'}")
    print(f"🎨 Widgets modernes disponibles: {'Oui' if MODERN_WIDGETS_AVAILABLE else 'Non'}")
    
    # Fenêtre principale
    window = CommonDemoSimple()
    window.show()
    
    print("🖥️ Fenêtre de démonstration ouverte!")
    print("👉 Testez les différentes fonctionnalités avec les boutons")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 