#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gestionnaire de styles pour l'application Qt
Système de thèmes simplifié et moderne
"""

from ..models import Settings
from ..cstatic import logger

# Import des nouveaux styles modernes
try:
    from .modern_styles import get_modern_style, MODERN_LIGHT, MODERN_DARK
    MODERN_STYLES_AVAILABLE = True
except ImportError:
    logger.warning("Les styles modernes ne sont pas disponibles")
    MODERN_STYLES_AVAILABLE = False
    MODERN_LIGHT = ""
    MODERN_DARK = ""

# ===== THÈMES CSS INTÉGRÉS =====

# Thème par défaut moderne
default_theme = """
/* Thème par défaut moderne */
QMainWindow {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #ffffff, stop: 1 #f5f5f5);
    color: #333333;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

QPushButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #ffffff, stop: 1 #e0e0e0);
    border: 1px solid #cccccc;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 24px;
}

QPushButton:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #f0f0f0, stop: 1 #d0d0d0);
    border-color: #999999;
}

QPushButton:pressed {
    background: #d0d0d0;
    border-color: #666666;
}

QLineEdit {
    background: white;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 6px 8px;
    selection-background-color: #0078d4;
    font-size: 14px;
}

QLineEdit:focus {
    border-color: #0078d4;
    outline: none;
}

QGroupBox {
    background: white;
    border: 2px solid #0078d4;
    border-radius: 8px;
    font-weight: bold;
    color: #333333;
    margin-top: 1ex;
    padding-top: 16px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 8px;
    background: #0078d4;
    color: white;
    font-weight: bold;
    border-radius: 4px;
    margin-left: 8px;
}

QTableView {
    background: white;
    alternate-background-color: #f8f9fa;
    gridline-color: #e9ecef;
    border: 1px solid #dee2e6;
    selection-background-color: #0078d4;
    selection-color: white;
}

QHeaderView::section {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #f8f9fa, stop: 1 #e9ecef);
    border: none;
    border-right: 1px solid #dee2e6;
    border-bottom: 1px solid #dee2e6;
    padding: 8px 12px;
    font-weight: bold;
    color: #495057;
}
"""

# Thème clair moderne
light_modern_theme = """
/* Thème Clair Moderne */
QMainWindow {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #4a90e2, stop: 1 #2171b5);
    color: white;
}

QToolBar {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #5ba0f2, stop: 1 #4a90e2);
    border: none;
    min-height: 48px;
    spacing: 4px;
    padding: 8px;
}

QToolButton {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    color: white;
    font-weight: bold;
    padding: 8px 12px;
    min-height: 32px;
    min-width: 32px;
}

QToolButton:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.4);
}

QToolButton:checked {
    background: rgba(255, 255, 255, 0.3);
}

QPushButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(255, 255, 255, 0.8), stop: 1 rgba(255, 255, 255, 0.6));
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 4px;
    color: #2c3e50;
    font-weight: bold;
    padding: 6px 12px;
    min-height: 24px;
}

QPushButton:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(255, 255, 255, 0.9), stop: 1 rgba(255, 255, 255, 0.7));
}

QLineEdit {
    background: white;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 6px 8px;
    color: #2c3e50;
    selection-background-color: #3498db;
}

QGroupBox {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(255, 255, 255, 0.9), stop: 1 rgba(255, 255, 255, 0.7));
    border: 2px solid white;
    border-radius: 8px;
    font-weight: bold;
    color: #2c3e50;
    margin-top: 1ex;
    padding-top: 16px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 8px;
    background: #3498db;
    color: white;
    font-weight: bold;
    border-radius: 4px;
    margin-left: 8px;
}
"""

# Thème sombre moderne
dark_modern_theme = """
/* Thème Sombre Moderne */
QMainWindow {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #2c3e50, stop: 1 #1a252f);
    color: #ecf0f1;
    font-family: "Segoe UI", Arial, sans-serif;
}

QToolBar {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #34495e, stop: 1 #2c3e50);
    border: none;
    min-height: 48px;
    spacing: 4px;
    padding: 8px;
}

QToolButton {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    color: #ecf0f1;
    font-weight: bold;
    padding: 8px 12px;
    min-height: 32px;
    min-width: 32px;
}

QToolButton:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.4);
}

QToolButton:checked {
    background: #3498db;
    border-color: #3498db;
}

QPushButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #34495e, stop: 1 #2c3e50);
    border: 1px solid #4a6574;
    border-radius: 4px;
    color: #ecf0f1;
    font-weight: bold;
    padding: 6px 12px;
    min-height: 24px;
}

QPushButton:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #4a6574, stop: 1 #34495e);
    border-color: #5d737e;
}

QPushButton:pressed {
    background: #2c3e50;
    border-color: #34495e;
}

QLineEdit {
    background: #34495e;
    border: 1px solid #4a6574;
    border-radius: 4px;
    padding: 6px 8px;
    color: #ecf0f1;
    selection-background-color: #3498db;
}

QLineEdit:focus {
    border-color: #3498db;
}

QGroupBox {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #34495e, stop: 1 #2c3e50);
    border: 2px solid #4a6574;
    border-radius: 8px;
    font-weight: bold;
    color: #ecf0f1;
    margin-top: 1ex;
    padding-top: 16px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 8px;
    background: #3498db;
    color: white;
    font-weight: bold;
    border-radius: 4px;
    margin-left: 8px;
}

