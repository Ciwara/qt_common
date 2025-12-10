#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Styles CSS pour tous les thèmes
Version 2.0 - Styles nettoyés et optimisés
"""

from ...cstatic import logger
from .config import get_current_theme

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

# ===== THÈME SYSTÈME =====

def get_system_theme_styles():
    """Styles pour le thème système - résout dynamiquement vers clair ou sombre"""
    from .config import ThemeConfig
    
    # Cette fonction ne devrait normalement pas être appelée directement
    # car le thème "system" est résolu avant d'arriver ici
    # Mais on garde une implémentation de fallback
    if ThemeConfig._detect_system_dark_mode():
        logger.debug("Thème système: mode sombre détecté")
        return get_dark_modern_theme_styles()
    else:
        logger.debug("Thème système: mode clair détecté")
        return get_light_modern_theme_styles()


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


# ===== FONCTION PRINCIPALE =====

def get_theme_style(theme_key=None):
    """Fonction principale pour obtenir le style CSS d'un thème"""
    if theme_key is None:
        theme_key = get_current_theme()
    
    try:
        # Si le thème est "system", résoudre vers le thème système réel
        if theme_key == "system":
            from .config import ThemeConfig
            resolved_theme = ThemeConfig.resolve_system_theme()
            logger.info(f"Thème système résolu vers: {resolved_theme}")
            theme_key = resolved_theme
        
        # Mapping des thèmes vers leurs fonctions de style
        theme_styles = {
            "system": get_system_theme_styles,  # Résolu dynamiquement ci-dessus
            "light_modern": get_light_modern_theme_styles,
            "dark_modern": get_dark_modern_theme_styles,
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
            logger.warning(f"Thème '{theme_key}' non trouvé, utilisation du thème clair par défaut")
            return get_light_modern_theme_styles()
            
    except Exception as e:
        logger.error(f"Erreur lors de la génération du style pour '{theme_key}': {e}")
        return get_light_modern_theme_styles()

# Fonction de compatibilité
def get_style():
    """Fonction de compatibilité avec l'ancien système"""
    return get_theme_style()

# ===== FONCTIONS UTILITAIRES =====


def get_theme_colors(theme_key):
    """Retourne les couleurs principales d'un thème"""
    color_map = {
        "light_modern": {"primary": Colors.BLUE_PRIMARY, "bg": Colors.WHITE},
        "dark_modern": {"primary": "#60a5fa", "bg": Colors.DARK_BG},
        "system": {"primary": Colors.BLUE_PRIMARY, "bg": Colors.WHITE},  # Résolu dynamiquement
    }
    # Pour le thème système, résoudre vers le thème réel
    if theme_key == "system":
        from .config import ThemeConfig
        resolved_theme = ThemeConfig.resolve_system_theme()
        return color_map.get(resolved_theme, color_map["light_modern"])
    return color_map.get(theme_key, {"primary": Colors.BLUE_PRIMARY, "bg": Colors.WHITE})

# Log d'initialisation
logger.info("Module de styles initialisé avec 2 thèmes disponibles: light_modern et dark_modern") 