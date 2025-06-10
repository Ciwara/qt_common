#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Styles CSS modernes pour l'application Qt
Auteur: Assistant AI
"""

from ..models import Settings
from ..cstatic import logger

# ===== CONSTANTES DE COULEURS =====
class Colors:
    """Palette de couleurs modernes"""
    # Couleurs neutres
    WHITE = "#ffffff"
    LIGHT_GRAY = "#f8f9fa"
    GRAY = "#6c757d"
    DARK_GRAY = "#343a40"
    BLACK = "#000000"
    
    # Couleurs primaires
    BLUE_PRIMARY = "#0d6efd"
    BLUE_SECONDARY = "#6c757d"
    GREEN_PRIMARY = "#198754"
    RED_PRIMARY = "#dc3545"
    YELLOW_PRIMARY = "#ffc107"
    
    # Couleurs pour thème sombre
    DARK_BG = "#1a202c"
    DARK_SURFACE = "#2d3748"
    DARK_BORDER = "#4a5568"
    DARK_TEXT = "#e2e8f0"

# ===== STYLES DE BASE =====
BASE_FONT = '"Segoe UI", "Inter", -apple-system, BlinkMacSystemFont, "Roboto", sans-serif'

TRANSITIONS = """
/* Transitions fluides pour une meilleure UX */
QPushButton, QToolButton, QLineEdit, QComboBox, QSpinBox, QTabBar::tab {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

QPushButton:hover, QToolButton:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

QPushButton:pressed, QToolButton:pressed {
    transform: translateY(0px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
"""

# ===== THÈME MODERNE CLAIR =====
MODERN_LIGHT = f"""
{TRANSITIONS}

/* === CONFIGURATION GLOBALE === */
* {{
    font-family: {BASE_FONT};
    font-size: 14px;
    outline: none;
}}

/* === FENÊTRE PRINCIPALE === */
QMainWindow {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {Colors.WHITE}, 
        stop: 1 {Colors.LIGHT_GRAY});
    color: #1f2937;
}}

QDialog {{
    background: {Colors.WHITE};
    border: 1px solid #e5e7eb;
    border-radius: 12px;
}}

/* === BARRE D'OUTILS MODERNE === */
QToolBar {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {Colors.WHITE}, 
        stop: 1 {Colors.LIGHT_GRAY});
    border: none;
    border-bottom: 1px solid #e5e7eb;
    spacing: 8px;
    padding: 12px 16px;
    min-height: 56px;
}}

QToolButton {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    color: #374151;
    font-weight: 500;
    padding: 10px 14px;
    min-height: 40px;
    min-width: 40px;
}}

QToolButton:hover {{
    background: #f3f4f6;
    border-color: #d1d5db;
    color: #111827;
}}

QToolButton:pressed {{
    background: #e5e7eb;
    border-color: #9ca3af;
}}

QToolButton:checked {{
    background: {Colors.BLUE_PRIMARY};
    border-color: {Colors.BLUE_PRIMARY};
    color: white;
}}

/* === BOUTONS MODERNES === */
QPushButton {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {Colors.WHITE}, 
        stop: 1 #f9fafb);
    border: 1.5px solid #d1d5db;
    border-radius: 8px;
    color: #374151;
    font-weight: 500;
    padding: 10px 20px;
    min-height: 40px;
    min-width: 100px;
}}

QPushButton:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #f9fafb, 
        stop: 1 #f3f4f6);
    border-color: #9ca3af;
    color: #111827;
}}

QPushButton:pressed {{
    background: #e5e7eb;
    border-color: #6b7280;
}}

QPushButton:disabled {{
    background: #f9fafb;
    border-color: #e5e7eb;
    color: #9ca3af;
}}

/* === BOUTON PRIMAIRE === */
QPushButton[class="primary"] {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {Colors.BLUE_PRIMARY}, 
        stop: 1 #0056b3);
    border-color: {Colors.BLUE_PRIMARY};
    color: white;
    font-weight: 600;
}}

QPushButton[class="primary"]:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #4dabf7, 
        stop: 1 {Colors.BLUE_PRIMARY});
    border-color: #0056b3;
}}

QPushButton[class="success"] {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {Colors.GREEN_PRIMARY}, 
        stop: 1 #146c43);
    border-color: {Colors.GREEN_PRIMARY};
    color: white;
    font-weight: 600;
}}

