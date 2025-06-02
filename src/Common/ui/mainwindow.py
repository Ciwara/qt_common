#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow

from ..cstatic import CConstants, logger
from .cmenubar import FMenuBar
from .cmenutoolbar import FMenuToolBar
from .common import FMainWindow, FWidget


class DebtsViewWidget(FWidget):
    """Shows the home page"""

    def __init__(self, parent=0, *args, **kwargs):
        super(DebtsViewWidget, self).__init__(parent=parent, *args, **kwargs)
        self.parent = parent
        self.parentWidget().setWindowTitle(" Gestion des dettes")
        self.title = "Movements"
        logger.debug("Initialisation de DebtsViewWidget")


class MainWindow(FMainWindow):
    def __init__(self):
        logger.info("Initialisation de la fenêtre principale")
        FMainWindow.__init__(self)

        self.menubar = FMenuBar(self)
        self.setMenuBar(self.menubar)
        logger.debug("Barre de menu initialisée")

        self.toolbar = FMenuToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)
        logger.debug("Barre d'outils initialisée")

        self.page = DebtsViewWidget
        self.change_context(self.page)
        logger.debug("Contexte initial changé vers DebtsViewWidget")

    def page_width(self):
        return self.width() - 100

    def exit(self):
        logger.info("Fermeture de l'application")
        self.logout()
        self.close() 