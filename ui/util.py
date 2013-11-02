#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

import os
import sys
import locale
import tempfile
import subprocess
import datetime

from PyQt4 import QtGui, QtCore
from window import F_Window


class PDFFileUnavailable(IOError):
    pass


def uopen_prefix(platform=sys.platform):

    if platform in ('win32', 'win64'):
        return 'cmd /c start'

    if 'darwin' in platform:
        return 'open'

    if platform in ('cygwin', 'linux') or \
       platform.startswith('linux') or \
       platform.startswith('sun') or \
       'bsd' in platform:
        return 'xdg-open'

    return 'xdg-open'


def uopen_file(filename):
    if not os.path.exists(filename):
        raise IOError(u"Fichier %s non valable." % filename)
    subprocess.call('%(cmd)s %(file)s' % {'cmd': uopen_prefix(), 'file': filename}, shell=True)


def get_temp_filename(extension=None):
    f = tempfile.NamedTemporaryFile(delete=False)
    if extension:
        fname = '%s.%s' % (f.name, extension)
    else:
        fname = f.name
    return fname


def raise_error(title, message):
    box = QtGui.QMessageBox(QtGui.QMessageBox.Critical, title,
                            message, QtGui.QMessageBox.Ok,
                            parent=F_Window.window)
    box.setWindowOpacity(0.9)
    box.exec_()


def raise_success(title, message):
    box = QtGui.QMessageBox(QtGui.QMessageBox.Information, title,
                            message, QtGui.QMessageBox.Ok,
                            parent=F_Window.window)
    box.setWindowOpacity(0.9)
    box.exec_()


def formatted_number(number):
    """ """

    try:
        return locale.format("%d", number, grouping=True).decode(locale.getlocale()[1])
    except:
        return "%s" % number


class SystemTrayIcon(QtGui.QSystemTrayIcon):

    def __init__(self, mss, parent=None):

        QtGui.QSystemTrayIcon.__init__(self, parent)

        self.setIcon(QtGui.QIcon.fromTheme("document-save"))

        self.activated.connect(self.click_trap)
        # self.mss = ("Confirmation", "Mali rapou!!!!")
        self.show(mss)

    def click_trap(self, value):
        #left click!
        if value == self.Trigger:
            self.left_menu.exec_(QtGui.QCursor.pos())

    def welcome(self):
        self.showMessage(self.mss[0], self.mss[1])

    def show(self, mss):
        self.mss = mss
        QtGui.QSystemTrayIcon.show(self)
        QtCore.QTimer.singleShot(1000, self.welcome)


def is_int(val):

    try:
        val = unicode(val).split()
        v = ''
        for i in val:
            v += i
        return int(v)
    except:
        return 0


def date_datetime(dat):
    "reçoit une date return une datetime"
    dat = str(unicode(dat))
    day, month, year = dat.split('/')
    dt = datetime.datetime.now()
    return datetime.datetime(int(year), int(month), int(day),
                             int(dt.hour), int(dt.minute),
                             int(dt.second), int(dt.microsecond))


def alerte():
    pass


def date_end(dat):
    dat = str(unicode(dat))
    day, month, year = dat.split('/')
    return datetime.datetime(int(year), int(month), int(day), 23, 59, 59)


def date_on(dat):
    dat = str(unicode(dat))
    day, month, year = dat.split('/')
    return datetime.datetime(int(year), int(month), int(day), 0, 0, 0)


def date_start_end(date, st):
    day, month, year = str(unicode(date)).split('/')
    # return datetime(int(year), int(month), int(day), if st 0 else 23,
    #                                            if st: 0 else 59, if st: 0 59)


def format_date(dat):
    dat = str(dat)
    day, month, year = dat.split('/')
    return '-'.join([year, month, day])


def show_date(dat):
    return dat.strftime(u"%A le %d %b %Y a %Hh:%Mmn")
