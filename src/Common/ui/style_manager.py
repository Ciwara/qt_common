#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gestionnaire de styles moderne pour l'application Qt
Remplace l'ancien système de thèmes par une approche plus moderne et maintenable
"""

from ..models import Settings
from ..cstatic import logger

# ===== CONSTANTES =====
class ThemeNames:
    """Constantes pour les noms de thèmes"""
    DEFAULT = "default"
    LIGHT_MODERN = "light_modern" 
    DARK_MODERN = "dark_modern"
    BLUE_PROFESSIONAL = "blue_professional"
    GREEN_NATURE = "green_nature"
    
class Colors:
    """Palette de couleurs modernes"""
    # Couleurs neutres
    WHITE = "#ffffff"
    LIGHT_GRAY = "#f8f9fa"
    MEDIUM_GRAY = "#6c757d"
    DARK_GRAY = "#343a40"
    BLACK = "#000000"
    
    # Couleurs d'accent
    BLUE_PRIMARY = "#0d6efd"
    BLUE_LIGHT = "#4dabf7"
    GREEN_PRIMARY = "#198754"
    RED_PRIMARY = "#dc3545"
    YELLOW_PRIMARY = "#ffc107"
    PURPLE_PRIMARY = "#6f42c1"
    
    # Couleurs pour thème sombre
    DARK_BG = "#1a202c"
    DARK_SURFACE = "#2d3748"
    DARK_BORDER = "#4a5568"
    DARK_TEXT = "#e2e8f0"

# ===== COMPOSANTS DE STYLE =====
def create_base_styles():
    """Styles de base communs à tous les thèmes"""
    return f"""
    /* Configuration globale */
    * {{
        font-family: "Segoe UI", "Inter", -apple-system, BlinkMacSystemFont, "Roboto", sans-serif;
        font-size: 14px;
        outline: none;
    }}

    /* Transitions fluides */
    QPushButton, QToolButton, QLineEdit, QComboBox, QSpinBox, QTabBar::tab {{
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    QPushButton:hover, QToolButton:hover {{
        transform: translateY(-1px);
    }}

    QPushButton:pressed, QToolButton:pressed {{
        transform: translateY(0px);
    }}
    """

def create_button_styles(bg_color, hover_color, pressed_color, text_color, border_color):
    """Génère les styles pour les boutons"""
    return f"""
    QPushButton {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {bg_color}, stop: 1 {hover_color});
        border: 1.5px solid {border_color};
        border-radius: 8px;
        color: {text_color};
        font-weight: 500;
        padding: 10px 20px;
        min-height: 36px;
        min-width: 100px;
    }}

    QPushButton:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {hover_color}, stop: 1 {pressed_color});
        border-color: {Colors.MEDIUM_GRAY};
    }}

    QPushButton:pressed {{
        background: {pressed_color};
        border-color: {Colors.DARK_GRAY};
    }}

    QPushButton:disabled {{
        background: {Colors.LIGHT_GRAY};
        border-color: {Colors.MEDIUM_GRAY};
        color: {Colors.MEDIUM_GRAY};
    }}

    /* Boutons spécialisés */
    QPushButton[class="primary"] {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.BLUE_PRIMARY}, stop: 1 #0056b3);
        border-color: {Colors.BLUE_PRIMARY};
        color: white;
        font-weight: 600;
    }}

    QPushButton[class="primary"]:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.BLUE_LIGHT}, stop: 1 {Colors.BLUE_PRIMARY});
    }}

    QPushButton[class="success"] {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.GREEN_PRIMARY}, stop: 1 #146c43);
        border-color: {Colors.GREEN_PRIMARY};
        color: white;
        font-weight: 600;
    }}

    QPushButton[class="danger"] {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {Colors.RED_PRIMARY}, stop: 1 #b02a37);
        border-color: {Colors.RED_PRIMARY};
        color: white;
        font-weight: 600;
    }}
    """

def create_input_styles(bg_color, border_color, text_color, focus_color):
    """Génère les styles pour les champs de saisie"""
    return f"""
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background: {bg_color};
        border: 1.5px solid {border_color};
        border-radius: 8px;
        color: {text_color};
        padding: 12px 16px;
        selection-background-color: {Colors.BLUE_PRIMARY};
        selection-color: white;
        font-size: 14px;
    }}

    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {focus_color};
        box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
    }}

    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
        background: {Colors.LIGHT_GRAY};
        border-color: {Colors.MEDIUM_GRAY};
        color: {Colors.MEDIUM_GRAY};
    }}

    /* ComboBox */
    QComboBox {{
        background: {bg_color};
        border: 1.5px solid {border_color};
        border-radius: 8px;
        color: {text_color};
        padding: 12px 16px;
        padding-right: 40px;
        min-height: 20px;
    }}

    QComboBox:hover {{
        border-color: {focus_color};
    }}

    QComboBox:focus {{
        border-color: {focus_color};
        box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
    }}

    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 32px;
        border-left: 1.5px solid {border_color};
        border-top-right-radius: 8px;
        border-bottom-right-radius: 8px;
        background: {Colors.LIGHT_GRAY};
    }}

    QComboBox::down-arrow {{
        image: none;
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 7px solid {text_color};
        margin: auto;
    }}

    QComboBox QAbstractItemView {{
        background: {bg_color};
        border: 1px solid {border_color};
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
        background: {Colors.LIGHT_GRAY};
    }}
    """

def create_table_styles(bg_color, alt_bg_color, border_color, text_color, header_bg):
    """Génère les styles pour les tableaux"""
    return f"""
    QTableView {{
        background: {bg_color};
        alternate-background-color: {alt_bg_color};
        gridline-color: {border_color};
        border: 1px solid {border_color};
        border-radius: 8px;
        selection-background-color: {Colors.BLUE_PRIMARY};
        selection-color: white;
    }}

    QHeaderView::section {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {header_bg}, stop: 1 {alt_bg_color});
        border: none;
        border-right: 1px solid {border_color};
        border-bottom: 2px solid {border_color};
        color: {text_color};
        font-weight: 600;
        padding: 12px 16px;
        text-align: left;
    }}

    QHeaderView::section:hover {{
        background: {alt_bg_color};
    }}

    QTableView::item {{
        padding: 8px 12px;
        border: none;
    }}

    QTableView::item:hover {{
        background: {alt_bg_color};
    }}

    QTableView::item:selected {{
        background: {Colors.BLUE_PRIMARY};
        color: white;
    }}
    """

def create_toolbar_styles(bg_gradient_start, bg_gradient_end, border_color):
    """Génère les styles pour la barre d'outils"""
    return f"""
    QToolBar {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {bg_gradient_start}, stop: 1 {bg_gradient_end});
        border: none;
        border-bottom: 1px solid {border_color};
        spacing: 8px;
        padding: 12px 16px;
        min-height: 56px;
    }}

    QToolButton {{
        background: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        font-weight: 500;
        padding: 10px 14px;
        min-height: 40px;
        min-width: 40px;
    }}

    QToolButton:hover {{
        background: rgba(0, 0, 0, 0.1);
        border-color: rgba(0, 0, 0, 0.2);
    }}

    QToolButton:pressed {{
        background: rgba(0, 0, 0, 0.2);
    }}

    QToolButton:checked {{
        background: {Colors.BLUE_PRIMARY};
        border-color: {Colors.BLUE_PRIMARY};
        color: white;
    }}
    """

