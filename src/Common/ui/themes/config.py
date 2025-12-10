#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration centralisée et nettoyée des thèmes
Version 2.0 - Système unifié et optimisé
"""

import platform
from ...cstatic import logger
from ...models import Settings

# ===== CONFIGURATION CENTRALISÉE DES THÈMES =====

class ThemeConfig:
    """Configuration centralisée de tous les thèmes de l'application"""
    
    # Définition complète de tous les thèmes disponibles
    THEMES = {
        "system": {
            "name": "Thème Système", 
            "description": "Suit automatiquement les préférences système (clair/sombre)",
            "is_dark": None,  # Dynamique selon le système
            "category": "Système",
            "author": "System",
            "version": "3.0"
        },
        "light_modern": {
            "name": "Moderne Clair",
            "description": "Interface moderne et claire avec des effets visuels",
            "is_dark": False,
            "category": "Moderne",
            "author": "Qt Common",
            "version": "2.0"
        },
        "dark_modern": {
            "name": "Moderne Sombre", 
            "description": "Interface moderne sombre, idéale pour le travail nocturne",
            "is_dark": True,
            "category": "Moderne",
            "author": "Qt Common",
            "version": "2.0"
        }
    }
    
    # Thème par défaut
    DEFAULT_THEME = "system"
    
    @classmethod
    def get_all_themes(cls):
        """Retourne tous les thèmes {theme_key: theme_name}"""
        return {key: config["name"] for key, config in cls.THEMES.items()}
    
    @classmethod
    def get_theme_info(cls, theme_key):
        """Retourne les informations détaillées d'un thème"""
        return cls.THEMES.get(theme_key)
    
    @classmethod
    def is_dark_theme(cls, theme_key):
        """Détermine si un thème est sombre"""
        theme_info = cls.get_theme_info(theme_key)
        if not theme_info:
            return False
        
        is_dark = theme_info.get("is_dark")
        
        # Pour le thème système, détecter dynamiquement
        if theme_key == "system" or is_dark is None:
            return cls._detect_system_dark_mode()
        
        return is_dark
    
    @classmethod
    def _detect_system_dark_mode(cls):
        """Détecte si le système est en mode sombre"""
        try:
            system = platform.system()
            
            # macOS - utiliser les préférences utilisateur via defaults
            if system == "Darwin":
                try:
                    from subprocess import check_output, CalledProcessError
                    try:
                        result = check_output(["defaults", "read", "-g", "AppleInterfaceStyle"]).decode().strip()
                        return result == "Dark"
                    except CalledProcessError:
                        # Si la clé n'existe pas, c'est le mode clair (par défaut avant macOS Mojave)
                        return False
                except Exception:
                    # Fallback: essayer avec AppKit si disponible
                    try:
                        import AppKit
                        appearance = AppKit.NSAppearance.currentAppearance()
                        if appearance:
                            dark_appearance = appearance.name()
                            return "Dark" in str(dark_appearance)
                    except ImportError:
                        pass
            
            # Windows - utiliser les APIs Windows
            elif system == "Windows":
                try:
                    import winreg
                    # Vérifier la clé de registre Windows
                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                    )
                    apps_use_light_theme = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
                    winreg.CloseKey(key)
                    return apps_use_light_theme == 0
                except:
                    pass
            
            # Linux - vérifier les variables d'environnement GTK
            elif system == "Linux":
                try:
                    import os
                    gtk_theme = os.environ.get("GTK_THEME", "").lower()
                    if "dark" in gtk_theme:
                        return True
                    
                    # Vérifier les préférences via gsettings si disponible
                    from subprocess import check_output
                    try:
                        result = check_output(["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"]).decode().strip()
                        return "dark" in result.lower()
                    except:
                        pass
                except:
                    pass
            
            # Fallback: utiliser la palette Qt si disponible
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    palette = app.palette()
                    window_color = palette.color(palette.Window)
                    # Si la couleur de fond est sombre, considérer que c'est le mode sombre
                    return window_color.lightness() < 128
            except:
                pass
            
            # Par défaut, retourner False (mode clair)
            return False
            
        except Exception as e:
            logger.debug(f"Erreur lors de la détection du mode sombre système: {e}")
            return False
    
    @classmethod
    def resolve_system_theme(cls):
        """Résout le thème système vers un thème réel (light_modern ou dark_modern)"""
        if cls._detect_system_dark_mode():
            return "dark_modern"
        return "light_modern"
    
    @classmethod
    def theme_exists(cls, theme_key):
        """Vérifie si un thème existe"""
        return theme_key in cls.THEMES
    
    @classmethod
    def get_default_theme(cls):
        """Retourne la clé du thème par défaut"""
        return cls.DEFAULT_THEME
    

