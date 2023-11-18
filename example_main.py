#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

import os
import sys

from cdatabase import AdminDatabase
from cmain import cmain
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from ui.cmenubar import FMenuBar
from ui.cmenutoolbar import FMenuToolBar
from ui.common import FMainWindow, FWidget
from ui.style_qss import theme

app = QApplication(sys.argv)

# AdminDatabase.make_migrate()


class DebtsViewWidget(FWidget):

    """Shows the home page"""

    def __init__(self, parent=0, *args, **kwargs):
        super(DebtsViewWidget, self).__init__(parent=parent, *args, **kwargs)
        self.parent = parent
        self.parentWidget().setWindowTitle(" Gestion des dettes")

        self.title = "Movements"


class MainWindow(FMainWindow):
    def __init__(self):
        FMainWindow.__init__(self)

        self.setWindowIcon(
            QIcon.fromTheme("logo", QIcon("{}".format(CConstants.APP_LOGO)))
        )
        self.menubar = FMenuBar(self)
        self.setMenuBar(self.menubar)
        self.toolbar = FMenuToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

        self.page = DebtsViewWidget

        self.change_context(self.page)

    def page_width(self):
        return self.width() - 100

    def exit(self):
        self.logout()
        self.close()


if __name__ == "__main__":
    print("run !")
    if cmain(test=True):
        sys.exit(app.exec_())