# ===== THÈMES COMPLETS =====

class ModernLightTheme:
    """Thème moderne clair"""
    
    @staticmethod
    def get_styles():
        base = create_base_styles()
        
        # Configuration principale
        main_bg = f"""
        QMainWindow {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {Colors.WHITE}, stop: 1 {Colors.LIGHT_GRAY});
            color: #1f2937;
        }}

        QDialog {{
            background: {Colors.WHITE};
            border: 1px solid #e5e7eb;
            border-radius: 12px;
        }}
        """
        
        buttons = create_button_styles(
            bg_color=Colors.WHITE,
            hover_color="#f9fafb", 
            pressed_color="#e5e7eb",
            text_color="#374151",
            border_color="#d1d5db"
        )
        
        inputs = create_input_styles(
            bg_color=Colors.WHITE,
            border_color="#d1d5db",
            text_color="#111827",
            focus_color=Colors.BLUE_PRIMARY
        )
        
        tables = create_table_styles(
            bg_color=Colors.WHITE,
            alt_bg_color="#f8fafc",
            border_color="#e2e8f0", 
            text_color="#475569",
            header_bg="#f8fafc"
        )
        
        toolbar = create_toolbar_styles(
            bg_gradient_start=Colors.WHITE,
            bg_gradient_end=Colors.LIGHT_GRAY,
            border_color="#e5e7eb"
        )
        
        additional = f"""
        /* Groupes */
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

        /* Barres de défilement */
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

        /* Onglets */
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

        /* Tooltips */
        QToolTip {{
            background: #1f2937;
            border: none;
            border-radius: 6px;
            color: white;
            padding: 8px 12px;
            font-size: 12px;
            font-weight: 500;
        }}
        """
        
        return base + main_bg + buttons + inputs + tables + toolbar + additional