# ===== FONCTIONS PUBLIQUES SIMPLIFIÉES =====

def get_available_themes():
    """Fonction principale pour obtenir tous les thèmes disponibles"""
    try:
        return ThemeConfig.get_all_themes()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des thèmes: {e}")
        return {"light_modern": "Moderne Clair", "dark_modern": "Moderne Sombre"}

def is_theme_dark(theme_key):
    """Fonction principale pour vérifier si un thème est sombre"""
    try:
        return ThemeConfig.is_dark_theme(theme_key)
    except Exception as e:
        logger.debug(f"Erreur lors de la vérification du thème sombre: {e}")
        return False

def theme_exists(theme_key):
    """Fonction principale pour vérifier l'existence d'un thème"""
    try:
        return ThemeConfig.theme_exists(theme_key)
    except Exception as e:
        logger.debug(f"Erreur lors de la vérification de l'existence du thème: {e}")
        return False

def get_current_theme():
    """Obtient le thème actuellement configuré avec persistance améliorée"""
    try:
        # Utiliser init_settings pour assurer l'existence de l'enregistrement
        settings = Settings.init_settings()
        current_theme = settings.theme
        
        # Si pas de thème configuré, utiliser le thème système par défaut
        if not current_theme:
            current_theme = ThemeConfig.get_default_theme()
            settings.theme = current_theme
            settings.save()
            logger.info(f"Thème système par défaut configuré: {current_theme}")
        
        # Vérifier si le thème existe, sinon utiliser le défaut
        if not theme_exists(current_theme):
            logger.warning(f"Thème '{current_theme}' invalide, utilisation du thème par défaut")
            current_theme = ThemeConfig.get_default_theme()
            settings.theme = current_theme
            settings.save()
            logger.info(f"Thème corrigé vers: {current_theme}")
        else:
            logger.debug(f"Thème récupéré depuis la base: {current_theme}")
            
        return current_theme
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du thème actuel: {e}")
        fallback_theme = ThemeConfig.get_default_theme()
        logger.info(f"Utilisation du thème de fallback: {fallback_theme}")
        return fallback_theme

def set_current_theme(theme_key):
    """Définit le thème actuel avec sauvegarde sécurisée"""
    try:
        if not theme_key:
            logger.error("Clé de thème vide fournie")
            return False
            
        if not theme_exists(theme_key):
            logger.error(f"Impossible de définir le thème '{theme_key}': thème inexistant")
            return False
            
        # Utiliser init_settings pour assurer l'existence de l'enregistrement
        settings = Settings.init_settings()
        
        # Sauvegarder l'ancien thème pour debug
        old_theme = settings.theme
        
        # Définir le nouveau thème
        settings.theme = theme_key
        settings.save()
        
        logger.info(f"Thème sauvegardé: {old_theme} → {theme_key}")
        return True
            
    except Exception as e:
        logger.error(f"Erreur lors de la définition du thème: {e}")
        import traceback
        logger.debug(f"Trace de l'erreur: {traceback.format_exc()}")
        return False

def get_theme_info(theme_key=None):
    """Obtient les informations complètes d'un thème"""
    if theme_key is None:
        theme_key = get_current_theme()
    
    try:
        return ThemeConfig.get_theme_info(theme_key)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations du thème: {e}")
        return None

# Initialisation du module
logger.info(f"Configuration des thèmes initialisée - {len(ThemeConfig.THEMES)} thèmes disponibles: {list(ThemeConfig.THEMES.keys())}") 