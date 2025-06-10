#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Styles CSS pour tous les thèmes
Version 2.0 - Styles nettoyés et optimisés
"""

from ...cstatic import logger
from .config import get_current_theme, is_theme_dark

# ===== COULEURS ET CONSTANTES =====

class Colors:
    """Palette de couleurs commune à tous les thèmes"""
    # Couleurs neutres
    WHITE = "#ffffff"
    LIGHT_GRAY = "#f8f9fa"
    GRAY = "#6c757d"
    DARK_GRAY = "#343a40"
    BLACK = "#000000"
    
    # Couleurs primaires
    BLUE_PRIMARY = "#0d6efd"
    GREEN_PRIMARY = "#198754"
    RED_PRIMARY = "#dc3545"
    YELLOW_PRIMARY = "#ffc107"
    
    # Couleurs pour thème sombre
    DARK_BG = "#1a202c"
    DARK_SURFACE = "#2d3748"
    DARK_BORDER = "#4a5568"
    DARK_TEXT = "#e2e8f0"

# ===== STYLES DE BASE =====

def get_base_styles():
    """Styles de base communs à tous les thèmes"""
    return """
    /* Styles de base pour tous les thèmes */
    * {
        font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    }
    
    QWidget {
        font-size: 14px;
        outline: none;
    }
    
    /* Animation et transitions */
    QPushButton, QLineEdit, QComboBox {
        transition: all 0.2s ease;
    }
    """

# ===== THÈME PAR DÉFAUT =====

def get_default_theme_styles():
    """Styles pour le thème par défaut"""
    return f"""
    {get_base_styles()}
    
    /* Thème par défaut - Simple et compatible */
    QMainWindow {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.WHITE}, stop: 1 {Colors.LIGHT_GRAY});
        color: #333333;
    }}

    QPushButton {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.WHITE}, stop: 1 #e0e0e0);
        border: 1px solid #cccccc;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
        min-height: 24px;
    }}

    QPushButton:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #f0f0f0, stop: 1 #d0d0d0);
        border-color: #999999;
    }}

    QPushButton:pressed {{
        background: #d0d0d0;
        border-color: #666666;
    }}

    QLineEdit {{
        background: {Colors.WHITE};
        border: 1px solid #cccccc;
        border-radius: 4px;
        padding: 6px 8px;
        selection-background-color: {Colors.BLUE_PRIMARY};
    }}

    QLineEdit:focus {{
        border-color: {Colors.BLUE_PRIMARY};
    }}

    QGroupBox {{
        background: {Colors.WHITE};
        border: 2px solid {Colors.BLUE_PRIMARY};
        border-radius: 8px;
        font-weight: bold;
        color: #333333;
        margin-top: 1ex;
        padding-top: 16px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 4px 8px;
        background: {Colors.BLUE_PRIMARY};
        color: {Colors.WHITE};
        font-weight: bold;
        border-radius: 4px;
        margin-left: 8px;
    }}

    QTableView {{
        background: {Colors.WHITE};
        alternate-background-color: {Colors.LIGHT_GRAY};
        gridline-color: #e9ecef;
        border: 1px solid #dee2e6;
        selection-background-color: {Colors.BLUE_PRIMARY};
        selection-color: {Colors.WHITE};
    }}

    QHeaderView::section {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.LIGHT_GRAY}, stop: 1 #e9ecef);
        border: none;
        border-right: 1px solid #dee2e6;
        border-bottom: 1px solid #dee2e6;
        padding: 8px 12px;
        font-weight: bold;
        color: #495057;
    }}
    """

# ===== THÈME MODERNE CLAIR =====

def get_light_modern_theme_styles():
    """Styles pour le thème moderne clair"""
    return f"""
    {get_base_styles()}
    
    /* Thème moderne clair - Interface élégante */
    QMainWindow {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.WHITE}, stop: 1 #f1f5f9);
        color: #1e293b;
    }}

    QPushButton {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.WHITE}, stop: 1 #f8fafc);
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        min-height: 28px;
        color: #475569;
    }}

    QPushButton:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #f8fafc, stop: 1 #e2e8f0);
        border-color: {Colors.BLUE_PRIMARY};
        color: {Colors.BLUE_PRIMARY};
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(13, 110, 253, 0.15);
    }}

    QPushButton:pressed {{
        background: #e2e8f0;
        transform: translateY(0px);
    }}

    QLineEdit {{
        background: {Colors.WHITE};
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        selection-background-color: {Colors.BLUE_PRIMARY};
    }}

    QLineEdit:focus {{
        border-color: {Colors.BLUE_PRIMARY};
        box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
    }}

    QGroupBox {{
        background: {Colors.WHITE};
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        font-weight: 600;
        color: #1e293b;
        margin-top: 1ex;
        padding-top: 20px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 6px 12px;
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 {Colors.BLUE_PRIMARY}, stop: 1 #4338ca);
        color: {Colors.WHITE};
        font-weight: 600;
        border-radius: 6px;
        margin-left: 12px;
    }}
    """

# ===== THÈME MODERNE SOMBRE =====

def get_dark_modern_theme_styles():
    """Styles pour le thème moderne sombre"""
    return f"""
    {get_base_styles()}
    
    /* Thème moderne sombre - Interface élégante pour la nuit */
    QMainWindow {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.DARK_BG}, stop: 1 #0f172a);
        color: {Colors.DARK_TEXT};
    }}

    QPushButton {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.DARK_SURFACE}, stop: 1 #1e293b);
        border: 1px solid {Colors.DARK_BORDER};
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        min-height: 28px;
        color: {Colors.DARK_TEXT};
    }}

    QPushButton:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #374151, stop: 1 {Colors.DARK_SURFACE});
        border-color: {Colors.BLUE_PRIMARY};
        color: #60a5fa;
        box-shadow: 0 4px 12px rgba(96, 165, 250, 0.2);
    }}

    QPushButton:pressed {{
        background: #1f2937;
    }}

    QLineEdit {{
        background: {Colors.DARK_SURFACE};
        border: 2px solid {Colors.DARK_BORDER};
        border-radius: 8px;
        padding: 10px 12px;
        color: {Colors.DARK_TEXT};
        selection-background-color: {Colors.BLUE_PRIMARY};
    }}

    QLineEdit:focus {{
        border-color: #60a5fa;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
    }}

    QGroupBox {{
        background: {Colors.DARK_SURFACE};
        border: 2px solid {Colors.DARK_BORDER};
        border-radius: 12px;
        font-weight: 600;
        color: {Colors.DARK_TEXT};
        margin-top: 1ex;
        padding-top: 20px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 6px 12px;
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 #3b82f6, stop: 1 #1d4ed8);
        color: {Colors.WHITE};
        font-weight: 600;
        border-radius: 6px;
        margin-left: 12px;
    }}
    """

# ===== THÈMES ADDITIONNELS =====

def get_blue_professional_theme_styles():
    """Styles pour le thème professionnel bleu"""
    return f"""
    {get_default_theme_styles()}
    
    /* Surcharge pour le thème professionnel bleu */
    QMainWindow {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #f0f8ff, stop: 1 #e6f3ff);
    }}
    
    QPushButton {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #4a90e2, stop: 1 #2c5aa0);
        color: {Colors.WHITE};
        border: none;
    }}
    
    QPushButton:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #5ba0f2, stop: 1 #3c6ab0);
    }}
    """

def get_green_nature_theme_styles():
    """Styles pour le thème nature verte"""
    return f"""
    {get_default_theme_styles()}
    
    /* Surcharge pour le thème nature verte */
    QMainWindow {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #f0fff0, stop: 1 #e6ffe6);
    }}
    
    QPushButton {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.GREEN_PRIMARY}, stop: 1 #0d5d2c);
        color: {Colors.WHITE};
        border: none;
    }}
    
    QPushButton:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #20c997, stop: 1 #1e7e5a);
    }}
    """

# ===== FONCTION PRINCIPALE =====

def get_theme_style(theme_key=None):
    """Fonction principale pour obtenir le style CSS d'un thème"""
    if theme_key is None:
        theme_key = get_current_theme()
    
    try:
        # Mapping des thèmes vers leurs fonctions de style
        theme_styles = {
            "default": get_default_theme_styles,
            "light_modern": get_light_modern_theme_styles,
            "dark_modern": get_dark_modern_theme_styles,
            "blue_professional": get_blue_professional_theme_styles,
            "green_nature": get_green_nature_theme_styles,
        }
        
        if theme_key in theme_styles:
            style = theme_styles[theme_key]()
            logger.debug(f"Style généré pour le thème: {theme_key}")
            return style
        else:
            logger.warning(f"Thème '{theme_key}' non trouvé, utilisation du thème par défaut")
            return get_default_theme_styles()
            
    except Exception as e:
        logger.error(f"Erreur lors de la génération du style pour '{theme_key}': {e}")
        return get_default_theme_styles()

# Fonction de compatibilité
def get_style():
    """Fonction de compatibilité avec l'ancien système"""
    return get_theme_style()

# Log d'initialisation
logger.info("Module de styles v2.0 initialisé") 