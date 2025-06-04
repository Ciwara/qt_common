#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exemples d'utilisation des composants Common
Démonstration de FDialog, FWidget, FMenuBar et autres composants
"""

import sys
import os
from pathlib import Path

# Ajout du répertoire src au PYTHONPATH
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTextEdit, QMessageBox, QFormLayout, QListWidget,
    QGroupBox, QCheckBox, QSpinBox, QDateEdit, QComboBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon

# Import des composants Common
try:
    from Common.ui.common import FMainWindow, FWidget, FDialog
    from Common.ui.cmenubar import FMenuBar
    from Common.ui.modern_widgets import (
        ModernButton, ModernLineEdit, ModernCard, StatusIndicator
    )
    from Common.cstatic import logger
    from Common.models import Settings, Organization, Owner
    COMMON_AVAILABLE = True
    print("✅ Composants Common importés avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    COMMON_AVAILABLE = False

# ===== EXEMPLE DE FDIALOG =====

class ExampleDialog(FDialog):
    """Exemple d'utilisation de FDialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exemple de FDialog")
        self.setMinimumSize(400, 300)
        self.init_ui()
        
    def init_ui(self):
        """Initialise l'interface du dialog"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête
        title = QLabel("🔧 Exemple de FDialog")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Description
        description = QLabel("""
        Ce dialog hérite de FDialog qui combine QDialog et FWidget.
        Il peut accéder aux méthodes de la fenêtre principale via:
        - self.change_main_context() pour changer le contexte principal
        - self.open_dialog() pour ouvrir d'autres dialogs
        """)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Formulaire d'exemple
        form_group = QGroupBox("Formulaire d'Exemple")
        form_layout = QFormLayout(form_group)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Entrez votre nom")
        form_layout.addRow("Nom:", self.name_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("votre.email@example.com")
        form_layout.addRow("Email:", self.email_input)
        
        self.age_input = QSpinBox()
        self.age_input.setRange(1, 120)
        self.age_input.setValue(25)
        form_layout.addRow("Âge:", self.age_input)
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_input)
        
        layout.addWidget(form_group)
        
        # Zone de résultat
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(100)
        self.result_text.setPlaceholderText("Les résultats s'afficheront ici...")
        layout.addWidget(self.result_text)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        test_btn = QPushButton("📊 Tester les Données")
        test_btn.clicked.connect(self.test_data)
        buttons_layout.addWidget(test_btn)
        
        dialog_btn = QPushButton("🔍 Ouvrir Sous-Dialog")
        dialog_btn.clicked.connect(self.open_sub_dialog)
        buttons_layout.addWidget(dialog_btn)
        
        close_btn = QPushButton("✅ Fermer")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def test_data(self):
        """Teste les données saisies"""
        name = self.name_input.text()
        email = self.email_input.text()
        age = self.age_input.value()
        date = self.date_input.date().toString("dd/MM/yyyy")
        
        result = f"""
📝 Données saisies:
• Nom: {name or "Non spécifié"}
• Email: {email or "Non spécifié"}
• Âge: {age} ans
• Date: {date}

✅ Validation: {"OK" if name and email else "Données incomplètes"}
"""
        self.result_text.setText(result)
        logger.info(f"Test des données: {name}, {email}, {age} ans")
    
    def open_sub_dialog(self):
        """Ouvre un sous-dialog"""
        sub_dialog = SimpleSubDialog(self)
        result = sub_dialog.exec_()
        if result:
            self.result_text.append("\n🔍 Sous-dialog fermé avec succès")

class SimpleSubDialog(FDialog):
    """Sous-dialog simple"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sous-Dialog")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        
        label = QLabel("🎯 Ceci est un sous-dialog!")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        info = QLabel("Il hérite aussi de FDialog")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)

# ===== EXEMPLE DE FWIDGET =====

