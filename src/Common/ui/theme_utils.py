#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

"""
Utilitaires pour la gestion dynamique des thèmes
Permet le changement de thème sans redémarrage de l'application
"""

from ..cstatic import logger
from ..models import Settings


def apply_theme_to_application(theme_name, main_window=None):
    """
    Applique un thème à toute l'application de manière dynamique
    
    Args:
        theme_name (str): Nom du thème à appliquer
        main_window (QMainWindow, optional): Fenêtre principale. Si None, essaie de la détecter automatiquement
    
    Returns:
        bool: True si le thème a été appliqué avec succès, False sinon
    """
    try:
        # Sauvegarder le thème en base de données
        settings = Settings.init_settings()
        settings.theme = theme_name
        settings.save()
        logger.info(f"Thème sauvegardé: {theme_name}")
        
        # Obtenir le style CSS du nouveau thème
        new_style = get_theme_style()
        
        # Appliquer le thème à TOUTE l'application (toutes fenêtres et dialogues)
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        
        if app:
            # Appliquer le style à toute l'application
            app.setStyleSheet(new_style)
            logger.info("Style appliqué à toute l'application")
            
            # Rafraîchir toutes les fenêtres et dialogues ouverts
            refresh_all_application_windows(app)
            
            # Détecter la fenêtre principale pour notification
            if main_window is None:
                main_window = detect_main_window()
            
            # Notifier l'utilisateur si possible
            if main_window:
                notify_theme_change(main_window, theme_name)
            
            logger.info(f"Thème '{theme_name}' appliqué avec succès à toute l'application sans redémarrage")
            return True
        else:
            logger.warning("Impossible d'obtenir l'instance de QApplication")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de l'application du thème '{theme_name}': {e}")
        return False


def get_theme_style():
    """
    Obtient le style CSS du thème actuel depuis les paramètres
    
    Returns:
        str: Code CSS du thème actuel
    """
    try:
        # Essayer d'importer depuis le nouveau gestionnaire de styles
        try:
            from .style_manager import get_style
        except ImportError:
            # Fallback vers l'ancien système
            from .style_qss import get_style
        
        return get_style()
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du style: {e}")
        # Retourner un style de base en cas d'erreur
        return """
        QMainWindow {
            background: #f5f5f5;
            color: #333333;
            font-family: "Segoe UI", Arial, sans-serif;
        }
        """


def detect_main_window():
    """
    Détecte automatiquement la fenêtre principale de l'application
    
    Returns:
        QMainWindow or None: La fenêtre principale si trouvée
    """
    try:
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app:
            # Chercher la fenêtre principale parmi les widgets de niveau supérieur
            for widget in app.topLevelWidgets():
                if hasattr(widget, 'menuBar') and hasattr(widget, 'centralWidget'):
                    return widget
                    
            # Si pas trouvé, prendre le premier widget de niveau supérieur qui n'est pas une dialog
            for widget in app.topLevelWidgets():
                if widget.isVisible() and not hasattr(widget, 'exec_'):
                    return widget
                    
        return None
        
    except Exception as e:
        logger.debug(f"Erreur lors de la détection de la fenêtre principale: {e}")
        return None


def refresh_all_application_windows(app):
    """
    Rafraîchit toutes les fenêtres et dialogues de l'application
    
    Args:
        app (QApplication): Instance de l'application Qt
    """
    try:
        # Rafraîchir tous les widgets de niveau supérieur (fenêtres et dialogues)
        for widget in app.topLevelWidgets():
            if widget.isVisible():
                # Rafraîchir le widget
                widget.update()
                widget.repaint()
                
                # Rafraîchir récursivement tous ses enfants
                refresh_widgets_recursively(widget)
                
                # Rafraîchir les composants spéciaux si c'est une fenêtre principale
                if hasattr(widget, 'menuBar') and hasattr(widget, 'centralWidget'):
                    refresh_special_components(widget)
                
                logger.debug(f"Widget de niveau supérieur rafraîchi: {widget.__class__.__name__}")
        
        # Forcer l'application à traiter tous les événements en attente
        app.processEvents()
        
        logger.info("Toutes les fenêtres et dialogues ont été rafraîchis")
        
    except Exception as e:
        logger.error(f"Erreur lors du rafraîchissement de toutes les fenêtres: {e}")


