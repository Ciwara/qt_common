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
from .ui.license_view import LicenseViewWidget
from .ui.login import LoginWidget
from .ui.organization_add_or_edit import NewOrEditOrganizationViewWidget
from .ui.restoration_view import RestorationViewWidget
from .ui.style_qss import theme
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
        window.setStyleSheet(theme)
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
    window.setStyleSheet(theme)
    setattr(FWindow, "window", window)
    logger.debug("Fenêtre principale Common initialisée")
    return window

def handle_initial_conditions(window):
    logger.info("Vérification des conditions initiales")
    
    try:
        # Initialisation des paramètres
        settings = Settings.init_settings()
        logger.debug("Paramètres initialisés avec succès")

        # Vérification des propriétaires actifs
        if Owner.select().where(Owner.isactive == True).count() == 0:
            logger.debug("Aucun propriétaire actif trouvé, affichage de la vue de restauration")
            if RestorationViewWidget().exec_() != QDialog.Accepted:
                logger.warning("Restauration annulée par l'utilisateur")
                return False
            if NewOrEditUserViewWidget().exec_() != QDialog.Accepted:
                logger.warning("Création d'utilisateur annulée par l'utilisateur")
                return False

        # Vérification des organisations
        if Organization.select().count() == 0:
            logger.debug("Aucune organisation trouvée, affichage de la vue de création d'organisation")
            if NewOrEditOrganizationViewWidget().exec_() != QDialog.Accepted:
                logger.warning("Création d'organisation annulée par l'utilisateur")
                return False

        # Vérification de la licence
        if is_valide_mac()[1] != CConstants.OK:
            logger.debug("Vérification de la licence")
            if LicenseViewWidget(parent=None).exec_() != QDialog.Accepted:
                logger.warning("Activation de la licence annulée par l'utilisateur")
                return False

        # Vérification de la connexion
        if not settings.is_login or LoginWidget().exec_() != QDialog.Accepted:
            logger.info("Affichage de la fenêtre principale maximisée")
            window.showMaximized()
            return True

        return False

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
        try:
            # Essayer d'abord la fenêtre principale externe
            window = initialize_main_window()
            logger.info("Fenêtre principale externe utilisée")
        except Exception as e:
            logger.warning(f"Impossible d'utiliser la fenêtre principale externe: {e}")
            try:
                # Utiliser la fenêtre commune du module Common
                window = initialize_common_main_window()
                logger.info("Fenêtre principale Common utilisée")
            except Exception as e2:
                logger.error(f"Impossible d'initialiser aucune fenêtre: {e2}")
                return False

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
