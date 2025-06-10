#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration centralisée et nettoyée des thèmes
Version 2.0 - Système unifié et optimisé
"""

from ...cstatic import logger
from ...models import Settings

# ===== CONFIGURATION CENTRALISÉE DES THÈMES =====

class ThemeConfig:
    """Configuration centralisée de tous les thèmes de l'application"""
    
    # Définition complète de tous les thèmes disponibles
    THEMES = {
        "default": {
            "name": "Défaut", 
            "description": "Thème par défaut simple et compatible",
            "is_dark": False,
            "category": "Basique",
            "author": "System",
            "version": "1.0"
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
        },
        "blue_professional": {
            "name": "Professionnel Bleu",
            "description": "Thème professionnel avec des accents bleus",
            "is_dark": False,
            "category": "Professionnel",
            "author": "Qt Common",
            "version": "1.5"
        },
        "green_nature": {
            "name": "Nature Verte",
            "description": "Thème inspiré de la nature avec des tons verts",
            "is_dark": False,
            "category": "Coloré",
            "author": "Qt Common",
            "version": "1.5"
        }
    }
    
    # Thème par défaut
    DEFAULT_THEME = "default"
    
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
        return theme_info.get("is_dark", False) if theme_info else False
    
    @classmethod
    def theme_exists(cls, theme_key):
        """Vérifie si un thème existe"""
        return theme_key in cls.THEMES
    
    @classmethod
    def get_default_theme(cls):
        """Retourne la clé du thème par défaut"""
        return cls.DEFAULT_THEME
    
    @classmethod
    def get_themes_by_category(cls, category=None):
        """Retourne les thèmes par catégorie"""
        if category:
            return {
                key: config for key, config in cls.THEMES.items() 
                if config.get("category") == category
            }
        
        # Grouper par catégorie
        categories = {}
        for key, config in cls.THEMES.items():
            cat = config.get("category", "Autre")
            if cat not in categories:
                categories[cat] = {}
            categories[cat][key] = config
        return categories
    
    @classmethod
    def get_light_themes(cls):
        """Retourne tous les thèmes clairs"""
        return {
            key: config["name"] for key, config in cls.THEMES.items() 
            if not config.get("is_dark", False)
        }
    
    @classmethod
    def get_dark_themes(cls):
        """Retourne tous les thèmes sombres"""
        return {
            key: config["name"] for key, config in cls.THEMES.items() 
            if config.get("is_dark", False)
        }

# ===== FONCTIONS PUBLIQUES SIMPLIFIÉES =====

def get_available_themes():
    """Fonction principale pour obtenir tous les thèmes disponibles"""
    try:
        return ThemeConfig.get_all_themes()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des thèmes: {e}")
        return {"default": "Défaut"}

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
        
        # Vérifier si le thème existe, sinon utiliser le défaut
        if not current_theme or not theme_exists(current_theme):
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
logger.info(f"Configuration des thèmes v2.0 initialisée - {len(ThemeConfig.THEMES)} thèmes disponibles")
logger.debug(f"Thèmes disponibles: {list(ThemeConfig.THEMES.keys())}") 