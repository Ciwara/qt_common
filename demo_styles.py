#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Démonstration des styles modernes de l'application Qt
Ce fichier permet de tester les nouveaux thèmes et widgets
"""

import sys
import os

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QTabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import des nouveaux modules de styles
try:
    from Common.ui.style_manager import get_style, apply_theme, get_available_themes, ThemeNames
    from Common.ui.modern_widgets import (
        ModernButton, ModernLineEdit, ModernComboBox, ModernGroupBox,
        ModernCard, LoadingSpinner, StatusIndicator, ModernWidgetShowcase
    )
    MODERN_STYLES_AVAILABLE = True
except ImportError as e:
    print(f"Erreur d'import: {e}")
    MODERN_STYLES_AVAILABLE = False

class StyleDemoWindow(QMainWindow):
    """Fenêtre de démonstration des styles"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Démonstration des Styles Modernes - Qt Application")
        self.setMinimumSize(1000, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête avec sélecteur de thème
        self.create_header(main_layout)
        
        # Contenu principal avec onglets
        self.create_content_tabs(main_layout)
        
        # Appliquer le thème par défaut
        if MODERN_STYLES_AVAILABLE:
            self.apply_current_theme()
    
    def create_header(self, parent_layout):
        """Crée l'en-tête avec les contrôles de thème"""
        header_card = ModernCard() if MODERN_STYLES_AVAILABLE else QWidget()
        
        if MODERN_STYLES_AVAILABLE:
            header_card.add_title("Démonstration des Styles Modernes", 
                                "Sélectionnez un thème pour voir les changements en temps réel")
        else:
            title = QLabel("Démonstration des Styles (Mode Basique)")
            title.setFont(QFont("Arial", 16, QFont.Bold))
            header_layout = QVBoxLayout(header_card)
            header_layout.addWidget(title)
        
        # Boutons de sélection de thème
        theme_layout = QHBoxLayout()
        
        if MODERN_STYLES_AVAILABLE:
            themes = get_available_themes()
            for theme_key, theme_name in themes.items():
                btn = ModernButton(theme_name, button_type="default")
                btn.clicked.connect(lambda checked, key=theme_key: self.change_theme(key))
                theme_layout.addWidget(btn)
        else:
            # Boutons basiques si les styles modernes ne sont pas disponibles
            basic_btn = QPushButton("Thème de base seulement")
            basic_btn.setEnabled(False)
            theme_layout.addWidget(basic_btn)
        
        theme_layout.addStretch()
        
        theme_widget = QWidget()
        theme_widget.setLayout(theme_layout)
        
        if MODERN_STYLES_AVAILABLE:
            header_card.add_widget(theme_widget)
        else:
            header_layout.addWidget(theme_widget)
        
        parent_layout.addWidget(header_card)
    
    def create_content_tabs(self, parent_layout):
        """Crée le contenu principal avec des onglets de démonstration"""
        if MODERN_STYLES_AVAILABLE:
            tab_widget = QTabWidget()
        else:
            tab_widget = QTabWidget()
        
        # Onglet 1: Widgets modernes
        if MODERN_STYLES_AVAILABLE:
            modern_tab = self.create_modern_widgets_tab()
            tab_widget.addTab(modern_tab, "Widgets Modernes")
        
        # Onglet 2: Composants classiques
        classic_tab = self.create_classic_widgets_tab()
        tab_widget.addTab(classic_tab, "Widgets Classiques")
        
        # Onglet 3: Démonstration complète
        if MODERN_STYLES_AVAILABLE:
            showcase_tab = ModernWidgetShowcase()
            tab_widget.addTab(showcase_tab, "Showcase Complet")
        
        parent_layout.addWidget(tab_widget)
    
    def create_modern_widgets_tab(self):
        """Crée l'onglet des widgets modernes"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(20)
        
        # Boutons modernes
        button_card = ModernCard()
        button_card.add_title("Boutons Modernes", "Différents types de boutons avec animations")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(ModernButton("Défaut", button_type="default"))
        button_layout.addWidget(ModernButton("Primaire", button_type="primary"))
        button_layout.addWidget(ModernButton("Succès", button_type="success"))
        button_layout.addWidget(ModernButton("Danger", button_type="danger"))
        
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        button_card.add_widget(button_widget)
        layout.addWidget(button_card)
        
        # Champs de saisie modernes
        input_card = ModernCard()
        input_card.add_title("Champs de Saisie", "Inputs avec design moderne")
        
        input_card.add_widget(ModernLineEdit("Nom d'utilisateur"))
        input_card.add_widget(ModernLineEdit("Adresse email"))
        
        combo = ModernComboBox()
        combo.addItems(["Thème clair", "Thème sombre", "Automatique"])
        input_card.add_widget(combo)
        
        layout.addWidget(input_card)
        
        # Groupe moderne
        group = ModernGroupBox("Configuration Avancée")
        group_layout = QVBoxLayout(group)
        group_layout.addWidget(ModernLineEdit("Paramètre 1"))
        group_layout.addWidget(ModernLineEdit("Paramètre 2"))
        layout.addWidget(group)
        
        # Indicateurs de statut
        status_card = ModernCard()
        status_card.add_title("Indicateurs de Statut", "Différents états visuels")
        
        status_layout = QHBoxLayout()
        
        status_layout.addWidget(QLabel("Actif:"))
        active_indicator = StatusIndicator("active")
        status_layout.addWidget(active_indicator)
        
        status_layout.addWidget(QLabel("Traitement:"))
        processing_indicator = StatusIndicator("processing")
        status_layout.addWidget(processing_indicator)
        
        status_layout.addWidget(QLabel("Erreur:"))
        status_layout.addWidget(StatusIndicator("error"))
        
        status_layout.addWidget(QLabel("Chargement:"))
        spinner = LoadingSpinner(24)
        spinner.start()
        status_layout.addWidget(spinner)
        
        status_layout.addStretch()
        
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        status_card.add_widget(status_widget)
        layout.addWidget(status_card)
        
        layout.addStretch()
        return tab_widget
    
    def create_classic_widgets_tab(self):
        """Crée l'onglet des widgets classiques"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(20)
        
        # Titre
        title = QLabel("Widgets Qt Classiques")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Boutons classiques
        classic_group = QWidget()
        classic_layout = QVBoxLayout(classic_group)
        
        classic_layout.addWidget(QLabel("Boutons classiques:"))
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("Bouton 1"))
        button_layout.addWidget(QPushButton("Bouton 2"))
        button_layout.addWidget(QPushButton("Bouton 3"))
        button_layout.addStretch()
        
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        classic_layout.addWidget(button_widget)
        
        # Champs classiques
        classic_layout.addWidget(QLabel("Champs de saisie classiques:"))
        from PyQt5.QtWidgets import QLineEdit, QComboBox
        
        classic_input = QLineEdit()
        classic_input.setPlaceholderText("Champ de saisie classique")
        classic_layout.addWidget(classic_input)
        
        classic_combo = QComboBox()
        classic_combo.addItems(["Option A", "Option B", "Option C"])
        classic_layout.addWidget(classic_combo)
        
        layout.addWidget(classic_group)
        layout.addStretch()
        
        return tab_widget
    
    def change_theme(self, theme_key):
        """Change le thème de l'application"""
        if MODERN_STYLES_AVAILABLE:
            try:
                new_style = apply_theme(theme_key)
                self.setStyleSheet(new_style)
                print(f"Thème changé vers: {theme_key}")
            except Exception as e:
                print(f"Erreur lors du changement de thème: {e}")
    
    def apply_current_theme(self):
        """Applique le thème actuel"""
        if MODERN_STYLES_AVAILABLE:
            try:
                current_style = get_style()
                self.setStyleSheet(current_style)
                print("Thème appliqué avec succès")
            except Exception as e:
                print(f"Erreur lors de l'application du thème: {e}")

def main():
    """Fonction principale"""
    print("=== Démonstration des Styles Modernes ===")
    print(f"Styles modernes disponibles: {'Oui' if MODERN_STYLES_AVAILABLE else 'Non'}")
    
    app = QApplication(sys.argv)
    
    # Configuration de l'application
    app.setApplicationName("Style Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Modern Qt Styles")
    
    # Fenêtre principale
    window = StyleDemoWindow()
    window.show()
    
    print("Fenêtre de démonstration ouverte. Testez les différents thèmes !")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 