class ExampleWidget(FWidget):
    """Exemple d'utilisation de FWidget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Utilisation des méthodes de FWidget
        self.page_names("Exemples Common", "Widget de Démonstration")
        logger.info("ExampleWidget initialisé")
        
    def init_ui(self):
        """Initialise l'interface du widget"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête
        title = QLabel("📱 Exemple de FWidget")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Description
        description = QLabel("""
        Ce widget hérite de FWidget qui étend QWidget avec des fonctionnalités supplémentaires:
        • Accès au parent via self.pp
        • Méthode page_names() pour définir le titre de la fenêtre
        • change_main_context() pour changer le contexte principal
        • open_dialog() pour ouvrir des dialogs
        • refresh() pour actualiser le contenu
        """)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Section fonctionnalités
        features_group = QGroupBox("🔧 Fonctionnalités FWidget")
        features_layout = QVBoxLayout(features_group)
        
        # Boutons de test
        buttons_layout = QHBoxLayout()
        
        dialog_btn = QPushButton("📝 Ouvrir Dialog")
        dialog_btn.clicked.connect(self.test_open_dialog)
        buttons_layout.addWidget(dialog_btn)
        
        context_btn = QPushButton("🔄 Changer Contexte")
        context_btn.clicked.connect(self.test_change_context)
        buttons_layout.addWidget(context_btn)
        
        refresh_btn = QPushButton("🔃 Refresh")
        refresh_btn.clicked.connect(self.refresh)
        buttons_layout.addWidget(refresh_btn)
        
        features_layout.addLayout(buttons_layout)
        
        # Informations dynamiques
        self.info_label = QLabel("Cliquez sur les boutons pour tester les fonctionnalités")
        self.info_label.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 5px;")
        features_layout.addWidget(self.info_label)
        
        layout.addWidget(features_group)
        
        # Section base de données
        if COMMON_AVAILABLE:
            db_group = QGroupBox("🗃️ Données du Module Common")
            db_layout = QFormLayout(db_group)
            
            try:
                settings_count = Settings.select().count()
                owners_count = Owner.select().count()
                orgs_count = Organization.select().count()
                
                db_layout.addRow("Paramètres:", QLabel(f"{settings_count} enregistrement(s)"))
                db_layout.addRow("Propriétaires:", QLabel(f"{owners_count} enregistrement(s)"))
                db_layout.addRow("Organisations:", QLabel(f"{orgs_count} enregistrement(s)"))
            except Exception as e:
                db_layout.addRow("Erreur:", QLabel(str(e)))
            
            layout.addWidget(db_group)
        
        # Zone de logs/messages
        self.messages_text = QTextEdit()
        self.messages_text.setMaximumHeight(150)
        self.messages_text.setPlaceholderText("Les messages et logs s'afficheront ici...")
        layout.addWidget(self.messages_text)
        
        layout.addStretch()
    
    def test_open_dialog(self):
        """Teste l'ouverture d'un dialog"""
        try:
            self.open_dialog(ExampleDialog, modal=True)
            self.info_label.setText("✅ Dialog ouvert avec succès!")
            self.messages_text.append("📝 Dialog ExampleDialog ouvert")
            logger.info("Dialog ouvert depuis ExampleWidget")
        except Exception as e:
            self.info_label.setText(f"❌ Erreur: {e}")
            self.messages_text.append(f"❌ Erreur dialog: {e}")
    
    def test_change_context(self):
        """Teste le changement de contexte"""
        try:
            # Changer vers un autre widget d'exemple
            self.change_main_context(AnotherExampleWidget)
            logger.info("Contexte changé vers AnotherExampleWidget")
        except Exception as e:
            self.info_label.setText(f"❌ Erreur changement contexte: {e}")
            self.messages_text.append(f"❌ Erreur contexte: {e}")
    
    def refresh(self):
        """Actualise le contenu du widget"""
        self.info_label.setText("🔃 Widget actualisé!")
        self.messages_text.append(f"🔃 Actualisation à {QDate.currentDate().toString()}")
        logger.info("ExampleWidget actualisé")

