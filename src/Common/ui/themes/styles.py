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
    MEDIUM_GRAY = "#e9ecef"
    GRAY = "#6c757d"
    DARK_GRAY = "#343a40"
    BLACK = "#000000"
    
    # Couleurs primaires améliorées
    BLUE_PRIMARY = "#0d6efd"
    BLUE_LIGHT = "#3d8bfd"
    BLUE_DARK = "#0b5ed7"
    GREEN_PRIMARY = "#198754"
    GREEN_LIGHT = "#20c997"
    GREEN_DARK = "#146c43"
    RED_PRIMARY = "#dc3545"
    RED_LIGHT = "#ea868f"
    RED_DARK = "#b02a37"
    YELLOW_PRIMARY = "#ffc107"
    YELLOW_LIGHT = "#ffcd39"
    YELLOW_DARK = "#e6ac00"
    
    # Couleurs pour thème sombre améliorées
    DARK_BG = "#0f172a"
    DARK_BG_SECONDARY = "#1a202c"
    DARK_SURFACE = "#2d3748"
    DARK_SURFACE_HOVER = "#374151"
    DARK_BORDER = "#4a5568"
    DARK_BORDER_LIGHT = "#718096"
    DARK_TEXT = "#e2e8f0"
    DARK_TEXT_SECONDARY = "#a0aec0"
    
    # Couleurs d'accent
    PURPLE = "#8b5cf6"
    ORANGE = "#f97316"
    PINK = "#ec4899"
    TEAL = "#14b8a6"
    
    # Couleurs de statut
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    INFO = "#3b82f6"
    
    # Couleurs modernes pour nouveaux thèmes
    NEON_CYAN = "#00ffff"
    NEON_PINK = "#ff006e"
    NEON_GREEN = "#39ff14"
    NEON_PURPLE = "#bf00ff"
    
    # Couleurs glassmorphism
    GLASS_WHITE = "rgba(255, 255, 255, 0.25)"
    GLASS_DARK = "rgba(0, 0, 0, 0.25)"
    GLASS_BORDER = "rgba(255, 255, 255, 0.18)"
    
    # Couleurs neumorphism
    NEURO_LIGHT_BG = "#e0e5ec"
    NEURO_LIGHT_SHADOW = "#a3b1c6"
    NEURO_LIGHT_HIGHLIGHT = "#ffffff"
    NEURO_DARK_BG = "#2c2c54"
    NEURO_DARK_SHADOW = "#1a1a2e"
    NEURO_DARK_HIGHLIGHT = "#40407a"

# ===== STYLES DE BASE =====

