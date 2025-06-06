#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QToolBar

from ..cstatic import CConstants, logger
from .cmenubar import FMenuBar
from .cmenutoolbar import FMenuToolBar
from .common import FMainWindow, FWidget
from .statusbar import GStatusBar
from ..updater import UpdaterInit


class TestViewWidget(FWidget):
    """Shows the home page"""

    def __init__(self, parent=0, *args, **kwargs):
        super(TestViewWidget, self).__init__(parent=parent, *args, **kwargs)
        self.parent = parent
        self.parentWidget().setWindowTitle(" Test")
        self.title = "Movements"
        logger.debug("Initialisation de TestViewWidget")


class CommonMainWindow(FMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        QMainWindow.__init__(self, parent=parent, *args, **kwargs)

        self.setWindowIcon(QIcon(f"{CConstants.APP_LOGO}"))
        self.setWindowTitle(f"{CConstants.APP_NAME} {CConstants.APP_VERSION}")

        self.toolBar = QToolBar()
        self.addToolBar(Qt.LeftToolBarArea, self.toolBar)

        # Pour statusBar
        try:
            self.status_bar = GStatusBar(self)
            self.setStatusBar(self.status_bar)
            # Enregistrer l'instance pour le nettoyage
            try:
                from ..cmain import register_statusbar_instance
                register_statusbar_instance(self.status_bar)
            except ImportError:
                logger.warning("Impossible d'enregistrer la statusbar pour le nettoyage")
        except Exception as exc:
            logger.warning(f"Impossible d'initialiser la barre de statut: {exc}")
            self.status_bar = None

        # Pour l'updater
        try:
            self.updater = UpdaterInit()
            # Enregistrer l'instance pour le nettoyage
            try:
                from ..cmain import register_updater_instance
                register_updater_instance(self.updater)
            except ImportError:
                logger.warning("Impossible d'enregistrer l'updater pour le nettoyage")
        except Exception as exc:
            logger.warning(f"Impossible d'initialiser l'updater: {exc}")
            self.updater = None

        self.menubar = FMenuBar(self)
        self.setMenuBar(self.menubar)
        logger.debug("Barre de menu initialisée")

        self.toolbar = FMenuToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)
        logger.debug("Barre d'outils initialisée")

        self.page = TestViewWidget
        self.change_context(self.page)
        logger.debug("Contexte initial changé vers TestViewWidget")
        
    def closeEvent(self, event):
        """Override closeEvent pour nettoyer les threads avant fermeture"""
        try:
            logger.info("Fermeture de la fenêtre principale - nettoyage des threads")
            
            # Nettoyer manuellement les instances si elles existent
            if hasattr(self, 'status_bar') and self.status_bar:
                if hasattr(self.status_bar, 'cleanup'):
                    self.status_bar.cleanup()
                    
            if hasattr(self, 'updater') and self.updater:
                if hasattr(self.updater, 'cleanup'):
                    self.updater.cleanup()
                    
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage de la fenêtre principale: {e}")
        finally:
            super().closeEvent(event)

    def page_width(self):
        return self.width() - 100

    def exit(self):
        logger.info("Fermeture de l'application")
        self.logout()
        self.close() 