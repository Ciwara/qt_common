#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from PyQt5.QtWidgets import QTabWidget

from .ui.common import TabPane


def tabbox(*args):
    """adds a box with tab
    params:  (widget, title) title is the string"""
    tab_widget = QTabWidget()
    tab_widget.setMovable(True)
    # tab_widget.setAutoFillBackground(True)
    # tab_widget.setTabShape(QTabWidget.Triangular)
    # tab_widget.setTabPosition(QTabWidget.West)

    for box, btitle in args:
        pane = TabPane()
        pane.addBox(box)
        tab_widget.addTab(pane, btitle)
    return tab_widget