def get_base_styles():
    """Styles de base communs à tous les thèmes"""
    return """
    /* Styles de base pour tous les thèmes */
    * {
                 font-family: "Helvetica Neue", "Helvetica", "Arial", sans-serif;
    }
    
    QWidget {
        font-size: 14px;
        outline: none;
    }
    
    /* Styles pour les barres de défilement */
    QScrollBar:vertical {
        width: 12px;
        border-radius: 6px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        height: 12px;
        border-radius: 6px;
        margin: 0px;
    }
    
    QScrollBar::handle:horizontal {
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    
    /* Styles pour les menus */
    QMenuBar {
        spacing: 3px;
        padding: 4px;
    }
    
    QMenuBar::item {
        padding: 8px 12px;
        border-radius: 4px;
    }
    
    QMenu {
        border-radius: 8px;
        padding: 8px;
        margin: 2px;
    }
    
    QMenu::item {
        padding: 8px 24px;
        border-radius: 4px;
        margin: 2px;
    }
    
    QMenu::separator {
        height: 1px;
        margin: 8px 0px;
    }
    
    /* Styles pour les tooltips */
    QToolTip {
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
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
    
    /* Styles complémentaires pour le thème moderne clair */
    QComboBox {{
        background: {Colors.WHITE};
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        min-width: 120px;
        color: #1e293b;
    }}
    
    QComboBox:hover {{
        border-color: {Colors.BLUE_PRIMARY};
    }}
    
    QComboBox:focus {{
        border-color: {Colors.BLUE_PRIMARY};
        box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
    }}
    
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 30px;
        border-left: 1px solid #e2e8f0;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
        background: #f8fafc;
    }}
    
    QComboBox::down-arrow {{
        width: 12px;
        height: 8px;
        background: #64748b;
    }}
    
    /* Styles pour QTextEdit */
    QTextEdit {{
        background: {Colors.WHITE};
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
        selection-background-color: {Colors.BLUE_PRIMARY};
        color: #1e293b;
    }}
    
    QTextEdit:focus {{
        border-color: {Colors.BLUE_PRIMARY};
        box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
    }}
    
    /* Styles pour les barres de défilement */
    QScrollBar:vertical {{
        background: #f8fafc;
        border: none;
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background: #cbd5e1;
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: #94a3b8;
    }}
    
    QScrollBar:horizontal {{
        background: #f8fafc;
        border: none;
        height: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background: #cbd5e1;
        border-radius: 6px;
        min-width: 20px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background: #94a3b8;
    }}
    
    /* Styles pour les menus */
    QMenuBar {{
        background: {Colors.WHITE};
        color: #1e293b;
        border-bottom: 1px solid #e2e8f0;
        padding: 4px;
    }}
    
    QMenuBar::item {{
        padding: 8px 12px;
        border-radius: 4px;
    }}
    
    QMenuBar::item:selected {{
        background: #f1f5f9;
        color: {Colors.BLUE_PRIMARY};
    }}
    
    QMenu {{
        background: {Colors.WHITE};
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px;
        margin: 2px;
        color: #1e293b;
    }}
    
    QMenu::item {{
        padding: 8px 24px;
        border-radius: 4px;
        margin: 2px;
    }}
    
    QMenu::item:selected {{
        background: #f1f5f9;
        color: {Colors.BLUE_PRIMARY};
    }}
    
    QMenu::separator {{
        height: 1px;
        background: #e2e8f0;
        margin: 8px 0px;
    }}
    
    /* Styles pour les tooltips */
    QToolTip {{
        background: #1e293b;
        color: {Colors.WHITE};
        border: none;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 12px;
        font-weight: 500;
    }}
    
    /* Styles pour QTabWidget */
    QTabWidget::pane {{
        background: {Colors.WHITE};
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        top: -1px;
    }}
    
    QTabBar::tab {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        color: #64748b;
        font-weight: 500;
    }}
    
    QTabBar::tab:selected {{
        background: {Colors.WHITE};
        color: {Colors.BLUE_PRIMARY};
        border-color: {Colors.BLUE_PRIMARY};
        font-weight: 600;
    }}
    
    QTabBar::tab:hover:!selected {{
        background: #f1f5f9;
        color: #475569;
    }}
    
    /* Styles pour QTableView améliorés */
    QTableView {{
        background: {Colors.WHITE};
        alternate-background-color: #f8fafc;
        gridline-color: #e2e8f0;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        selection-background-color: {Colors.BLUE_PRIMARY};
        selection-color: {Colors.WHITE};
    }}
    
    QHeaderView::section {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #f8fafc, stop: 1 #f1f5f9);
        border: none;
        border-right: 1px solid #e2e8f0;
        border-bottom: 2px solid #e2e8f0;
        padding: 12px;
        font-weight: 600;
        color: #1e293b;
    }}
    
    QHeaderView::section:hover {{
        background: #f1f5f9;
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
    
    /* Styles complémentaires pour le thème moderne sombre */
    QComboBox {{
        background: {Colors.DARK_SURFACE};
        border: 2px solid {Colors.DARK_BORDER};
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        min-width: 120px;
        color: {Colors.DARK_TEXT};
    }}
    
    QComboBox:hover {{
        border-color: #60a5fa;
        background: {Colors.DARK_SURFACE_HOVER};
    }}
    
    QComboBox:focus {{
        border-color: #60a5fa;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
    }}
    
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 30px;
        border-left: 1px solid {Colors.DARK_BORDER};
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
        background: #1f2937;
    }}
    
    QComboBox::down-arrow {{
        width: 12px;
        height: 8px;
        background: {Colors.DARK_TEXT_SECONDARY};
    }}
    
    /* Styles pour QTextEdit */
    QTextEdit {{
        background: {Colors.DARK_SURFACE};
        border: 2px solid {Colors.DARK_BORDER};
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
        selection-background-color: #3b82f6;
        color: {Colors.DARK_TEXT};
    }}
    
    QTextEdit:focus {{
        border-color: #60a5fa;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
    }}
    
    /* Styles pour les barres de défilement sombres */
    QScrollBar:vertical {{
        background: {Colors.DARK_BG};
        border: none;
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {Colors.DARK_BORDER};
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {Colors.DARK_BORDER_LIGHT};
    }}
    
    QScrollBar:horizontal {{
        background: {Colors.DARK_BG};
        border: none;
        height: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background: {Colors.DARK_BORDER};
        border-radius: 6px;
        min-width: 20px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background: {Colors.DARK_BORDER_LIGHT};
    }}
    
    /* Styles pour les menus sombres */
    QMenuBar {{
        background: {Colors.DARK_SURFACE};
        color: {Colors.DARK_TEXT};
        border-bottom: 1px solid {Colors.DARK_BORDER};
        padding: 4px;
    }}
    
    QMenuBar::item {{
        padding: 8px 12px;
        border-radius: 4px;
    }}
    
    QMenuBar::item:selected {{
        background: {Colors.DARK_SURFACE_HOVER};
        color: #60a5fa;
    }}
    
    QMenu {{
        background: {Colors.DARK_SURFACE};
        border: 1px solid {Colors.DARK_BORDER};
        border-radius: 8px;
        padding: 8px;
        margin: 2px;
        color: {Colors.DARK_TEXT};
    }}
    
    QMenu::item {{
        padding: 8px 24px;
        border-radius: 4px;
        margin: 2px;
    }}
    
    QMenu::item:selected {{
        background: {Colors.DARK_SURFACE_HOVER};
        color: #60a5fa;
    }}
    
    QMenu::separator {{
        height: 1px;
        background: {Colors.DARK_BORDER};
        margin: 8px 0px;
    }}
    
    /* Styles pour les tooltips sombres */
    QToolTip {{
        background: {Colors.DARK_BG};
        color: {Colors.DARK_TEXT};
        border: 1px solid {Colors.DARK_BORDER};
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 12px;
        font-weight: 500;
    }}
    
    /* Styles pour QTabWidget sombre */
    QTabWidget::pane {{
        background: {Colors.DARK_SURFACE};
        border: 2px solid {Colors.DARK_BORDER};
        border-radius: 8px;
        top: -1px;
    }}
    
    QTabBar::tab {{
        background: {Colors.DARK_BG};
        border: 1px solid {Colors.DARK_BORDER};
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        color: {Colors.DARK_TEXT_SECONDARY};
        font-weight: 500;
    }}
    
    QTabBar::tab:selected {{
        background: {Colors.DARK_SURFACE};
        color: #60a5fa;
        border-color: #60a5fa;
        font-weight: 600;
    }}
    
    QTabBar::tab:hover:!selected {{
        background: {Colors.DARK_SURFACE_HOVER};
        color: {Colors.DARK_TEXT};
    }}
    
    /* Styles pour QTableView sombre */
    QTableView {{
        background: {Colors.DARK_SURFACE};
        alternate-background-color: {Colors.DARK_BG_SECONDARY};
        gridline-color: {Colors.DARK_BORDER};
        border: 2px solid {Colors.DARK_BORDER};
        border-radius: 8px;
        selection-background-color: #3b82f6;
        selection-color: {Colors.WHITE};
        color: {Colors.DARK_TEXT};
    }}
    
    QHeaderView::section {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.DARK_BG}, stop: 1 {Colors.DARK_BG_SECONDARY});
        border: none;
        border-right: 1px solid {Colors.DARK_BORDER};
        border-bottom: 2px solid {Colors.DARK_BORDER};
        padding: 12px;
        font-weight: 600;
        color: {Colors.DARK_TEXT};
    }}
    
    QHeaderView::section:hover {{
        background: {Colors.DARK_SURFACE_HOVER};
    }}
    """

