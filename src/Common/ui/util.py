#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad


import ctypes
import hashlib
import locale
import os
import subprocess
import sys
from pathlib import Path
import tempfile
from datetime import datetime
from time import mktime, strptime
from urllib.request import URLError, urlopen
from uuid import getnode

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QCursor, QIcon
from PyQt6.QtWidgets import QMessageBox, QSystemTrayIcon, QTextEdit

from ..cstatic import CConstants, license_required, logger
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
        logger.debug(f"URLError {err}")
        return False
    except Exception as exc:
        logger.debug(exc)


def access_server():
    if not CConstants.SERV:
        logger.info("Not server mode")
        return False

    if not internet_on():
        return
    try:
        urlopen(get_server_url(""), timeout=1)
        return True
    except URLError as err:
        return False
    except Exception as e:
        logger.debug(e)


def device_amount(value, dvs=None):
    from Common.models import Settings

    if dvs:
        return f"{formatted_number(value)} {dvs}"
    try:
        organ = Settings().get(id=1)
    except Exception as e:
        print(e)
    d = organ.DEVISE[organ.devise]
    v = formatted_number(value)
    if organ.devise == organ.USA:
        return f"{d}{v}"
    else:
        return f"{v} {d}"


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
    """
    Ouvre un fichier avec l’application par défaut du système.
    Windows : ``os.startfile`` ; macOS : ``open`` ; Linux/BSD : ``xdg-open``.
    """
    path = os.path.abspath(os.path.normpath(str(file)))
    if not os.path.isfile(path):
        logger.warning("openFile: fichier introuvable: %s", path)
        return 1
    try:
        if sys.platform == "win32":
            os.startfile(path)  # noqa: S606
            return 0
        if sys.platform == "darwin":
            return subprocess.run(["open", path], check=False).returncode
        return subprocess.run(["xdg-open", path], check=False).returncode
    except OSError as e:
        logger.warning("openFile: impossible d'ouvrir %s: %s", path, e)
        return 1


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
        QMessageBox.Icon.Critical,
        title,
        message,
        QMessageBox.StandardButton.Ok,
        parent=FWindow.window,
    )
    box.setWindowOpacity(0.9)

    box.exec()


def raise_success(title, message):
    box = QMessageBox(
        QMessageBox.Icon.Information,
        title,
        message,
        QMessageBox.StandardButton.Ok,
        parent=FWindow.window,
    )
    box.setWindowOpacity(0.9)
    box.exec()


def formatted_number(number, sep=" ", aftergam=None):
    """Format a number with a stable thousands separator.

    Locale grouping is not reliable on every desktop install; use Python's
    grouping and replace the separator so tables always show readable amounts.
    """

    if isinstance(number, bool):
        return str(number)

    if aftergam is None:
        try:
            from Common.models import Settings

            aftergam = int(Settings.select().get().after_cam)
        except Exception:
            aftergam = 0
    else:
        aftergam = int(aftergam)
    if aftergam < 0:
        aftergam = 0

    try:
        if isinstance(number, int):
            return f"{number:,}".replace(",", sep)
        if isinstance(number, float):
            return f"{number:,.{aftergam}f}".replace(",", sep)
    except Exception as e:
        logger.debug("formatted_number : %s", e)
    return str(number)


def format_number_table_no_round(number):
    """Affichage tableau : pas d’arrondi imposé, uniquement suppression des zéros de fin.

    Utilise la représentation décimale de la valeur (Decimal(str(...)) pour les float)
    puis formate avec la locale (groupement), sans tronquer à N décimales fixes.
    """
    import math
    from decimal import Decimal, InvalidOperation

    try:
        if isinstance(number, int):
            return formatted_number(number)
        if isinstance(number, float):
            if math.isnan(number) or math.isinf(number):
                return str(number)
            d = Decimal(str(number))
        elif isinstance(number, Decimal):
            d = number
        else:
            d = Decimal(str(number))
    except (InvalidOperation, ValueError, TypeError):
        return str(number)

    s = format(d, "f")
    neg = s.startswith("-")
    if neg:
        s = s[1:]

    if "." in s:
        int_part, frac_part = s.split(".", 1)
        frac_part = frac_part.rstrip("0")
        ndigits = len(frac_part) if frac_part else 0
    else:
        int_part = s
        ndigits = 0

    int_val = int(int_part)
    if neg:
        int_val = -int_val

    try:
        if ndigits == 0:
            return formatted_number(int_val)
        conv = locale.localeconv()
        dec_sym = conv.get("decimal_point") or "."
        left = locale.format_string("%d", int_val, grouping=True)
        return f"{left}{dec_sym}{frac_part}"
    except Exception as e:
        logger.debug("format_number_table_no_round : %s", e)
        return str(d)


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
            self.left_menu.exec(QCursor.pos())

    def welcome(self):
        self.showMessage(self.mss[0], self.mss[1])

    def show(self, mss):
        self.mss = mss
        QSystemTrayIcon.show(self)
        QTimer.singleShot(1000, self.welcome)


