#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import absolute_import, division, print_function, unicode_literals

import hashlib
import locale
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from time import mktime, strptime
from urllib.request import URLError, urlopen
from uuid import getnode

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QSystemTrayIcon, QTextEdit

from ..cstatic import CConstants, logger
from .window import FWindow

try:
    unicode
except NameError:
    unicode = str


def internet_on():
    try:
        urlopen("https://google.com", timeout=1)
        return True
    except URLError as err:
        logger.debug("URLError {}".format(err))
        return False
    except Exception as exc:
        logger.debug(exc)


def acces_server():
    if not CConstants.SERV:
        logger.debug("Not server mode")
        return False

    if not internet_on():
        return
    try:
        urlopen(get_serv_url(""), timeout=1)
        return True
    except URLError as err:
        return False
    except Exception as e:
        logger.debug(e)


def device_amount(value, dvs=None):
    from Common.models import Settings

    if dvs:
        return "{} {}".format(formatted_number(value), dvs)
    try:
        organ = Settings().get(id=1)
    except Exception as e:
        print(e)
    d = organ.DEVISE[organ.devise]
    v = formatted_number(value)
    if organ.devise == organ.USA:
        return "{d}{v}".format(v=v, d=d)
    else:
        return "{v} {d}".format(v=v, d=d)


def check_is_empty(field):
    stylerreur = ""
    flag = False
    containt = ""
    # if isinstance(field, )
    field.setToolTip("")
    if isinstance(field, QTextEdit):
        containt = field.toPlainText()
    else:
        containt = field.text()

    if len(containt) == 0:
        field.setToolTip("Champs requis")
        stylerreur = "background-color: #fff79a; border : 2px solid red"
        flag = True
    field.setStyleSheet(stylerreur)
    return flag


def field_error(field, msg):
    field.setStyleSheet("background-color: #DF8F1F; border : 2px solid red")
    field.setToolTip("{}".format(msg))
    return False


def check_field(field, msg, condition):
    return is_valide_codition_field(field, msg, condition)


def is_valide_codition_field(field, msg, condition):
    stylerreur = ""
    flag = False
    field.setToolTip("")
    if condition:
        field.setToolTip(msg)
        stylerreur = "background-color: #fff79a;"
        flag = True
    field.setStyleSheet(stylerreur)
    return flag


def uopen_prefix(platform=sys.platform):
    if platform in ("win32", "win64"):
        return "cmd /c start"

    if "darwin" in platform:
        return "open"

    if (
        platform in ("cygwin", "linux")
        or platform.startswith("linux")
        or platform.startswith("sun")
        or "bsd" in platform
    ):
        return "xdg-open"

    return "xdg-open"


def openFile(file):
    if sys.platform == "linux2":
        subprocess.call(["xdg-open", file])
    else:
        os.startfile(file)


def uopen_file(filename):
    # print(filename)
    if not os.path.exists(filename):
        raise IOError("Fichier %s non valable." % filename)
    subprocess.call(
        "%(cmd)s %(file)s" % {"cmd": uopen_prefix(), "file": filename}, shell=True
    )


def get_temp_filename(extension=None):
    f = tempfile.NamedTemporaryFile(delete=False)
    if extension:
        fname = "%s.%s" % (f.name, extension)
    else:
        fname = f.name
    return fname


def raise_error(title, message):
    box = QMessageBox(
        QMessageBox.Critical,
        title,
        message,
        QMessageBox.Ok,
        parent=FWindow.window,
    )
    box.setWindowOpacity(0.9)

    box.exec_()


def raise_success(title, message):
    box = QMessageBox(
        QMessageBox.Information,
        title,
        message,
        QMessageBox.Ok,
        parent=FWindow.window,
    )
    box.setWindowOpacity(0.9)
    box.exec_()


def formatted_number(number, sep=".", aftergam=None):
    """ """

    from Common.models import Settings

    if not aftergam:
        aftergam = int(Settings.select().get().after_cam)
    locale_name, encoding = locale.getlocale()
    # locale.setlocale(locale.LC_ALL, "fra")
    fmt = "%s"
    if isinstance(number, int):
        # print("int ", number)
        fmt = "%d"
    elif isinstance(number, float):
        # print("float, ", number)
        fmt = "%.{}f".format(aftergam)

    try:
        return locale.format(fmt, number, grouping=True).decode(encoding)
    except AttributeError:
        return locale.format(fmt, number, grouping=True)
    except Exception as e:
        logger.debug("formatted_number : ", e)
        return "%s" % number


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, mss, parent=None):
        QSystemTrayIcon.__init__(self, parent)

        self.setIcon(QIcon.fromTheme("document-save"))

        self.activated.connect(self.click_trap)
        # self.mss = ("Confirmation", "Mali rapou!!!!")
        self.show(mss)

    def click_trap(self, value):
        # left click!
        if value == self.Trigger:
            self.left_menu.exec_(QCursor.pos())

    def welcome(self):
        self.showMessage(self.mss[0], self.mss[1])

    def show(self, mss):
        self.mss = mss
        QSystemTrayIcon.show(self)
        QTimer.singleShot(1000, self.welcome)