# ===== THÈMES ADDITIONNELS =====

def get_blue_professional_theme_styles():
    """Styles pour le thème professionnel bleu"""
    return f"""
    {get_light_modern_theme_styles()}
    
    /* Thème professionnel bleu - Interface corporate */
    QMainWindow {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #eff6ff, stop: 1 #dbeafe);
        color: #1e3a8a;
    }}
    
    QPushButton {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.BLUE_PRIMARY}, stop: 1 {Colors.BLUE_DARK});
        color: {Colors.WHITE};
        border: 1px solid {Colors.BLUE_DARK};
        font-weight: 600;
    }}
    
    QPushButton:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.BLUE_LIGHT}, stop: 1 {Colors.BLUE_PRIMARY});
        box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
        transform: translateY(-1px);
    }}
    
    QPushButton:pressed {{
        background: {Colors.BLUE_DARK};
        transform: translateY(0px);
    }}
    
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border-color: {Colors.BLUE_PRIMARY};
        box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.15);
    }}
    
    QGroupBox::title {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 {Colors.BLUE_PRIMARY}, stop: 1 {Colors.BLUE_DARK});
        color: {Colors.WHITE};
    }}
    
    QTabBar::tab:selected {{
        color: {Colors.BLUE_PRIMARY};
        border-color: {Colors.BLUE_PRIMARY};
    }}
    
    QMenuBar::item:selected, QMenu::item:selected {{
        color: {Colors.BLUE_PRIMARY};
    }}
    
    QTableView {{
        selection-background-color: {Colors.BLUE_PRIMARY};
    }}
    """

