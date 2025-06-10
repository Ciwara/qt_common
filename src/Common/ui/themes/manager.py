#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gestionnaire principal des thèmes
Version 2.0 - Gestion unifiée et simplifiée
"""

from ...cstatic import logger
from ...models import Settings
from .config import (
    get_available_themes, 
    get_current_theme, 
    set_current_theme, 
    theme_exists,
    is_theme_dark
)
from .styles import get_theme_style

class ThemeManager:
    """Gestionnaire principal pour tous les aspects des thèmes"""
    
    def __init__(self):
        self.current_theme = get_current_theme()
        logger.info(f"ThemeManager initialisé avec le thème: {self.current_theme}")
    
    def get_available_themes(self):
        """Retourne tous les thèmes disponibles"""
        return get_available_themes()
    
    def get_current_theme(self):
        """Retourne le thème actuel"""
        self.current_theme = get_current_theme()
        return self.current_theme
    
    def set_theme(self, theme_key):
        """Change le thème actuel"""
        if not theme_exists(theme_key):
            logger.error(f"Thème '{theme_key}' inexistant")
            return False
        
        success = set_current_theme(theme_key)
        if success:
            self.current_theme = theme_key
            logger.info(f"Thème changé vers: {theme_key}")
        return success
    
    def get_theme_style(self, theme_key=None):
        """Retourne le style CSS d'un thème"""
        return get_theme_style(theme_key)
    
    def apply_theme_to_application(self, theme_key=None):
        """Applique un thème à toute l'application Qt"""
        if theme_key is None:
            theme_key = self.current_theme
        
        try:
            from PyQt5.QtWidgets import QApplication
            
            app = QApplication.instance()
            if not app:
                logger.warning("Aucune instance QApplication trouvée")
                return False
            
            # Sauvegarder le thème
            if not self.set_theme(theme_key):
                return False
            
            # Obtenir le style CSS
            style = self.get_theme_style(theme_key)
            
            # Appliquer le style à l'application
            app.setStyleSheet(style)
            
            # Rafraîchir toutes les fenêtres
            self._refresh_all_windows(app)
            
            logger.info(f"Thème '{theme_key}' appliqué à toute l'application")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'application du thème: {e}")
            return False
    
    def _refresh_all_windows(self, app):
        """Rafraîchit toutes les fenêtres de l'application"""
        try:
            for widget in app.topLevelWidgets():
                if widget.isVisible():
                    widget.update()
                    widget.repaint()
                    # Rafraîchir récursivement
                    self._refresh_widget_recursively(widget)
            
            # Traiter les événements en attente
            app.processEvents()
            
        except Exception as e:
            logger.debug(f"Erreur lors du rafraîchissement: {e}")
    
    def _refresh_widget_recursively(self, widget):
        """Rafraîchit récursivement un widget et ses enfants"""
        try:
            for child in widget.findChildren(object):
                if hasattr(child, 'update') and hasattr(child, 'repaint'):
                    child.update()
                    child.repaint()
        except Exception as e:
            logger.debug(f"Erreur lors du rafraîchissement récursif: {e}")
    
    def is_current_theme_dark(self):
        """Vérifie si le thème actuel est sombre"""
        return is_theme_dark(self.current_theme)
    
    def get_theme_info(self, theme_key=None):
        """Retourne les informations d'un thème"""
        if theme_key is None:
            theme_key = self.current_theme
        
        from .config import ThemeConfig
        return ThemeConfig.get_theme_info(theme_key)
    
    def notify_theme_change(self, main_window, theme_name):
        """Notifie l'utilisateur du changement de thème"""
        try:
            if hasattr(main_window, 'Notify') and callable(main_window.Notify):
                theme_info = self.get_theme_info(theme_name)
                theme_display = theme_info['name'] if theme_info else theme_name
                main_window.Notify(f"Thème '{theme_display}' appliqué avec succès !", "success")
            
            elif hasattr(main_window, 'statusBar') and callable(main_window.statusBar):
                status_bar = main_window.statusBar()
                if status_bar:
                    theme_info = self.get_theme_info(theme_name)
                    theme_display = theme_info['name'] if theme_info else theme_name
                    status_bar.showMessage(f"Thème appliqué: {theme_display}", 3000)
                    
        except Exception as e:
            logger.debug(f"Erreur lors de la notification: {e}")

# ===== INSTANCE GLOBALE =====

# Instance globale du gestionnaire de thèmes
_theme_manager = None

def get_theme_manager():
    """Retourne l'instance globale du gestionnaire de thèmes"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager

# ===== FONCTIONS DE COMPATIBILITÉ =====

def apply_theme_to_application(theme_name, main_window=None):
    """
    Fonction de compatibilité pour appliquer un thème à l'application
    Compatible avec l'ancien système theme_utils
    """
    manager = get_theme_manager()
    success = manager.apply_theme_to_application(theme_name)
    
    if success and main_window:
        manager.notify_theme_change(main_window, theme_name)
    
    return success

def apply_theme_immediately():
    """
    Fonction de compatibilité pour appliquer immédiatement le thème actuel
    Compatible avec l'ancien système theme_utils
    """
    manager = get_theme_manager()
    current_theme = manager.get_current_theme()
    return manager.apply_theme_to_application(current_theme)

# Log d'initialisation
logger.info("ThemeManager v2.0 initialisé") 