QTableView {
    background: #34495e;
    alternate-background-color: #2c3e50;
    gridline-color: #4a6574;
    border: 1px solid #4a6574;
    selection-background-color: #3498db;
    selection-color: white;
    color: #ecf0f1;
}

QHeaderView::section {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #4a6574, stop: 1 #34495e);
    border: none;
    border-right: 1px solid #5d737e;
    border-bottom: 1px solid #5d737e;
    padding: 8px 12px;
    font-weight: bold;
    color: #ecf0f1;
}

QScrollBar:vertical {
    background: #2c3e50;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #4a6574;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #5d737e;
}

QScrollBar:horizontal {
    background: #2c3e50;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: #4a6574;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background: #5d737e;
}
"""

# ===== CONFIGURATION DES THÈMES =====

# Dictionnaire principal des thèmes disponibles
AVAILABLE_THEMES = {
    "default": {
        "name": "Défaut",
        "css": default_theme,
        "is_dark": False
    },
    "light_modern": {
        "name": "Moderne Clair", 
        "css": MODERN_LIGHT if MODERN_STYLES_AVAILABLE else light_modern_theme,
        "is_dark": False
    },
    "dark_modern": {
        "name": "Moderne Sombre",
        "css": MODERN_DARK if MODERN_STYLES_AVAILABLE else dark_modern_theme,
        "is_dark": True
    }
}

# ===== FONCTIONS PRINCIPALES =====

def get_style():
    """Retourne le style CSS selon le thème sélectionné dans les paramètres"""
    try:
        settings, created = Settings.get_or_create(id=1)
        if created:
            logger.info("Nouveaux paramètres créés avec le thème par défaut")
            
        current_theme = settings.theme
        
        # Vérifier si le thème existe, sinon utiliser le thème par défaut
        if current_theme not in AVAILABLE_THEMES:
            logger.warning(f"Thème '{current_theme}' non trouvé, utilisation du thème par défaut")
            current_theme = "default"
            settings.theme = current_theme
            settings.save()
            
        theme_config = AVAILABLE_THEMES[current_theme]
        logger.debug(f"Thème sélectionné: {current_theme} ({theme_config['name']})")
        
        # Si les styles modernes sont disponibles et le thème le supporte
        if MODERN_STYLES_AVAILABLE and current_theme in ["light_modern", "dark_modern"]:
            if current_theme == "light_modern":
                logger.info("Application du style moderne clair")
                return get_modern_style("light")
            elif current_theme == "dark_modern":
                logger.info("Application du style moderne sombre")
                return get_modern_style("dark")
                
        return theme_config["css"]
        
    except Exception as exc:
        logger.error(f"Erreur lors de la récupération du style: {exc}")
        return default_theme

def get_available_themes():
    """Retourne la liste de tous les thèmes disponibles"""
    return {key: config["name"] for key, config in AVAILABLE_THEMES.items()}

def apply_theme(theme_key):
    """Applique un thème spécifique"""
    try:
        if theme_key not in AVAILABLE_THEMES:
            logger.error(f"Thème '{theme_key}' non disponible")
            return default_theme
            
        settings = Settings.get_or_create(id=1)[0]
        settings.theme = theme_key
        settings.save()
        logger.info(f"Thème changé vers: {theme_key}")
        return get_style()
        
    except Exception as exc:
        logger.error(f"Erreur lors du changement de thème: {exc}")
        return default_theme

def is_dark_theme(theme_key=None):
    """Détermine si le thème actuel ou spécifié est sombre"""
    if theme_key is None:
        try:
            settings = Settings.get_or_create(id=1)[0]
            theme_key = settings.theme
        except:
            return False
    
    if theme_key in AVAILABLE_THEMES:
        return AVAILABLE_THEMES[theme_key]["is_dark"]
    return False

def get_theme_info():
    """Retourne des informations complètes sur le thème actuel"""
    try:
        settings = Settings.get_or_create(id=1)[0]
        current_theme = settings.theme
        
        if current_theme not in AVAILABLE_THEMES:
            current_theme = "default"
            
        theme_config = AVAILABLE_THEMES[current_theme]
        
        return {
            "current": current_theme,
            "name": theme_config["name"],
            "is_dark": theme_config["is_dark"],
            "modern_available": MODERN_STYLES_AVAILABLE,
            "available_themes": get_available_themes()
        }
        
    except Exception as exc:
        logger.error(f"Erreur lors de la récupération des infos du thème: {exc}")
        return {
            "current": "default",
            "name": "Défaut",
            "is_dark": False,
            "modern_available": False,
            "available_themes": {"default": "Défaut"}
        }

# ===== INITIALISATION =====

# Obtention du thème actuel
theme = get_style()

# Log des informations de démarrage
logger.info(f"Gestionnaire de styles initialisé. Styles modernes: {'Disponibles' if MODERN_STYLES_AVAILABLE else 'Non disponibles'}")
theme_info = get_theme_info()
logger.info(f"Thème actuel: {theme_info['name']} ({'Sombre' if theme_info['is_dark'] else 'Clair'})")
