#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
# ###############################
# #                             #
# #  Coded By: Ibrihima Fadiga  #
# #  Original: 10/12/15         #
# #  File: style CSS PyQt       #
# ###############################

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import platform

from .models import Organization

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))


def load_stylesheet(file_qss):
    """ """
    from PyQt5.QtCore import QFile, QTextStream

    f = QFile("{}.css".format(os.path.join(ROOT_DIR, file_qss)))
    if not f.exists():
        print("Unable to load stylesheet, file not found in " "resources")
        return ""
    else:
        f.open(QFile.ReadOnly | QFile.Text)
        ts = QTextStream(f)
        stylesheet = ts.readAll()
        if platform.system().lower() == "darwin":  # see issue #12 on github
            mac_fix = """
            QDockWidget::title
            {
                background-color: #353434;
                text-align: center;
                height: 12px;
            }
            """
            stylesheet += mac_fix
        return stylesheet


def read_qss_file(file_name):
    styleFile = os.path.join(ROOT_DIR, file_name + ".qss")
    styleSheetStr = open(styleFile, "r").read()
    return styleSheetStr


def dict_style():
    return {
        "Theme systeme": "",
        "Dark": load_stylesheet("dark"),
        "DSVie": load_stylesheet("DSView"),
        "Tangerine": load_stylesheet("tangerine"),
        "Coffee": load_stylesheet("coffee"),
        "F": load_stylesheet("fad"),
        # "DDD KK": read_qss_file("styleD"),
        "Fat": load_stylesheet("fat"),
    }


try:
    theme = dict_style()[(Organization.get(id=1).theme)]
except Exception as e:
    theme = dict_style()["Theme systeme"]