class ModernDarkTheme:
    """Thème moderne sombre"""
    
    @staticmethod
    def get_styles():
        base = create_base_styles()
        
        # Configuration principale
        main_bg = f"""
        QMainWindow {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {Colors.DARK_BG}, stop: 1 #111827);
            color: {Colors.DARK_TEXT};
        }}

        QDialog {{
            background: {Colors.DARK_SURFACE};
            border: 1px solid {Colors.DARK_BORDER};
            border-radius: 12px;
        }}
        """
        
        buttons = create_button_styles(
            bg_color=Colors.DARK_SURFACE,
            hover_color="#374151",
            pressed_color="#1f2937", 
            text_color=Colors.DARK_TEXT,
            border_color="#4b5563"
        )
        
        inputs = create_input_styles(
            bg_color=Colors.DARK_BG,
            border_color=Colors.DARK_BORDER,
            text_color=Colors.DARK_TEXT,
            focus_color="#60a5fa"
        )
        
        tables = create_table_styles(
            bg_color=Colors.DARK_BG,
            alt_bg_color=Colors.DARK_SURFACE,
            border_color=Colors.DARK_BORDER,
            text_color=Colors.DARK_TEXT,
            header_bg=Colors.DARK_SURFACE
        )
        
        toolbar = create_toolbar_styles(
            bg_gradient_start=Colors.DARK_SURFACE,
            bg_gradient_end=Colors.DARK_BG,
            border_color=Colors.DARK_BORDER
        )
        
        additional = f"""
        /* Groupes sombres */
        QGroupBox {{
            background: {Colors.DARK_BG};
            border: 1px solid {Colors.DARK_BORDER};
            border-radius: 12px;
            font-weight: 600;
            color: {Colors.DARK_TEXT};
            margin-top: 1ex;
            padding-top: 20px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 4px 12px;
            background: #3b82f6;
            color: white;
            font-weight: 600;
            border-radius: 6px;
            margin-left: 12px;
        }}

        /* Barres de défilement sombres */
        QScrollBar:vertical {{
            background: {Colors.DARK_SURFACE};
            width: 14px;
            border-radius: 7px;
            margin: 0;
        }}

        QScrollBar::handle:vertical {{
            background: {Colors.DARK_BORDER};
            border-radius: 7px;
            min-height: 20px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: #718096;
        }}

        /* Onglets sombres */
        QTabWidget::pane {{
            background: {Colors.DARK_BG};
            border: 1px solid {Colors.DARK_BORDER};
            border-radius: 8px;
            border-top-left-radius: 0;
            padding: 0;
        }}

        QTabBar::tab {{
            background: {Colors.DARK_SURFACE};
            border: 1px solid {Colors.DARK_BORDER};
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            color: #a0aec0;
            font-weight: 500;
            margin-right: 2px;
            padding: 10px 20px;
            min-width: 80px;
        }}

        QTabBar::tab:selected {{
            background: {Colors.DARK_BG};
            border-bottom: 1px solid {Colors.DARK_BG};
            color: #3b82f6;
            font-weight: 600;
        }}

        QTabBar::tab:hover:!selected {{
            background: #374151;
            color: {Colors.DARK_TEXT};
        }}

        /* Tooltips sombres */
        QToolTip {{
            background: #374151;
            border: 1px solid #4b5563;
            border-radius: 6px;
            color: white;
            padding: 8px 12px;
            font-size: 12px;
            font-weight: 500;
        }}

        /* Style pour toolbar buttons sombres */
        QToolButton {{
            color: #a0aec0;
        }}

        QToolButton:hover {{
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
            color: {Colors.DARK_TEXT};
        }}
        """
        
        return base + main_bg + buttons + inputs + tables + toolbar + additional