def get_green_nature_theme_styles():
    """Styles pour le thème nature verte"""
    return f"""
    {get_light_modern_theme_styles()}
    
    /* Surcharge pour le thème nature verte */
    QMainWindow {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #f0fff4, stop: 1 #dcfce7);
        color: #14532d;
    }}
    
    QPushButton {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.GREEN_PRIMARY}, stop: 1 {Colors.GREEN_DARK});
        color: {Colors.WHITE};
        border: 1px solid {Colors.GREEN_DARK};
        font-weight: 600;
    }}
    
    QPushButton:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.GREEN_LIGHT}, stop: 1 {Colors.GREEN_PRIMARY});
        box-shadow: 0 4px 12px rgba(25, 135, 84, 0.3);
        transform: translateY(-1px);
    }}
    
    QPushButton:pressed {{
        background: {Colors.GREEN_DARK};
        transform: translateY(0px);
    }}
    
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border-color: {Colors.GREEN_PRIMARY};
        box-shadow: 0 0 0 3px rgba(25, 135, 84, 0.15);
    }}
    
    QGroupBox::title {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 {Colors.GREEN_PRIMARY}, stop: 1 {Colors.GREEN_DARK});
        color: {Colors.WHITE};
    }}
    
    QTabBar::tab:selected {{
        color: {Colors.GREEN_PRIMARY};
        border-color: {Colors.GREEN_PRIMARY};
    }}
    
    QMenuBar::item:selected, QMenu::item:selected {{
        color: {Colors.GREEN_PRIMARY};
    }}
    """

def get_purple_creative_theme_styles():
    """Styles pour le thème créatif violet"""
    return f"""
    {get_light_modern_theme_styles()}
    
    /* Thème créatif violet - Interface artistique */
    QMainWindow {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #faf5ff, stop: 1 #f3e8ff);
        color: #581c87;
    }}
    
    QPushButton {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.PURPLE}, stop: 1 #7c3aed);
        color: {Colors.WHITE};
        border: 1px solid #7c3aed;
        font-weight: 600;
    }}
    
    QPushButton:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #a78bfa, stop: 1 {Colors.PURPLE});
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
        transform: translateY(-1px);
    }}
    
    QPushButton:pressed {{
        background: #7c3aed;
        transform: translateY(0px);
    }}
    
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border-color: {Colors.PURPLE};
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
    }}
    
    QGroupBox::title {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 {Colors.PURPLE}, stop: 1 #7c3aed);
        color: {Colors.WHITE};
    }}
    
    QTabBar::tab:selected {{
        color: {Colors.PURPLE};
        border-color: {Colors.PURPLE};
    }}
    
    QMenuBar::item:selected, QMenu::item:selected {{
        color: {Colors.PURPLE};
    }}
    
    QTableView {{
        selection-background-color: {Colors.PURPLE};
    }}
    """

