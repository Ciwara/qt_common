#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gestionnaire de styles pour l'application Qt
Compatible avec les anciens thèmes + nouveaux thèmes modernes
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

# ===== THÈMES EXISTANTS AMÉLIORÉS =====

# Thème par défaut amélioré
default = """
/* Thème par défaut amélioré */
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

# Thème bleu classique (simplifié)
blue_css = """
/* Thème Bleu Classique */
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

# Thème sombre corrigé
dark_css = """
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

# Thème bleu marine classique (simplifié)
bleu_mari_css = """
/* Thème Bleu Marine */
QMainWindow {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #1e3d59, stop: 1 #0f2027);
    color: white;
}

QToolBar {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #2e5266, stop: 1 #1e3d59);
    border: none;
    min-height: 48px;
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
}

QPushButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(255, 255, 255, 0.8), stop: 1 rgba(255, 255, 255, 0.6));
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 4px;
    color: #1e3d59;
    font-weight: bold;
    padding: 6px 12px;
}

QPushButton:hover {
    background: rgba(255, 178, 17, 0.8);
}

QLineEdit {
    background: white;
    border: 1px solid #2e5266;
    border-radius: 4px;
    padding: 6px 8px;
    color: #1e3d59;
}

QGroupBox {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #1e3d59, stop: 1 rgba(255, 255, 255, 0.9));
    border: 2px solid white;
    border-radius: 8px;
    font-weight: bold;
    color: white;
    margin-top: 1ex;
    padding-top: 16px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 8px;
    background: #1e3d59;
    color: white;
    font-weight: bold;
    border-radius: 4px;
    margin-left: 8px;
}
"""

def get_style():
    """Retourne le style CSS selon le thème sélectionné dans les paramètres"""
    # Dictionnaire des thèmes avec nouveaux styles modernes en priorité
    dic_t = {
        Settings.DF: default,
        Settings.BL: MODERN_LIGHT if MODERN_STYLES_AVAILABLE else blue_css,
        Settings.DK: MODERN_DARK if MODERN_STYLES_AVAILABLE else dark_css,
        Settings.FAD: bleu_mari_css,
        # Nouveaux thèmes modernes
        "MODERN_LIGHT": MODERN_LIGHT if MODERN_STYLES_AVAILABLE else default,
        "MODERN_DARK": MODERN_DARK if MODERN_STYLES_AVAILABLE else dark_css,
        # Thèmes classiques
        "CLASSIC_BLUE": blue_css,
        "CLASSIC_DARK": dark_css,
        "CLASSIC_NAVY": bleu_mari_css,
    }
    
    try:
        stt, created = Settings.get_or_create(id=1)
        if created:
            logger.info("Nouveaux paramètres créés avec le thème par défaut")
            
        selected_theme = dic_t.get(stt.theme, default)
        logger.debug(f"Thème sélectionné: {stt.theme}")
        
        # Si les styles modernes sont disponibles et qu'un thème moderne est demandé
        if MODERN_STYLES_AVAILABLE and stt.theme in [Settings.BL, Settings.DK]:
            if stt.theme == Settings.BL:
                logger.info("Application du thème moderne clair")
                return get_modern_style("light")
            elif stt.theme == Settings.DK:
                logger.info("Application du thème moderne sombre")
                return get_modern_style("dark")
                
        return selected_theme
        
    except Exception as exc:
        logger.error(f"Erreur lors de la récupération du style: {exc}")
        return default

# ===== FONCTIONS UTILITAIRES =====
def get_available_themes():
    """Retourne la liste de tous les thèmes disponibles"""
    themes = {
        Settings.DF: "Défaut amélioré",
        Settings.BL: "Moderne clair" if MODERN_STYLES_AVAILABLE else "Bleu classique",
        Settings.DK: "Moderne sombre" if MODERN_STYLES_AVAILABLE else "Sombre classique",
        Settings.FAD: "Bleu marine",
    }
    
    # Ajout des thèmes additionnels si les styles modernes sont disponibles
    if MODERN_STYLES_AVAILABLE:
        themes.update({
            "MODERN_LIGHT": "Moderne clair (Force)",
            "MODERN_DARK": "Moderne sombre (Force)",
            "CLASSIC_BLUE": "Bleu classique",
            "CLASSIC_DARK": "Sombre classique",
            "CLASSIC_NAVY": "Bleu marine classique",
        })
    
    return themes

def apply_theme(theme_key):
    """Applique un thème spécifique"""
    try:
        settings = Settings.get_or_create(id=1)[0]
        settings.theme = theme_key
        settings.save()
        logger.info(f"Thème changé vers: {theme_key}")
        return get_style()
    except Exception as exc:
        logger.error(f"Erreur lors du changement de thème: {exc}")
        return default

def is_dark_theme(theme_key=None):
    """Détermine si le thème actuel ou spécifié est sombre"""
    if theme_key is None:
        try:
            settings = Settings.get_or_create(id=1)[0]
            theme_key = settings.theme
        except:
            return False
    
    dark_themes = [Settings.DK, "MODERN_DARK", "CLASSIC_DARK"]
    return theme_key in dark_themes

def get_theme_info():
    """Retourne des informations sur le thème actuel"""
    try:
        settings = Settings.get_or_create(id=1)[0]
        current_theme = settings.theme
        available_themes = get_available_themes()
        
        return {
            "current": current_theme,
            "name": available_themes.get(current_theme, "Inconnu"),
            "is_dark": is_dark_theme(current_theme),
            "modern_available": MODERN_STYLES_AVAILABLE,
            "available_themes": available_themes
        }
    except Exception as exc:
        logger.error(f"Erreur lors de la récupération des infos du thème: {exc}")
        return {
            "current": Settings.DF,
            "name": "Défaut",
            "is_dark": False,
            "modern_available": False,
            "available_themes": {Settings.DF: "Défaut"}
        }

# Obtention du thème actuel
theme = get_style()

# Log des informations sur les thèmes au démarrage
logger.info(f"Gestionnaire de styles initialisé. Styles modernes: {'Disponibles' if MODERN_STYLES_AVAILABLE else 'Non disponibles'}")
theme_info = get_theme_info()
logger.info(f"Thème actuel: {theme_info['name']} ({'Sombre' if theme_info['is_dark'] else 'Clair'})")