# ===== GESTIONNAIRE DE THÈMES =====
class StyleManager:
    """Gestionnaire principal des styles"""
    
    def __init__(self):
        self.themes = {
            ThemeNames.DEFAULT: self._get_default_theme,
            ThemeNames.LIGHT_MODERN: ModernLightTheme.get_styles,
            ThemeNames.DARK_MODERN: ModernDarkTheme.get_styles,
        }
        
    def _get_default_theme(self):
        """Thème par défaut simple et compatible"""
        return f"""
        QMainWindow {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {Colors.WHITE}, stop: 1 {Colors.LIGHT_GRAY});
            color: #333333;
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: 14px;
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

        QLineEdit {{
            background: white;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 6px 8px;
            selection-background-color: {Colors.BLUE_PRIMARY};
            font-size: 14px;
        }}

        QLineEdit:focus {{
            border-color: {Colors.BLUE_PRIMARY};
        }}

        QGroupBox {{
            background: white;
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
            color: white;
            font-weight: bold;
            border-radius: 4px;
            margin-left: 8px;
        }}
        """
    
    def get_theme(self, theme_name):
        """Retourne le CSS pour un thème donné"""
        if theme_name in self.themes:
            try:
                return self.themes[theme_name]()
            except Exception as exc:
                logger.error(f"Erreur lors de la génération du thème {theme_name}: {exc}")
                return self._get_default_theme()
        else:
            logger.warning(f"Thème {theme_name} non trouvé, utilisation du thème par défaut")
            return self._get_default_theme()
    
    def get_available_themes(self):
        """Retourne la liste des thèmes disponibles"""
        return {
            ThemeNames.DEFAULT: "Défaut",
            ThemeNames.LIGHT_MODERN: "Moderne Clair",
            ThemeNames.DARK_MODERN: "Moderne Sombre",
        }
    
    def apply_theme(self, theme_name):
        """Applique un thème et le sauvegarde en base"""
        try:
            settings = Settings.get_or_create(id=1)[0]
            settings.theme = theme_name
            settings.save()
            logger.info(f"Thème appliqué: {theme_name}")
            return self.get_theme(theme_name)
        except Exception as exc:
            logger.error(f"Erreur lors de l'application du thème: {exc}")
            return self._get_default_theme()

# ===== FONCTIONS PUBLIQUES =====

# Instance globale du gestionnaire
_style_manager = StyleManager()

def get_style():
    """Fonction principale pour obtenir le style actuel"""
    try:
        settings = Settings.get_or_create(id=1)[0]
        
        # Mapping des anciens thèmes vers les nouveaux
        theme_mapping = {
            Settings.DF: ThemeNames.DEFAULT,
            Settings.BL: ThemeNames.LIGHT_MODERN,
            Settings.DK: ThemeNames.DARK_MODERN,
            Settings.FAD: ThemeNames.DEFAULT,  # Temporaire
        }
        
        current_theme = theme_mapping.get(settings.theme, ThemeNames.DEFAULT)
        logger.debug(f"Thème demandé: {settings.theme} -> {current_theme}")
        
        return _style_manager.get_theme(current_theme)
        
    except Exception as exc:
        logger.error(f"Erreur lors de la récupération du style: {exc}")
        return _style_manager.get_theme(ThemeNames.DEFAULT)

def get_available_themes():
    """Retourne les thèmes disponibles"""
    return _style_manager.get_available_themes()

def apply_theme(theme_name):
    """Applique un nouveau thème"""
    return _style_manager.apply_theme(theme_name)

def is_dark_theme():
    """Détermine si le thème actuel est sombre"""
    try:
        settings = Settings.get_or_create(id=1)[0]
        return settings.theme in [Settings.DK, ThemeNames.DARK_MODERN]
    except:
        return False

# Variable globale pour compatibilité
theme = get_style()

# Log d'initialisation
logger.info("Gestionnaire de styles moderne initialisé")
logger.info(f"Thèmes disponibles: {list(get_available_themes().keys())}") 