def get_orange_warm_theme_styles():
    """Styles pour le thème chaleureux orange"""
    return f"""
    {get_light_modern_theme_styles()}
    
    /* Thème chaleureux orange - Interface accueillante */
    QMainWindow {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #fff7ed, stop: 1 #fed7aa);
        color: #9a3412;
    }}
    
    QPushButton {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.ORANGE}, stop: 1 #ea580c);
        color: {Colors.WHITE};
        border: 1px solid #ea580c;
        font-weight: 600;
    }}
    
    QPushButton:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #fb923c, stop: 1 {Colors.ORANGE});
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
        transform: translateY(-1px);
    }}
    
    QPushButton:pressed {{
        background: #ea580c;
        transform: translateY(0px);
    }}
    
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border-color: {Colors.ORANGE};
        box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15);
    }}
    
    QGroupBox::title {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 {Colors.ORANGE}, stop: 1 #ea580c);
        color: {Colors.WHITE};
    }}
    
    QTabBar::tab:selected {{
        color: {Colors.ORANGE};
        border-color: {Colors.ORANGE};
    }}
    
    QMenuBar::item:selected, QMenu::item:selected {{
        color: {Colors.ORANGE};
    }}
    
    QTableView {{
        selection-background-color: {Colors.ORANGE};
    }}
    """

def get_glassmorphism_theme_styles():
    """Styles pour le thème glassmorphism moderne - Effet de verre transparent"""
    return f"""
    {get_base_styles()}
    
    /* Thème glassmorphism - Design verre moderne */
    QMainWindow {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 #667eea, stop: 0.5 #764ba2, stop: 1 #f093fb);
        color: {Colors.WHITE};
    }}

    QPushButton {{
        background: {Colors.GLASS_WHITE};
        border: 1px solid {Colors.GLASS_BORDER};
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        min-height: 32px;
        color: {Colors.WHITE};
    }}

    QPushButton:hover {{
        background: rgba(255, 255, 255, 0.35);
        border-color: rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }}

    QLineEdit {{
        background: {Colors.GLASS_WHITE};
        border: 1px solid {Colors.GLASS_BORDER};
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 14px;
        color: {Colors.WHITE};
    }}

    QLineEdit:focus {{
        border-color: rgba(255, 255, 255, 0.5);
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
        background: rgba(255, 255, 255, 0.3);
    }}

    QGroupBox {{
        background: {Colors.GLASS_WHITE};
        border: 1px solid {Colors.GLASS_BORDER};
        border-radius: 16px;
        font-weight: 600;
        color: {Colors.WHITE};
        margin-top: 1ex;
        padding-top: 24px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 8px 16px;
        background: rgba(255, 255, 255, 0.4);
        color: {Colors.WHITE};
        font-weight: 600;
        border-radius: 8px;
        margin-left: 16px;
    }}

    QTableView {{
        background: {Colors.GLASS_WHITE};
        border: 1px solid {Colors.GLASS_BORDER};
        border-radius: 12px;
        color: {Colors.WHITE};
        gridline-color: rgba(255, 255, 255, 0.2);
    }}

    QScrollBar:vertical {{
        background: rgba(255, 255, 255, 0.1);
        border: none;
        width: 12px;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical {{
        background: rgba(255, 255, 255, 0.3);
        border-radius: 6px;
        min-height: 20px;
    }}
    """