def is_float(val):
    try:
        val = val.replace(",", ".").replace(" ", "").replace("\xa0", "")
        return float(val)
    except Exception as e:
        # print("is_float", e)
        logger.debug("is_float ", e)
        return 0


def is_int(val):
    try:
        val = str(val).split()
        v = ""
        for i in val:
            v += i
        return int(v)
    except Exception as e:
        # print("is_int", e)
        logger.debug("is_int ", e)
        return 0


def date_to_str(date):
    if not date:
        return None
    if isinstance(date, str):
        d, m, y = date.split("/")
        if len(y) == 4:
            return "{}-{}-{}".format(y, m, d)
        else:
            return date.replace("/", "-")
    return date.strftime("%Y-%m-%d")


def alerte():
    pass


def format_date(dat):
    dat = str(dat)
    day, month, year = dat.split("/")
    return "-".join([year, month, day])


def datetime_to_str(date):
    return mktime(strptime(date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))


def to_jstimestamp(adate):
    if not adate:
        return int(to_timestamp(adate)) * 1000


def to_timestamp(dt):
    """
    Return a timestamp for the given datetime object.
    """
    if not dt:
        return (dt - datetime(1970, 1, 1)).total_seconds()


def copy_file(dest, path_filename):
    """Copy the file, rename file in banc and return new name of the doc
    created folder banc doc if not existe
    """
    import shutil

    dest = os.path.join(os.path.dirname(os.path.abspath("__file__")), dest)
    filename = os.path.basename(path_filename)
    if not os.path.exists(dest):
        os.makedirs(dest)
    shutil.copyfile(path_filename, get_path(dest, filename))

    return rename_file(dest, filename, slug_mane_file(filename))


def rename_file(path, old_filename, new_filename):
    """Rename file in banc docs  params: old_filename, new_filename
    return newname"""
    os.rename(get_path(path, old_filename), get_path(path, new_filename))
    return new_filename


def get_path(path, filename):
    return os.path.join(path, filename)


def get_serv_url(sub_url):
    from Common.models import Settings

    return "{}/{}".format(Settings.get(id=1).url, sub_url)


def slug_mane_file(file_name):
    return "{timestamp}_{fname}".format(
        fname=file_name.replace(" ", "_"), timestamp=to_jstimestamp(datetime.now())
    )


def normalize(s):
    if type(s) == unicode:
        return s.encode("utf8", "ignore")
    else:
        return str(s)


def str_date_split(date):
    try:
        return date.split("/")
    except AttributeError:
        return date.day, date.month, date.year


def date_on_or_end(dat, on=True):
    day, month, year = str_date_split(dat)
    if on:
        hour, second, micro_second = 0, 0, 0
    else:
        hour, second, micro_second = 23, 59, 59
    return datetime(
        int(year), int(month), int(day), int(hour), int(second), int(micro_second)
    )


def show_date(dat, time=True):
    if isinstance(dat, str):
        dat = date_to_datetime(dat)
    if not dat:
        return "pas de date"
    return dat.strftime("%Y-%m-%d à %Hh:%Mmn") if time else dat.strftime("%Y-%m-%d")


def date_to_datetime(dat):
    "reçoit une date return une datetime"
    day, month, year = str_date_split(dat)
    dt = datetime.now()
    return datetime(
        int(year),
        int(month),
        int(day),
        int(dt.hour),
        int(dt.minute),
        int(dt.second),
        int(dt.microsecond),
    )


def getlog(text):
    return "Log-{}".format(text)


def is_valide_mac():
    """check de license"""
    from Common.models import License

    try:
        lcse = License.get(License.code == str(make_lcse()))
        return lcse, lcse.can_use()
    except Exception as e:
        logger.debug("/!\ invalide license.")
        return None, CConstants.IS_EXPIRED


def clean_mac():
    return getnode()


def make_lcse(lcse=clean_mac()):
    # print("lcse:", lcse)
    lcse = hashlib.md5(str(lcse).encode("utf-8")).hexdigest()
    return lcse


def get_lcse_of_file():
    return open("{}".format(get_lcse_file()), "r").read()


def get_lcse_file():
    return os.path.join(os.path.dirname(os.path.abspath("__file__")), "LICENCE")


def _disk_c(self):
    drive = unicode(os.getenv("SystemDrive"))
    freeuser = ctypes.c_int64()
    total = ctypes.c_int64()
    free = ctypes.c_int64()
    ctypes.windll.kernel32.GetDiskFreeSpaceExW(
        drive, ctypes.byref(freeuser), ctypes.byref(total), ctypes.byref(free)
    )
    return freeuser.value
