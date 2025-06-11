# -*- coding: utf-8 -*-
"""
Gestionnaire de thèmes centralisé pour l'application
Résout les problèmes de styles CSS hardcodés qui interfèrent avec les thèmes
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    """Gestionnaire centralisé des thèmes pour toute l'application"""
    
    themeChanged = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_theme = "light_modern"
        self.theme_styles = {}
        self._init_theme_styles()
        
    def _init_theme_styles(self):
        """Initialise tous les styles des thèmes"""
        
        # Thème moderne clair
        self.theme_styles["light_modern"] = {
            "main_bg": "#ffffff",
            "secondary_bg": "#f8f9fa",
            "primary_color": "#0d6efd",
            "success_color": "#28a745",
            "warning_color": "#ffc107",
            "danger_color": "#dc3545",
            "text_color": "#212529",
            "text_muted": "#6c757d",
            "border_color": "#e2e8f0",
            "border_hover": "#0d6efd",
            
            # Styles spécifiques
            "button_primary": """
                QPushButton {
                    background-color: #0d6efd;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #0b5ed7; }
                QPushButton:pressed { background-color: #0a58ca; }
            """,
            "button_success": """
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #218838; }
                QPushButton:pressed { background-color: #1e7e34; }
            """,
            "button_danger": """
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #c82333; }
                QPushButton:pressed { background-color: #bd2130; }
            """,
            "input_field": """
                QLineEdit {
                    background-color: #ffffff;
                    border: 2px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: #212529;
                }
                QLineEdit:focus { border-color: #0d6efd; }
            """,
            "combobox": """
                QComboBox {
                    background-color: #ffffff;
                    border: 2px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: #212529;
                }
                QComboBox:hover { border-color: #0d6efd; }
            """,
            "error_label": """
                QLabel {
                    color: #dc3545;
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: 500;
                }
            """,
            "groupbox": """
                QGroupBox {
                    font-weight: 600;
                    border: 2px solid #e2e8f0;
                    border-radius: 12px;
                    margin-top: 12px;
                    padding-top: 12px;
                    background-color: #ffffff;
                    color: #212529;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 20px;
                    padding: 0 8px 0 8px;
                    background-color: #ffffff;
                    color: #2c3e50;
                }
            """
        }
        
        # Thème moderne sombre
        self.theme_styles["dark_modern"] = {
            "main_bg": "#1a1a1a",
            "secondary_bg": "#2d2d2d",
            "primary_color": "#4dabf7",
            "success_color": "#40c057",
            "warning_color": "#ffd43b",
            "danger_color": "#f03e3e",
            "text_color": "#e9ecef",
            "text_muted": "#adb5bd",
            "border_color": "#495057",
            "border_hover": "#4dabf7",
            
            "button_primary": """
                QPushButton {
                    background-color: #4dabf7;
                    color: #000000;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #339af0; }
                QPushButton:pressed { background-color: #228be6; }
            """,
            "button_success": """
                QPushButton {
                    background-color: #40c057;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #37b24d; }
                QPushButton:pressed { background-color: #2f9e44; }
            """,
            "button_danger": """
                QPushButton {
                    background-color: #f03e3e;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #e03131; }
                QPushButton:pressed { background-color: #c92a2a; }
            """,
            "input_field": """
                QLineEdit {
                    background-color: #2d2d2d;
                    border: 2px solid #495057;
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: #e9ecef;
                }
                QLineEdit:focus { border-color: #4dabf7; }
            """,
            "combobox": """
                QComboBox {
                    background-color: #2d2d2d;
                    border: 2px solid #495057;
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: #e9ecef;
                }
                QComboBox:hover { border-color: #4dabf7; }
            """,
            "error_label": """
                QLabel {
                    color: #f03e3e;
                    background-color: #2d1618;
                    border: 1px solid #f03e3e;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: 500;
                }
            """,
            "groupbox": """
                QGroupBox {
                    font-weight: 600;
                    border: 2px solid #495057;
                    border-radius: 12px;
                    margin-top: 12px;
                    padding-top: 12px;
                    background-color: #2d2d2d;
                    color: #e9ecef;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 20px;
                    padding: 0 8px 0 8px;
                    background-color: #2d2d2d;
                    color: #e9ecef;
                }
            """
        }
        
    def apply_theme(self, theme_key: str):
        """Applique un thème à toute l'application"""
        if theme_key not in self.theme_styles:
            print(f"⚠️ Thème '{theme_key}' non trouvé, utilisation du thème par défaut")
            theme_key = "light_modern"
            
        self.current_theme = theme_key
        theme = self.theme_styles[theme_key]
        
        # Style global de l'application
        app_style = f"""
        QMainWindow {{
            background-color: {theme['main_bg']};
            color: {theme['text_color']};
        }}
        
        QWidget {{
            background-color: {theme['main_bg']};
            color: {theme['text_color']};
        }}
        
        QDialog {{
            background-color: {theme['main_bg']};
            color: {theme['text_color']};
        }}
        
        QLabel {{
            color: {theme['text_color']};
            background-color: transparent;
        }}
        
        {theme['input_field']}
        {theme['combobox']}
        {theme['groupbox']}
        """
        
        # Appliquer le style à l'application
        app = QApplication.instance()
        if app:
            app.setStyleSheet(app_style)
            print(f"🎨 Thème '{theme_key}' appliqué avec succès")
            
        self.themeChanged.emit(theme_key)
        
    def get_button_style(self, button_type: str) -> str:
        """Retourne le style pour un type de bouton spécifique"""
        theme = self.theme_styles[self.current_theme]
        return theme.get(f"button_{button_type}", theme.get("button_primary", ""))
        
    def get_error_style(self) -> str:
        """Retourne le style pour les messages d'erreur"""
        theme = self.theme_styles[self.current_theme]
        return theme.get("error_label", "")
        
    def get_current_theme(self) -> str:
        """Retourne le thème actuel"""
        return self.current_theme
        
    def get_available_themes(self) -> dict:
        """Retourne la liste des thèmes disponibles"""
        return {
            "light_modern": "🌟 Moderne Clair",
            "dark_modern": "🌙 Moderne Sombre"
        }

# Instance globale du gestionnaire de thèmes
theme_manager = ThemeManager()

def get_theme_manager():
    """Retourne l'instance globale du gestionnaire de thèmes"""
    return theme_manager

def apply_theme_to_widget(widget, widget_type: str = "default"):
    """Applique le thème actuel à un widget spécifique"""
    if not hasattr(widget, 'setStyleSheet'):
        return
        
    manager = get_theme_manager()
    theme = manager.theme_styles[manager.current_theme]
    
    # Appliquer le style selon le type de widget
    if widget_type == "button_primary":
        widget.setStyleSheet(manager.get_button_style("primary"))
    elif widget_type == "button_success":
        widget.setStyleSheet(manager.get_button_style("success"))
    elif widget_type == "button_danger":
        widget.setStyleSheet(manager.get_button_style("danger"))
    elif widget_type == "error_label":
        widget.setStyleSheet(manager.get_error_style())
    elif widget_type == "input_field":
        widget.setStyleSheet(theme["input_field"])
    elif widget_type == "combobox":
        widget.setStyleSheet(theme["combobox"])
    elif widget_type == "groupbox":
        widget.setStyleSheet(theme["groupbox"]) 