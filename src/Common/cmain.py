#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

from __future__ import absolute_import, division, print_function, unicode_literals

import gettext
import locale

import gettext_windows
from PyQt5.QtWidgets import QDialog
from ui.mainwindow import MainWindow

from .cstatic import CConstants
from .models import Organization, Owner, Settings
from .ui.license_view import LicenseViewWidget
from .ui.login import LoginWidget
from .ui.organization_add_or_edit import NewOrEditOrganizationViewWidget
from .ui.restoration_view import RestorationViewWidget
from .ui.style_qss import theme
from .ui.user_add_or_edit import NewOrEditUserViewWidget
from .ui.util import is_valide_mac
from .ui.window import FWindow

try:
    from ui.mainwindow import MainWindow
except Exception as exc:
    print("import MainWindow", exc)
    # from .ui.common import FMainWindow as MainWindow


def cmain(test=False):
    gettext_windows.setup_env()
    locale.setlocale(locale.LC_ALL, "")
    gettext.install("main.py", localedir="locale")
    window = MainWindow()
    window.setStyleSheet(theme)
    setattr(FWindow, "window", window)

    if CConstants.DEBUG or test:
        window.showMaximized()
        print("Debug is True")
        return True

    if Owner().select().where(Owner.isactive == True).count() == 0:
        if not RestorationViewWidget().exec_() == QDialog.Accepted:
            return
        if not NewOrEditUserViewWidget().exec_() == QDialog.Accepted:
            return
    if Organization().select().count() == 0:
        if not NewOrEditOrganizationViewWidget().exec_() == QDialog.Accepted:
            return
    if not is_valide_mac()[1] == CConstants.OK:
        if not LicenseViewWidget(parent=None).exec_() == QDialog.Accepted:
            return
    if not Settings().get(id=1).is_login or LoginWidget().exec_() == QDialog.Accepted:
        window.showMaximized()
        return True
    return False