def refresh_widgets_recursively(widget):
    """
    Rafraîchit récursivement un widget et tous ses enfants
    
    Args:
        widget: Widget à rafraîchir
    """
    try:
        # Rafraîchir le widget actuel
        if hasattr(widget, 'update') and hasattr(widget, 'repaint'):
            widget.update()
            widget.repaint()
        
        # Rafraîchir tous les widgets enfants
        for child in widget.findChildren(object):
            if hasattr(child, 'update') and hasattr(child, 'repaint'):
                child.update()
                child.repaint()
                
                # Appeler les méthodes de rafraîchissement spécifiques si elles existent
                refresh_methods = ['refresh', 'refresh_', 'reload', 'update_content']
                for method_name in refresh_methods:
                    if hasattr(child, method_name) and callable(getattr(child, method_name)):
                        try:
                            getattr(child, method_name)()
                        except:
                            pass  # Ignore les erreurs pour éviter de casser l'application
                            
    except Exception as e:
        logger.debug(f"Erreur lors du rafraîchissement récursif: {e}")


def refresh_special_components(main_window):
    """
    Rafraîchit les composants spéciaux de l'interface (barres d'outils, menus, etc.)
    
    Args:
        main_window (QMainWindow): Fenêtre principale
    """
    try:
        # Rafraîchir la barre de menu
        if hasattr(main_window, 'menuBar') and callable(main_window.menuBar):
            menu_bar = main_window.menuBar()
            if menu_bar:
                menu_bar.update()
                menu_bar.repaint()
        
        # Rafraîchir la barre d'outils
        if hasattr(main_window, 'toolbar') and main_window.toolbar:
            main_window.toolbar.update()
            main_window.toolbar.repaint()
        
        # Rafraîchir la barre de statut
        if hasattr(main_window, 'statusBar') and callable(main_window.statusBar):
            status_bar = main_window.statusBar()
            if status_bar:
                status_bar.update()
                status_bar.repaint()
        
        # Rafraîchir le widget central
        central_widget = main_window.centralWidget()
        if central_widget:
            central_widget.update()
            central_widget.repaint()
            
    except Exception as e:
        logger.debug(f"Erreur lors du rafraîchissement des composants spéciaux: {e}")


def notify_theme_change(main_window, theme_name):
    """
    Notifie l'utilisateur du changement de thème
    
    Args:
        main_window: Fenêtre principale
        theme_name (str): Nom du thème appliqué
    """
    try:
        # Essayer d'utiliser le système de notification de l'application
        if hasattr(main_window, 'Notify') and callable(main_window.Notify):
            main_window.Notify(f"Thème '{theme_name}' appliqué avec succès !", "success")
        
        # Mettre à jour la barre de statut si disponible
        elif hasattr(main_window, 'statusBar') and callable(main_window.statusBar):
            status_bar = main_window.statusBar()
            if status_bar:
                status_bar.showMessage(f"Thème appliqué: {theme_name}", 3000)
                
    except Exception as e:
        logger.debug(f"Erreur lors de la notification: {e}")


def get_available_themes():
    """
    Retourne la liste des thèmes disponibles
    
    Returns:
        dict: Dictionnaire {clé_thème: nom_affiché}
    """
    try:
        # Essayer d'importer depuis le nouveau gestionnaire
        try:
            from .style_manager import get_available_themes as get_themes
            return get_themes()
        except ImportError:
            # Fallback vers l'ancien système
            from .style_qss import get_available_themes as get_themes
            return get_themes()
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des thèmes disponibles: {e}")
        # Retourner une liste basique en cas d'erreur
        return {
            "default": "Défaut",
            "light_modern": "Clair", 
            "dark_modern": "Sombre"
        }


