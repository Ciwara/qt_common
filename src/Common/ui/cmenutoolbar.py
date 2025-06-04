# !/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: fad

try:
    from ..cstatic import CConstants
except Exception as e:
    print(e)


from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import QToolBar

from .common import FMainWindow


class FMenuToolBar(QToolBar, FMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        QToolBar.__init__(self, parent, *args, **kwargs)

        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # self.setToolButtonStyle(Qt.ToolButtonFollowStyle)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        # self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        # self.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.setOrientation(Qt.Vertical)

        # self.setIconSize(QSize(135, 35))
        # font = QFont()
        # font.setPointSize(10)
        # font.setBold(True)
        # font.setWeight(35)
        # self.setFont(font)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        # self.setFocusPolicy(Qt.TabFocus)
        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.setAcceptDrops(True)
        # self.setAutoFillBackground(True)
        # self.addSeparator()
        print("toolbar", CConstants.img_cmedia)
        self.addAction(
            QIcon(f"{CConstants.img_cmedia}exit.png"), "Quiter", self.goto_exit
        )

        menu = []

    def goto(self, goto):
        self.change_main_context(goto)

    def goto_exit(self):
        self.parent().exit()
