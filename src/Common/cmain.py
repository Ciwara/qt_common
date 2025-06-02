#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

import gettext
import locale

import gettext_windows
from PyQt5.QtWidgets import QDialog

from .cstatic import CConstants, logger
from .models import Organization, Owner, Settings
from .ui.mainwindow import MainWindow
from .ui.license_view import LicenseViewWidget
from .ui.login import LoginWidget
from .ui.organization_add_or_edit import NewOrEditOrganizationViewWidget
from .ui.restoration_view import RestorationViewWidget
from .ui.style_qss import theme
from .ui.user_add_or_edit import NewOrEditUserViewWidget
from .ui.util import is_valide_mac
from .ui.window import FWindow


def setup_localization():
    logger.info("Configuration de la localisation")
    gettext_windows.setup_env()
    locale.setlocale(locale.LC_ALL, "")
    gettext.install("main.py", localedir="locale")
    logger.debug("Localisation configurée avec succès")


def initialize_main_window():
    logger.info("Initialisation de la fenêtre principale")
    window = MainWindow()
    # window.setStyleSheet(theme)
    setattr(FWindow, "window", window)
    logger.debug("Fenêtre principale initialisée")
    return window


def handle_initial_conditions(window):
    logger.info("Vérification des conditions initiales")
    
    if Owner().select().where(Owner.isactive == True).count() == 0:
        logger.debug("Aucun propriétaire actif trouvé, affichage de la vue de restauration")
        if RestorationViewWidget().exec_() != QDialog.Accepted:
            logger.warning("Restauration annulée par l'utilisateur")
            return False
        if NewOrEditUserViewWidget().exec_() != QDialog.Accepted:
            logger.warning("Création d'utilisateur annulée par l'utilisateur")
            return False

    if Organization().select().count() == 0:
        logger.debug("Aucune organisation trouvée, affichage de la vue de création d'organisation")
        if NewOrEditOrganizationViewWidget().exec_() != QDialog.Accepted:
            logger.warning("Création d'organisation annulée par l'utilisateur")
            return False

    if is_valide_mac()[1] != CConstants.OK:
        logger.debug("Vérification de la licence")
        if LicenseViewWidget(parent=None).exec_() != QDialog.Accepted:
            logger.warning("Activation de la licence annulée par l'utilisateur")
            return False

    settings = Settings().get(id=1)
    if not settings.is_login or LoginWidget().exec_() != QDialog.Accepted:
        logger.info("Affichage de la fenêtre principale maximisée")
        window.showMaximized()
        return True

    return False


def cmain(test=False):
    logger.info("Démarrage de l'application")
    setup_localization()
    window = initialize_main_window()

    if CConstants.DEBUG or test:
        logger.info("Mode debug activé")
        window.showMaximized()
        print("Debug is True")
        return True

    if handle_initial_conditions(window):
        logger.info("Application démarrée avec succès")
        return True

    logger.warning("L'application n'a pas pu démarrer correctement")
    return False