def is_theme_dark(theme_name=None):
    """
    Détermine si un thème est sombre
    
    Args:
        theme_name (str, optional): Nom du thème. Si None, utilise le thème actuel
    
    Returns:
        bool: True si le thème est sombre
    """
    try:
        if theme_name is None:
            # Obtenir le thème actuel
            settings = Settings.get_or_create(id=1)[0]
            theme_name = settings.theme
        
        # Listes des thèmes considérés comme sombres
        dark_themes = ["dark_modern", "CLASSIC_DARK", "dark", "sombre"]
        
        return theme_name.lower() in [t.lower() for t in dark_themes]
        
    except Exception as e:
        logger.debug(f"Erreur lors de la vérification du thème sombre: {e}")
        return False


# Fonctions de compatibilité pour l'ancien système
def change_theme_dynamically(theme_name, main_window=None):
    """
    Fonction de compatibilité pour changer de thème dynamiquement
    Alias pour apply_theme_to_application
    """
    return apply_theme_to_application(theme_name, main_window)


# Variables pour la compatibilité avec l'ancien système
try:
    from ..models import Settings
    
    # Initialiser Settings si pas déjà fait
    Settings.init_settings()
    
except Exception as e:
    logger.warning(f"Impossible d'initialiser Settings dans theme_utils: {e}")


# Log d'initialisation
logger.info("Module theme_utils initialisé - Changement de thème dynamique disponible")


def apply_theme_to_new_widgets():
    """
    S'assure que les nouveaux widgets créés héritent du thème actuel
    Cette fonction peut être appelée lors de la création de nouveaux dialogues
    """
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        
        if app:
            current_style = app.styleSheet()
            if current_style:
                # Le style est déjà appliqué au niveau de l'application
                # Les nouveaux widgets l'hériteront automatiquement
                logger.debug("Style global de l'application disponible pour nouveaux widgets")
                return True
        return False
        
    except Exception as e:
        logger.debug(f"Erreur lors de la vérification du style global: {e}")
        return False


def refresh_all_widgets(main_window):
    """
    Fonction de compatibilité - rafraîchit tous les widgets depuis une fenêtre principale
    
    Args:
        main_window (QMainWindow): Fenêtre principale à rafraîchir
    """
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        
        if app:
            # Utiliser la nouvelle fonction qui rafraîchit toute l'application
            refresh_all_application_windows(app)
        else:
            # Fallback vers l'ancienne méthode
            main_window.update()
            main_window.repaint()
            refresh_widgets_recursively(main_window)
            refresh_special_components(main_window)
            
    except Exception as e:
        logger.debug(f"Erreur lors du rafraîchissement des widgets: {e}")


def ensure_dialog_theme_inheritance(dialog):
    """
    S'assure qu'un dialogue hérite du thème de l'application
    
    Args:
        dialog: Le dialogue à thématiser
    
    Returns:
        bool: True si le thème a été appliqué avec succès
    """
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        
        if app:
            current_style = app.styleSheet()
            if current_style:
                # Le dialogue hérite automatiquement du style de l'application
                # Mais on peut forcer le rafraîchissement
                dialog.update()
                dialog.repaint()
                refresh_widgets_recursively(dialog)
                logger.debug(f"Thème appliqué au dialogue: {dialog.__class__.__name__}")
                return True
        return False
        
    except Exception as e:
        logger.debug(f"Erreur lors de l'application du thème au dialogue: {e}")
        return False


def get_current_application_theme():
    """
    Obtient le thème actuellement appliqué à l'application
    
    Returns:
        str: Le style CSS actuel de l'application, ou une chaîne vide si aucun
    """
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        
        if app:
            return app.styleSheet()
        return ""
        
    except Exception as e:
        logger.debug(f"Erreur lors de la récupération du thème actuel: {e}")
        return ""


def apply_theme_immediately():
    """
    Force l'application immédiate du thème actuel à toute l'application
    Utile pour s'assurer que tous les widgets sont correctement thématisés
    
    Returns:
        bool: True si le thème a été appliqué avec succès
    """
    try:
        # Obtenir le thème actuel depuis la base de données
        settings = Settings.get_or_create(id=1)[0]
        current_theme = settings.theme
        
        # Réappliquer le thème
        return apply_theme_to_application(current_theme)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'application immédiate du thème: {e}")
        return False 