def get_neumorphism_theme_styles():
    """Styles pour le thème neumorphism moderne - Design en relief soft"""
    return f"""
    {get_base_styles()}
    
    /* Thème neumorphism - Design en relief moderne */
    QMainWindow {{
        background: {Colors.NEURO_LIGHT_BG};
        color: #2c3e50;
    }}

    QPushButton {{
        background: {Colors.NEURO_LIGHT_BG};
        border: none;
        border-radius: 16px;
        padding: 16px 32px;
        font-weight: 600;
        min-height: 32px;
        color: #2c3e50;
    }}

    QPushButton:hover {{
        transform: translateY(-1px);
    }}

    QLineEdit {{
        background: {Colors.NEURO_LIGHT_BG};
        border: none;
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 14px;
        color: #2c3e50;
    }}

    QGroupBox {{
        background: {Colors.NEURO_LIGHT_BG};
        border: none;
        border-radius: 20px;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 1ex;
        padding-top: 24px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 8px 16px;
        background: {Colors.NEURO_LIGHT_BG};
        color: #2c3e50;
        font-weight: 600;
        border-radius: 12px;
        margin-left: 16px;
    }}

    QScrollBar:vertical {{
        background: {Colors.NEURO_LIGHT_BG};
        border: none;
        width: 16px;
        border-radius: 8px;
    }}
    """

def get_cyberpunk_neon_theme_styles():
    """Styles pour le thème cyberpunk néon - Design futuriste avec effets lumineux"""
    return f"""
    {get_base_styles()}
    
    /* Thème cyberpunk néon - Design futuriste */
    QMainWindow {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 #0c0c0c, stop: 0.5 #1a0033, stop: 1 #000000);
        color: {Colors.NEON_CYAN};
    }}

    QPushButton {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #1a1a2e, stop: 1 #16213e);
        border: 2px solid {Colors.NEON_CYAN};
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        min-height: 32px;
        color: {Colors.NEON_CYAN};
        text-transform: uppercase;
        font-family: "Courier New", monospace;
        box-shadow: 0 0 10px {Colors.NEON_CYAN};
    }}

    QPushButton:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #0f4c75, stop: 1 #3282b8);
        border-color: {Colors.NEON_PINK};
        color: {Colors.NEON_PINK};
        box-shadow: 0 0 20px {Colors.NEON_PINK};
        transform: translateY(-2px);
    }}

    QLineEdit {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #1a1a2e, stop: 1 #16213e);
        border: 2px solid {Colors.NEON_GREEN};
        border-radius: 6px;
        padding: 10px 12px;
        font-size: 14px;
        color: {Colors.NEON_GREEN};
        font-family: "Courier New", monospace;
        selection-background-color: {Colors.NEON_PINK};
        box-shadow: inset 0 0 5px rgba(57, 255, 20, 0.3);
    }}

    QLineEdit:focus {{
        border-color: {Colors.NEON_PINK};
        color: {Colors.NEON_PINK};
        box-shadow: 0 0 15px {Colors.NEON_PINK};
    }}

    QGroupBox {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 rgba(26, 26, 46, 0.8), stop: 1 rgba(22, 33, 62, 0.8));
        border: 2px solid {Colors.NEON_PINK};
        border-radius: 12px;
        font-weight: 600;
        color: {Colors.NEON_PINK};
        margin-top: 1ex;
        padding-top: 20px;
        font-family: "Courier New", monospace;
        box-shadow: 0 0 20px rgba(255, 0, 110, 0.3);
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 6px 12px;
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 {Colors.NEON_PINK}, stop: 1 {Colors.NEON_PURPLE});
        color: #000000;
        font-weight: 600;
        border-radius: 6px;
        margin-left: 12px;
        text-transform: uppercase;
        box-shadow: 0 0 10px {Colors.NEON_PINK};
    }}

    QScrollBar:vertical {{
        background: #1a1a2e;
        border: 1px solid {Colors.NEON_CYAN};
        width: 14px;
        border-radius: 7px;
    }}

    QScrollBar::handle:vertical {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 {Colors.NEON_CYAN}, stop: 1 {Colors.NEON_PINK});
        border-radius: 6px;
        min-height: 20px;
        box-shadow: 0 0 8px {Colors.NEON_CYAN};
    }}

    QToolTip {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 {Colors.NEON_CYAN}, stop: 1 {Colors.NEON_PINK});
        color: #000000;
        border: none;
        border-radius: 6px;
        font-family: "Courier New", monospace;
        text-transform: uppercase;
        font-weight: 600;
        box-shadow: 0 0 15px {Colors.NEON_CYAN};
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
            "purple_creative": get_purple_creative_theme_styles,
            "orange_warm": get_orange_warm_theme_styles,
            "glassmorphism": get_glassmorphism_theme_styles,
            "neumorphism": get_neumorphism_theme_styles,
            "cyberpunk_neon": get_cyberpunk_neon_theme_styles,
        }
        
        if theme_key in theme_styles:
            style = theme_styles[theme_key]()
            
            # Optimiser les polices selon le système
            try:
                from ..font_utils import optimize_css_fonts
                style = optimize_css_fonts(style)
                logger.debug(f"Style généré et optimisé pour le thème: {theme_key}")
            except ImportError:
                logger.debug(f"Optimisation des polices non disponible pour le thème: {theme_key}")
            
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

# ===== FONCTIONS UTILITAIRES =====

def get_available_themes():
    """Retourne la liste des thèmes disponibles avec leurs descriptions"""
    return {
        "default": "Thème par défaut - Simple et compatible",
        "light_modern": "Moderne clair - Interface élégante et lumineuse",
        "dark_modern": "Moderne sombre - Interface élégante pour la nuit",
        "blue_professional": "Professionnel bleu - Interface corporate",
        "green_nature": "Nature verte - Interface écologique et apaisante",
        "purple_creative": "Créatif violet - Interface artistique et moderne",
        "orange_warm": "Chaleureux orange - Interface accueillante et énergique",
        "glassmorphism": "Glassmorphism - Effet de verre transparent ultra-moderne",
        "neumorphism": "Neumorphism - Design en relief soft et élégant",
        "cyberpunk_neon": "Cyberpunk Néon - Design futuriste avec effets lumineux",
    }

def get_theme_preview_style(theme_key):
    """Génère un style CSS simplifié pour l'aperçu d'un thème"""
    try:
        full_style = get_theme_style(theme_key)
        # Extraire les couleurs principales pour l'aperçu
        preview_style = f"""
        QWidget {{
            font-family: "Helvetica Neue", "Helvetica", "Arial", sans-serif;
            font-size: 12px;
        }}
        """
        return preview_style
    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'aperçu pour '{theme_key}': {e}")
        return ""

def validate_theme_style(theme_key):
    """Valide qu'un thème peut être généré sans erreur"""
    try:
        style = get_theme_style(theme_key)
        return len(style) > 0
    except Exception as e:
        logger.error(f"Validation échouée pour le thème '{theme_key}': {e}")
        return False

