#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

import gettext
import locale
import sys
import atexit

import gettext_windows
from PyQt5.QtWidgets import QDialog, QApplication

from .cstatic import CConstants, logger
from .models import Organization, Owner, Settings, init_database, dbh
from .ui.theme_manager import get_theme_manager
from .ui.license_view import LicenseViewWidget
from .ui.login import LoginWidget
from .ui.organization_add_or_edit import NewOrEditOrganizationViewWidget
from .ui.restoration_view import RestorationViewWidget

from .ui.user_add_or_edit import NewOrEditUserViewWidget
from .ui.util import is_valide_mac
from .ui.window import FWindow

def cleanup():
    """Fonction de nettoyage appelée à la fermeture de l'application"""
    try:
        logger.info("Fermeture de la base de données")
        if dbh is not None and not dbh.is_closed():
            dbh.close()
    except Exception as e:
        logger.error(f"Erreur lors de la fermeture de la base de données: {e}")

# Enregistrement de la fonction de nettoyage
atexit.register(cleanup)

def setup_localization():
    logger.info("Configuration de la localisation")
    gettext_windows.setup_env()
    locale.setlocale(locale.LC_ALL, "")
    gettext.install("main.py", localedir="locale")
    logger.debug("Localisation configurée avec succès")

def initialize_main_window():   
    """Tentative d'initialisation de la fenêtre principale (externe)"""
    try:
        from ui.mainwindow import MainWindow
        logger.info("Initialisation de la fenêtre principale externe")
        window = MainWindow()
        apply_global_theme()
        setattr(FWindow, "window", window)
        logger.debug("Fenêtre principale externe initialisée")
        return window
    except ImportError as e:
        logger.warning(f"Module ui.mainwindow non trouvé: {e}")
        raise e

def initialize_common_main_window():
    """Initialisation de la fenêtre principale du module Common"""
    from .ui.commun_mainwindow import CommonMainWindow
    logger.info("Initialisation de la fenêtre principale du module Common")
    window = CommonMainWindow()
    apply_global_theme()
    setattr(FWindow, "window", window)
    logger.debug("Fenêtre principale Common initialisée")
    return window

def apply_global_theme():
    """Applique le thème à toute l'application"""
    try:
        # Utiliser le nouveau système de thèmes centralisé
        theme_manager = get_theme_manager()
        theme_manager.apply_theme("light_modern")
        logger.info("Thème appliqué globalement à toute l'application")
    except ImportError:
        # Fallback vers l'ancien système
        logger.debug("theme_manager non disponible, utilisation du fallback")
        fallback_theme_application()
    except Exception as e:
        logger.warning(f"Erreur lors de l'application du thème global: {e}")
        fallback_theme_application()

def fallback_theme_application():
    """Application de fallback du thème en cas d'erreur"""
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            # app.setStyleSheet(theme)
            logger.info("Thème appliqué via fallback à toute l'application")
    except Exception as e:
        logger.error(f"Erreur lors de l'application du thème fallback: {e}")

def handle_initial_conditions(window):
    logger.info("Vérification des conditions initiales")
    
    try:
        # Initialisation des paramètres
        settings = Settings.init_settings()
        logger.debug("Paramètres initialisés avec succès")

        # Vérification des propriétaires actifs
        active_owners = Owner.select().where(Owner.isactive, Owner.group != Owner.SUPERUSER)
        if not active_owners.exists():
            logger.debug("Aucun propriétaire actif du groupe Administrateur trouvé")
            if RestorationViewWidget().exec_() != QDialog.Accepted:
                logger.warning("Restauration annulée par l'utilisateur")
                return False
            if NewOrEditUserViewWidget().exec_() != QDialog.Accepted:
                logger.warning("Création d'utilisateur annulée par l'utilisateur")
                return False

        # Vérification des organisations
        if not Organization.select().exists():
            logger.debug("Aucune organisation trouvée")
            if NewOrEditOrganizationViewWidget().exec_() != QDialog.Accepted:
                logger.warning("Création d'organisation annulée par l'utilisateur")
                return False

        # Vérification de la licence
        license_status = is_valide_mac()[1]
        if license_status != CConstants.OK:
            logger.debug(f"Vérification de la licence - Statut: {license_status}")
            if LicenseViewWidget(parent=None).exec_() != QDialog.Accepted:
                logger.warning("Activation de la licence annulée par l'utilisateur")
                return False

        # Vérification de la connexion
        if settings.auth_required:
            logger.debug("Authentification requise")
            if LoginWidget().exec_() != QDialog.Accepted:
                logger.warning("Connexion annulée ou échouée")
                return False
            logger.info("Authentification réussie")
        else:
            logger.debug("Aucune authentification requise")
        
        logger.info("Toutes les conditions initiales sont satisfaites")
        window.showMaximized()
        return True

    except Exception as e:
        logger.error(f"Erreur lors de la vérification des conditions initiales: {e}")
        return False

def cmain(test=False):
    logger.info("Démarrage de l'application")
    
    try:
        # Initialisation de l'application Qt
        app = QApplication(sys.argv)
        
        # Initialisation de la base de données
        if not init_database():
            logger.error("Impossible d'initialiser la base de données")
            return False
            
        # Vérification de la connexion à la base de données
        if dbh is None:
            logger.error("La base de données n'est pas initialisée")
            return False
            
        if dbh.is_closed():
            logger.info("Connexion à la base de données")
            dbh.connect()
        
        setup_localization()
        
        # Tentative d'initialisation de la fenêtre principale
        window = None

        if test:
            window = initialize_common_main_window()
            logger.info("Fenêtre principale Common utilisée")
        else:
            window = initialize_main_window()
            logger.info("Fenêtre principale externe utilisée")

        if window is None:
            logger.error("Aucune fenêtre n'a pu être initialisée")
            return False

        if CConstants.DEBUG or test:
            logger.info("Mode debug activé")
            window.showMaximized()
            print("Debug is True")
            return app.exec_()

        if handle_initial_conditions(window):
            logger.info("Application démarrée avec succès")
            return app.exec_()

        logger.warning("L'application n'a pas pu démarrer correctement")
        return False

    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'application: {e}")
        return False