def is_float(val):
    try:
        # Normalize the string by removing spaces and non-breaking spaces
        val = val.replace(" ", "").replace("\xa0", "")

        # Handle comma as decimal separator, ensuring only the last occurrence is replaced
        if "," in val and "." in val:
            val = val.replace(".", "").replace(",", ".")
        else:
            val = val.replace(",", ".")

        # Convert to float to check validity
        float(val)
        return True
    except ValueError as e:
        logger.debug("is_float error: %s", e)
        return False


def is_int(val):
    val = str(val).split()
    v = ""
    for i in val:
        v += i
    try:
        v = int(v)
    except ValueError:
        v = v.replace(",", "")
    return int(v)


def parse_integer(value):
    # Remove spaces and commas from the input string
    cleaned_value = value.replace(" ", "").replace(",", "")

    try:
        # Attempt to convert the cleaned value to an integer
        result = int(cleaned_value)
    except ValueError:
        # Handle the case where conversion to int fails
        result = None  # or raise an exception or provide a default value

    return result


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


def get_server_url(sub_url):
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
    """Retourne (enregistrement License ou None, statut can_use / constante CConstants)."""
    from Common.models import License

    if not license_required():
        return None, CConstants.OK

    code = str(make_lcse())
    try:
        lcse = License.get(License.code == code)
        return lcse, lcse.can_use()
    except License.DoesNotExist:
        logger.debug("Aucune licence en base pour cette machine (code=%s…)", code[:8])
        return None, CConstants.IS_EXPIRED
    except Exception:
        logger.exception("Erreur lors de la vérification de la licence")
        return None, CConstants.IS_EXPIRED


_STABLE_NODE_BASENAME = ".common_device_node"


def _stable_machine_node():
    """Persiste `uuid.getnode()` une fois (Wi‑Fi / VPN peuvent le faire varier)."""
    base = Path(_license_base_dir())
    path = base / _STABLE_NODE_BASENAME
    try:
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace").strip()
            if text:
                return int(text)
    except (ValueError, OSError):
        logger.debug("Lecture .common_device_node impossible", exc_info=True)
    n = int(getnode())
    try:
        base.mkdir(parents=True, exist_ok=True)
        path.write_text(str(n), encoding="utf-8")
    except OSError as e:
        logger.warning("Impossible d'enregistrer l'identifiant machine (%s): %s", path, e)
    return n


def clean_mac():
    """Identifiant matériel stabilisé (fichier à côté de la base / LICENCE)."""
    return _stable_machine_node()


def make_lcse(lcse=None):
    """MD5 hex utilisé comme `License.code`. Priorité au fichier LICENCE après activation."""
    if lcse is not None:
        return hashlib.md5(str(lcse).encode("utf-8")).hexdigest()
    try:
        p = Path(get_lcse_file())
        if p.is_file():
            txt = p.read_text(encoding="utf-8", errors="replace").strip()
            if len(txt) == 32:
                low = txt.lower()
                if all(c in "0123456789abcdef" for c in low):
                    return low
    except OSError:
        pass
    raw = _stable_machine_node()
    logger.debug("Identifiant machine stabilisé (getnode persisté): %s", raw)
    return hashlib.md5(str(raw).encode("utf-8")).hexdigest()


def get_lcse_of_file():
    """Lit le contenu du fichier LICENCE (UTF-8). Lève FileNotFoundError si absent."""
    path = get_lcse_file()
    return Path(path).read_text(encoding="utf-8", errors="replace").strip()


def _license_base_dir():
    """Répertoire du fichier LICENCE : stable et en général le même que la base SQLite."""
    override = (os.environ.get("COMMON_LICENSE_DIR") or "").strip()
    if override:
        return override
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    try:
        from Common.models import dbh

        if dbh is not None:
            raw = getattr(dbh, "database", None)
            if raw:
                p = Path(str(raw))
                if not p.is_absolute():
                    p = (Path.cwd() / p).resolve()
                return str(p.parent)
    except Exception:
        logger.debug("Impossible de déduire le répertoire licence depuis la DB", exc_info=True)
    main = sys.argv[0] if sys.argv else ""
    if main and os.path.isfile(main):
        return str(Path(main).resolve().parent)
    return os.getcwd()


def get_lcse_file():
    """Chemin du fichier LICENCE : à côté de la base ou du binaire, pas le CWD arbitraire."""
    return os.path.join(_license_base_dir(), "LICENCE")


def _disk_c(self):
    drive = str(os.getenv("SystemDrive"))
    freeuser = ctypes.c_int64()
    total = ctypes.c_int64()
    free = ctypes.c_int64()
    ctypes.windll.kernel32.GetDiskFreeSpaceExW(
        drive, ctypes.byref(freeuser), ctypes.byref(total), ctypes.byref(free)
    )
    return freeuser.value