QPushButton[class="danger"] {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {Colors.RED_PRIMARY}, 
        stop: 1 #b02a37);
    border-color: {Colors.RED_PRIMARY};
    color: white;
    font-weight: 600;
}}

/* === CHAMPS DE SAISIE MODERNES === */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {Colors.WHITE};
    border: 1.5px solid #d1d5db;
    border-radius: 8px;
    color: #111827;
    padding: 12px 16px;
    selection-background-color: {Colors.BLUE_PRIMARY};
    selection-color: white;
    font-size: 14px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {Colors.BLUE_PRIMARY};
    box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
}}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
    background: #f9fafb;
    border-color: #e5e7eb;
    color: #6b7280;
}}

/* === COMBOBOX MODERNE === */
QComboBox {{
    background: {Colors.WHITE};
    border: 1.5px solid #d1d5db;
    border-radius: 8px;
    color: #111827;
    padding: 12px 16px;
    padding-right: 40px;
    min-height: 20px;
}}

QComboBox:hover {{
    border-color: #9ca3af;
}}

QComboBox:focus {{
    border-color: {Colors.BLUE_PRIMARY};
    box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 32px;
    border-left: 1.5px solid #d1d5db;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
    background: #f9fafb;
}}

QComboBox::down-arrow {{
    image: none;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 7px solid #6b7280;
    margin: auto;
}}

QComboBox QAbstractItemView {{
    background: {Colors.WHITE};
    border: 1px solid #d1d5db;
    border-radius: 8px;
    selection-background-color: {Colors.BLUE_PRIMARY};
    selection-color: white;
    outline: none;
    padding: 4px;
}}

QComboBox QAbstractItemView::item {{
    padding: 8px 12px;
    border-radius: 4px;
    margin: 1px;
}}

QComboBox QAbstractItemView::item:hover {{
    background: #f3f4f6;
}}

/* === TABLEAUX MODERNES === */
QTableView {{
    background: {Colors.WHITE};
    alternate-background-color: #f8fafc;
    gridline-color: #e2e8f0;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    selection-background-color: {Colors.BLUE_PRIMARY};
    selection-color: white;
}}

QHeaderView::section {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #f8fafc, 
        stop: 1 #f1f5f9);
    border: none;
    border-right: 1px solid #e2e8f0;
    border-bottom: 2px solid #e2e8f0;
    color: #475569;
    font-weight: 600;
    padding: 12px 16px;
    text-align: left;
}}

QHeaderView::section:hover {{
    background: #f1f5f9;
}}

QTableView::item {{
    padding: 8px 12px;
    border: none;
}}

QTableView::item:hover {{
    background: #f8fafc;
}}

QTableView::item:selected {{
    background: {Colors.BLUE_PRIMARY};
    color: white;
}}

/* === ONGLETS MODERNES === */
QTabWidget::pane {{
    background: {Colors.WHITE};
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    border-top-left-radius: 0;
    padding: 0;
}}

QTabBar::tab {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    color: #64748b;
    font-weight: 500;
    margin-right: 2px;
    padding: 10px 20px;
    min-width: 80px;
}}

QTabBar::tab:selected {{
    background: {Colors.WHITE};
    border-bottom: 1px solid {Colors.WHITE};
    color: {Colors.BLUE_PRIMARY};
    font-weight: 600;
}}

QTabBar::tab:hover:!selected {{
    background: #f1f5f9;
    color: #475569;
}}

/* === GROUPES MODERNES === */
QGroupBox {{
    background: {Colors.WHITE};
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    font-weight: 600;
    color: #374151;
    margin-top: 1ex;
    padding-top: 20px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    background: {Colors.BLUE_PRIMARY};
    color: white;
    font-weight: 600;
    border-radius: 6px;
    margin-left: 12px;
}}