class AnotherExampleWidget(FWidget):
    """Autre exemple de FWidget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_names("Exemples Common", "Autre Widget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("🎯 Autre Widget d'Exemple")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        info = QLabel("Ceci démontre le changement de contexte entre widgets")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        back_btn = QPushButton("🔙 Retour au Widget Principal")
        back_btn.clicked.connect(lambda: self.change_main_context(ExampleWidget))
        layout.addWidget(back_btn)
        
        layout.addStretch()

# ===== EXEMPLE DE FMAINWINDOW AVEC FMENUBAR =====

class ExampleMainWindow(FMainWindow):
    """Exemple de fenêtre principale avec FMenuBar"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exemples des Composants Common")
        self.setMinimumSize(800, 600)
        
        # Initialisation du menu bar (hérite de FMenuBar)
        if COMMON_AVAILABLE:
            try:
                self.menubar = FMenuBar(self)
                self.setMenuBar(self.menubar)
                logger.info("FMenuBar initialisé avec succès")
            except Exception as e:
                logger.error(f"Erreur initialisation FMenuBar: {e}")
                # Menu bar basique en fallback
                self.create_basic_menubar()
        else:
            self.create_basic_menubar()
        
        # Widget central par défaut
        self.change_context(ExampleWidget)
        
        # Barre de statut avec message
        self.statusBar().showMessage("Prêt - Exemples des composants Common")
    
    def create_basic_menubar(self):
        """Crée un menu bar basique si FMenuBar n'est pas disponible"""
        from PyQt5.QtWidgets import QMenuBar, QAction
        
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        
        # Menu Fichier
        file_menu = menubar.addMenu('Fichier')
        
        exit_action = QAction('Quitter', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Exemples
        examples_menu = menubar.addMenu('Exemples')
        
        widget_action = QAction('Widget Principal', self)
        widget_action.triggered.connect(lambda: self.change_context(ExampleWidget))
        examples_menu.addAction(widget_action)
        
        dialog_action = QAction('Test Dialog', self)
        dialog_action.triggered.connect(self.test_dialog)
        examples_menu.addAction(dialog_action)
    
    def test_dialog(self):
        """Teste l'ouverture d'un dialog"""
        dialog = ExampleDialog(self)
        dialog.exec_()

# ===== EXEMPLES AVEC WIDGETS MODERNES =====

class ModernExamplesWidget(FWidget):
    """Widget combinant composants Common et widgets modernes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_names("Exemples Common", "Widgets Modernes + Common")
        self.init_ui()
    
    def init_ui(self):
        """Interface avec widgets modernes et Common"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title = QLabel("🎨 Widgets Modernes + Common")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        if COMMON_AVAILABLE:
            # Carte moderne avec widgets Common
            card = ModernCard()
            card.add_title("Combinaison des Composants", "FWidget + Widgets Modernes")
            
            # Formulaire avec widgets modernes
            form_layout = QVBoxLayout()
            
            form_layout.addWidget(ModernLineEdit("Champ moderne dans FWidget"))
            
            combo = QComboBox()
            combo.addItems(["Option 1", "Option 2", "Option 3"])
            form_layout.addWidget(combo)
            
            # Boutons modernes
            buttons_layout = QHBoxLayout()
            buttons_layout.addWidget(ModernButton("Action Principale", button_type="primary"))
            buttons_layout.addWidget(ModernButton("Action Secondaire", button_type="default"))
            
            form_widget = FWidget()  # Widget Common comme conteneur
            form_widget.setLayout(buttons_layout)
            form_layout.addWidget(form_widget)
            
            # Indicateurs
            status_layout = QHBoxLayout()
            status_layout.addWidget(QLabel("États:"))
            status_layout.addWidget(StatusIndicator("active"))
            status_layout.addWidget(StatusIndicator("processing"))
            status_layout.addWidget(StatusIndicator("error"))
            status_layout.addStretch()
            form_layout.addLayout(status_layout)
            
            card_widget = FWidget()  # Conteneur Common
            card_widget.setLayout(form_layout)
            card.add_widget(card_widget)
            
            layout.addWidget(card)
        else:
            error_label = QLabel("❌ Widgets modernes non disponibles")
            error_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(error_label)
        
        layout.addStretch()

# ===== FONCTION PRINCIPALE =====

def main():
    """Fonction principale de démonstration"""
    print("🚀 === Exemples des Composants Common ===")
    print(f"Module Common disponible: {'Oui' if COMMON_AVAILABLE else 'Non'}")
    
    app = QApplication(sys.argv)
    
    # Configuration de l'application
    app.setApplicationName("Exemples Common Widgets")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Common Components Demo")
    
    # Fenêtre principale
    window = ExampleMainWindow()
    window.show()
    
    print("🖥️ Interface d'exemples ouverte!")
    print("""
📝 Composants démontrés:
• FMainWindow - Fenêtre principale avec fonctionnalités Common
• FMenuBar - Barre de menu avec actions prédéfinies
• FWidget - Widget étendu avec méthodes utiles
• FDialog - Dialog avec accès aux méthodes du parent
• Combinaison avec widgets modernes
    """)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 