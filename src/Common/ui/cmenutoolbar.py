# !/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: fad

try:
    from ..cstatic import CConstants
except Exception as e:
    print(e)


from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QCursor, QIcon
from PyQt6.QtWidgets import QToolBar, QWidget, QSizePolicy

from .common import FMainWindow


class FMenuToolBar(QToolBar, FMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        QToolBar.__init__(self, parent, *args, **kwargs)

        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        # self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonFollowStyle)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        # self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        # self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.setOrientation(Qt.Orientation.Vertical)

        # self.setIconSize(QSize(135, 35))
        # font = QFont()
        # font.setPointSize(10)
        # font.setBold(True)
        # font.setWeight(35)
        # self.setFont(font)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