/* === BARRES DE DÉFILEMENT MODERNES === */
QScrollBar:vertical {{
    background: #f8fafc;
    width: 14px;
    border-radius: 7px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: #cbd5e1;
    border-radius: 7px;
    min-height: 20px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background: #94a3b8;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: #f8fafc;
    height: 14px;
    border-radius: 7px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: #cbd5e1;
    border-radius: 7px;
    min-width: 20px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #94a3b8;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* === BARRES DE PROGRESSION === */
QProgressBar {{
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    text-align: center;
    color: #475569;
    font-weight: 500;
    padding: 2px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {Colors.BLUE_PRIMARY}, 
        stop: 1 #0056b3);
    border-radius: 6px;
    margin: 1px;
}}

/* === SPINBOX === */
QSpinBox, QDoubleSpinBox {{
    background: {Colors.WHITE};
    border: 1.5px solid #d1d5db;
    border-radius: 8px;
    color: #111827;
    padding: 12px 16px;
    padding-right: 32px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {Colors.BLUE_PRIMARY};
    box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #d1d5db;
    border-top-right-radius: 8px;
    background: #f9fafb;
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    border-left: 1px solid #d1d5db;
    border-bottom-right-radius: 8px;
    background: #f9fafb;
}}

/* === TOOLTIPS MODERNES === */
QToolTip {{
    background: #1f2937;
    border: none;
    border-radius: 6px;
    color: white;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 500;
}}

/* === MENUS === */
QMenuBar {{
    background: {Colors.WHITE};
    border-bottom: 1px solid #e2e8f0;
    color: #374151;
    padding: 4px;
}}

QMenuBar::item {{
    background: transparent;
    padding: 8px 12px;
    border-radius: 6px;
}}

QMenuBar::item:hover {{
    background: #f3f4f6;
}}

QMenuBar::item:pressed {{
    background: #e5e7eb;
}}

QMenu {{
    background: {Colors.WHITE};
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 4px;
    color: #374151;
}}

QMenu::item {{
    padding: 8px 16px;
    border-radius: 4px;
    margin: 1px;
}}

QMenu::item:hover {{
    background: #f3f4f6;
}}

QMenu::item:selected {{
    background: {Colors.BLUE_PRIMARY};
    color: white;
}}

QMenu::separator {{
    height: 1px;
    background: #e2e8f0;
    margin: 4px 8px;
}}

/* === CHECKBOXES ET RADIO BUTTONS === */
QCheckBox, QRadioButton {{
    color: #374151;
    font-weight: 500;
    spacing: 8px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 18px;
    height: 18px;
}}

QCheckBox::indicator {{
    border: 2px solid #d1d5db;
    border-radius: 4px;
    background: {Colors.WHITE};
}}

QCheckBox::indicator:checked {{
    background: {Colors.BLUE_PRIMARY};
    border-color: {Colors.BLUE_PRIMARY};
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiPjxwYXRoIGQ9Im0xIDQgMi41IDIuNUw5IDEiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
}}

QRadioButton::indicator {{
    border: 2px solid #d1d5db;
    border-radius: 9px;
    background: {Colors.WHITE};
}}

QRadioButton::indicator:checked {{
    background: {Colors.BLUE_PRIMARY};
    border-color: {Colors.BLUE_PRIMARY};
}}

QRadioButton::indicator:checked::after {{
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 3px;
    background: white;
    margin: 4px;
}}

/* === SLIDERS === */
QSlider::groove:horizontal {{
    border: none;
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {Colors.BLUE_PRIMARY};
    border: 2px solid white;
    width: 20px;
    height: 20px;
    margin: -7px 0;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}}

QSlider::handle:horizontal:hover {{
    background: #4dabf7;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}}

QSlider::sub-page:horizontal {{
    background: {Colors.BLUE_PRIMARY};
    border-radius: 3px;
}}

/* === DOCKWIDGETS === */
QDockWidget {{
    background: {Colors.WHITE};
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    titlebar-close-icon: url(:/icons/close.png);
    titlebar-normal-icon: url(:/icons/undock.png);
}}

QDockWidget::title {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #f8fafc, 
        stop: 1 #f1f5f9);
    border-bottom: 1px solid #e2e8f0;
    color: #374151;
    font-weight: 600;
    padding: 8px 12px;
    text-align: left;
}}

QDockWidget::close-button, QDockWidget::float-button {{
    border: 1px solid transparent;
    border-radius: 4px;
    background: transparent;
    padding: 2px;
}}

QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
    background: #f3f4f6;
    border-color: #d1d5db;
}}

QDockWidget::close-button:pressed, QDockWidget::float-button:pressed {{
    background: #e5e7eb;
}}
"""

# ===== THÈME SOMBRE MODERNE =====
MODERN_DARK = f"""
{TRANSITIONS}

/* === CONFIGURATION GLOBALE === */
* {{
    font-family: {BASE_FONT};
    font-size: 14px;
    outline: none;
}}

/* === FENÊTRE PRINCIPALE === */
QMainWindow {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {Colors.DARK_BG}, 
        stop: 1 #111827);
    color: {Colors.DARK_TEXT};
}}