def get_theme_colors(theme_key):
    """Retourne les couleurs principales d'un thème"""
    color_map = {
        "default": {"primary": Colors.BLUE_PRIMARY, "bg": Colors.WHITE},
        "light_modern": {"primary": Colors.BLUE_PRIMARY, "bg": Colors.WHITE},
        "dark_modern": {"primary": "#60a5fa", "bg": Colors.DARK_BG},
        "blue_professional": {"primary": Colors.BLUE_PRIMARY, "bg": "#eff6ff"},
        "green_nature": {"primary": Colors.GREEN_PRIMARY, "bg": "#f0fff4"},
        "purple_creative": {"primary": Colors.PURPLE, "bg": "#faf5ff"},
        "orange_warm": {"primary": Colors.ORANGE, "bg": "#fff7ed"},
        "glassmorphism": {"primary": Colors.WHITE, "bg": "#667eea"},
        "neumorphism": {"primary": "#2c3e50", "bg": Colors.NEURO_LIGHT_BG},
        "cyberpunk_neon": {"primary": Colors.NEON_CYAN, "bg": "#0c0c0c"},
    }
    return color_map.get(theme_key, {"primary": Colors.BLUE_PRIMARY, "bg": Colors.WHITE})

# Log d'initialisation
logger.info("Module de styles v3.0 initialisé avec 10 thèmes ultra-modernes disponibles") 