QDialog {{
    background: {Colors.DARK_SURFACE};
    border: 1px solid {Colors.DARK_BORDER};
    border-radius: 12px;
}}

/* === BARRE D'OUTILS === */
QToolBar {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {Colors.DARK_SURFACE}, 
        stop: 1 {Colors.DARK_BG});
    border: none;
    border-bottom: 1px solid {Colors.DARK_BORDER};
    spacing: 8px;
    padding: 12px 16px;
    min-height: 56px;
}}

QToolButton {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    color: #a0aec0;
    font-weight: 500;
    padding: 10px 14px;
    min-height: 40px;
    min-width: 40px;
}}

QToolButton:hover {{
    background: #374151;
    border-color: #4b5563;
    color: {Colors.DARK_TEXT};
}}

QToolButton:pressed {{
    background: #1f2937;
    border-color: #374151;
}}

QToolButton:checked {{
    background: #3b82f6;
    border-color: #3b82f6;
    color: white;
}}

/* === BOUTONS === */
QPushButton {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {Colors.DARK_SURFACE}, 
        stop: 1 #1f2937);
    border: 1.5px solid #4b5563;
    border-radius: 8px;
    color: {Colors.DARK_TEXT};
    font-weight: 500;
    padding: 10px 20px;
    min-height: 40px;
    min-width: 100px;
}}

QPushButton:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #374151, 
        stop: 1 {Colors.DARK_SURFACE});
    border-color: #6b7280;
    color: white;
}}

QPushButton:pressed {{
    background: #1f2937;
    border-color: #374151;
}}

QPushButton:disabled {{
    background: #111827;
    border-color: {Colors.DARK_BG};
    color: #4b5563;
}}

/* === BOUTON PRIMAIRE SOMBRE === */
QPushButton[class="primary"] {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #3b82f6, 
        stop: 1 #1d4ed8);
    border-color: #3b82f6;
    color: white;
    font-weight: 600;
}}

QPushButton[class="primary"]:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #60a5fa, 
        stop: 1 #3b82f6);
    border-color: #1d4ed8;
}}

/* === CHAMPS DE SAISIE SOMBRES === */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {Colors.DARK_BG};
    border: 1.5px solid {Colors.DARK_BORDER};
    border-radius: 8px;
    color: {Colors.DARK_TEXT};
    padding: 12px 16px;
    selection-background-color: #3b82f6;
    selection-color: white;
    font-size: 14px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: #60a5fa;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
    background: {Colors.DARK_SURFACE};
    border-color: {Colors.DARK_BG};
    color: #4b5563;
}}

/* === TABLEAUX SOMBRES === */
QTableView {{
    background: {Colors.DARK_BG};
    alternate-background-color: {Colors.DARK_SURFACE};
    gridline-color: {Colors.DARK_BORDER};
    border: 1px solid {Colors.DARK_BORDER};
    border-radius: 8px;
    selection-background-color: #3b82f6;
    selection-color: white;
}}

QHeaderView::section {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {Colors.DARK_SURFACE}, 
        stop: 1 #1f2937);
    border: none;
    border-right: 1px solid #4b5563;
    border-bottom: 2px solid #4b5563;
    color: {Colors.DARK_TEXT};
    font-weight: 600;
    padding: 12px 16px;
    text-align: left;
}}

QHeaderView::section:hover {{
    background: #374151;
}}

/* === TOOLTIPS SOMBRES === */
QToolTip {{
    background: #374151;
    border: 1px solid #4b5563;
    border-radius: 6px;
    color: white;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 500;
}}

/* Continuer avec les autres éléments... */
"""

# ===== FONCTIONS UTILITAIRES =====
def get_modern_style(theme_name="light"):
    """Retourne un style moderne selon le thème demandé"""
    themes = {
        "light": MODERN_LIGHT,
        "dark": MODERN_DARK,
    }
    return themes.get(theme_name, MODERN_LIGHT)

def get_available_modern_themes():
    """Retourne la liste des thèmes modernes disponibles"""
    return {
        "light": "Moderne Clair",
        "dark": "Moderne Sombre",
    }

def apply_modern_theme(theme_name="light"):
    """Applique un thème moderne"""
    try:
        logger.info(f"Application du thème moderne: {theme_name}")
        return get_modern_style(theme_name)
    except Exception as exc:
        logger.error(f"Erreur lors de l'application du thème moderne: {exc}")
        return MODERN_LIGHT 