#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad


import ctypes
import hashlib
import json
import locale
import os
import platform
import subprocess
import sys
from pathlib import Path
import tempfile
from datetime import datetime, timedelta
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


def default_server_base_url():
    """URL serveur par défaut (qt_common), partagée par toutes les apps DesktopApp.

    DEBUG=True → LOCAL_DEV_URL (http://127.0.0.1:8001), sinon BASE_URL prod.
    """
    try:
        from Common.cstatic import BASE_URL, CConstants, DEBUG, LOCAL_DEV_URL

        if bool(getattr(CConstants, "DEBUG", False) or DEBUG):
            return str(LOCAL_DEV_URL or "").rstrip("/") or "http://127.0.0.1:8001"
        return str(BASE_URL or "").rstrip("/") or "http://176.58.116.12:9001"
    except Exception:
        return "http://176.58.116.12:9001"


def resolve_server_base_url():
    """Une seule URL : en DEBUG → local ; sinon Settings.url (hors localhost), sinon BASE_URL.

    Sans --debug, une Settings.url laissée à 127.0.0.1 (premier lancement debug)
    ne doit pas empêcher l'envoi vers le serveur de production.
    """
    try:
        from Common.cstatic import CConstants, DEBUG

        if bool(getattr(CConstants, "DEBUG", False) or DEBUG):
            return default_server_base_url()
    except Exception:
        pass
    try:
        from Common.models import Settings

        configured = str(Settings.get(id=1).url or "").rstrip("/")
        if (
            configured
            and not _is_local_server(configured)
            and "file-repo.ml" not in configured.lower()
        ):
            return configured
    except Exception:
        pass
    return default_server_base_url()


def _configured_server_url():
    try:
        return resolve_server_base_url()
    except Exception:
        return default_server_base_url()


def _is_local_server(url):
    lowered = str(url or "").lower()
    return "://127.0.0.1" in lowered or "://localhost" in lowered


def access_server():
    if not CConstants.SERV:
        logger.info("Not server mode")
        return False

    server_url = _configured_server_url()
    if not server_url:
        return False
    if not _is_local_server(server_url) and not internet_on():
        return False
    try:
        urlopen(server_url, timeout=1)
        return True
    except URLError:
        return False
    except Exception as e:
        logger.debug(e)
        return False


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
    """Timestamp Unix ; None si la date est absente (champs nullable)."""
    if date is None:
        return None
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
    """Construit une URL sur la base unique (Settings.url ou BASE_URL qt_common)."""
    base = resolve_server_base_url()
    path = str(sub_url or "").lstrip("/")
    if not path:
        return base
    return "{}/{}".format(base, path)


def product_page_url():
    """Page produit sur le site, ex. http://host/app/GGarage/."""
    base = resolve_server_base_url().rstrip("/")
    try:
        from Common.cstatic import CConstants

        slug = str(getattr(CConstants, "APP_NAME", "") or "").strip()
    except Exception:
        slug = ""
    if slug:
        return "{}/app/{}/".format(base, slug)
    return "{}/".format(base)


def license_management_url():
    """Page offres en ligne, ex. http://host/app/offres/Mpayment/."""
    base = resolve_server_base_url().rstrip("/")
    try:
        from Common.cstatic import CConstants

        slug = str(getattr(CConstants, "APP_NAME", "") or "").strip()
    except Exception:
        slug = ""
    if slug:
        return "{}/app/offres/{}/".format(base, slug)
    return "{}/".format(base)


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

    remember_machine()
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
_LICENSE_SNAPSHOT = "license.json"
_USED_CODES = "used_codes.json"
_EVALUATION_KEY = "__evaluation__"


def _application_name():
    """Nom de l'application en cours. Il entre dans la clé de licence."""
    import Common.cstatic as cstatic

    name = getattr(cstatic.CConstants, "APP_NAME", None) or getattr(cstatic, "APP_NAME", None)
    text = str(name or "").strip()
    return text or "Common"


def _app_license_dir():
    """Dossier de licence propre à l'application, dans le profil utilisateur."""
    raw = _application_name()
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in raw).strip("_")
    return _durable_license_dir() / "apps" / (safe or "Common")


def _durable_license_dir():
    """Dossier du profil utilisateur : l'identifiant machine y survit à une réinstallation."""
    override = (os.environ.get("COMMON_SHARED_LICENSE_DIR") or "").strip()
    if override:
        return Path(override)
    system = platform.system()
    home = Path.home()
    if system == "Windows":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        root = Path(base) if base else home / "AppData" / "Local"
    elif system == "Darwin":
        root = home / "Library" / "Application Support"
    else:
        xdg = (os.environ.get("XDG_DATA_HOME") or "").strip()
        root = Path(xdg) if xdg else home / ".local" / "share"
    return root / "qt_common"


def _read_node_file(path):
    try:
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace").strip()
            if text:
                return int(text)
    except (ValueError, OSError):
        logger.debug("Lecture identifiant machine impossible: %s", path, exc_info=True)
    return None


def _write_node_file(path, value):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_file() and path.read_text(encoding="utf-8", errors="replace").strip() == str(int(value)):
            return
        path.write_text(str(int(value)), encoding="utf-8")
    except OSError as e:
        logger.warning("Impossible d'enregistrer l'identifiant machine (%s): %s", path, e)


_HARDWARE_STAMP = ".common_device_hw"


def _hardware_token():
    """Jeton du matériel de cet ordinateur. Vide si le système ne le fournit pas."""
    token = ""
    system = platform.system()
    try:
        if system == "Darwin":
            output = subprocess.check_output(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                text=True,
                timeout=5,
                stderr=subprocess.DEVNULL,
            )
            match = None
            for line in output.splitlines():
                if "IOPlatformUUID" in line and "=" in line:
                    match = line.split("=", 1)[1].strip().strip('"')
                    break
            token = match or ""
        elif system == "Windows":
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography"
            ) as key:
                token, _kind = winreg.QueryValueEx(key, "MachineGuid")
        else:
            for candidate in (Path("/etc/machine-id"), Path("/var/lib/dbus/machine-id")):
                if candidate.is_file():
                    token = candidate.read_text(encoding="utf-8", errors="replace").strip()
                    if token:
                        break
    except Exception:
        logger.debug("Identifiant matériel indisponible", exc_info=True)
        token = ""
    return str(token or "").strip()


def _hardware_node():
    """Numéro lié au matériel. None si seul un identifiant copiable est disponible."""
    token = _hardware_token()
    if not token:
        return None
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


def _stable_machine_node():
    """Numéro de cette machine seule.

    Il vient du matériel (UUID, MachineGuid ou machine-id), pas d'un fichier
    posé à côté de l'application : ce fichier voyage quand on copie le dossier
    sur un autre ordinateur. Après réinstallation sur le même ordinateur, le
    numéro reste celui du matériel.
    """
    durable = _durable_license_dir() / _STABLE_NODE_BASENAME
    stamp_path = _durable_license_dir() / _HARDWARE_STAMP
    hardware = _hardware_node()
    if hardware is not None:
        stored = _read_node_file(durable)
        stamp = _read_node_file(stamp_path)
        if stored is not None and stamp == hardware:
            return stored
        _write_node_file(durable, hardware)
        _write_node_file(stamp_path, hardware)
        logger.info("Identifiant de cette machine enregistré")
        return hardware
    stored = _read_node_file(durable)
    if stored is not None:
        return stored
    node = int(getnode())
    _write_node_file(durable, node)
    logger.info("Identifiant machine enregistré dans le profil utilisateur")
    return node


def clean_mac():
    """Identifiant matériel stabilisé, conservé hors du dossier de l'application."""
    return _stable_machine_node()


def machine_identity():
    """Identifiant stable de l'ordinateur. Il ne change pas quand l'adresse MAC change."""
    return "%x" % int(_stable_machine_node())


def hardware_guid():
    """MachineGuid (Windows), IOPlatformUUID (macOS) ou machine-id (Linux)."""
    return _hardware_token()


def _is_md5_hex(text):
    low = str(text or "").strip().lower()
    return len(low) == 32 and all(c in "0123456789abcdef" for c in low)


def _license_file_paths():
    return (
        Path(get_lcse_file()),
        _app_license_dir() / "LICENCE",
    )


def _read_license_code_file():
    for path in _license_file_paths():
        try:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            continue
        if _is_md5_hex(text):
            return text.lower()
    return None


def write_lcse_file(content):
    """Écrit le code licence à côté de l'application et dans le profil utilisateur."""
    text = str(content).strip()
    for path in _license_file_paths():
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        except OSError as e:
            logger.warning("Impossible d'enregistrer LICENCE (%s): %s", path, e)


def remove_lcse_files():
    """Retire la licence de cette application, pas l'identifiant de la machine."""
    for path in _license_file_paths():
        try:
            path.unlink(missing_ok=True)
        except OSError as e:
            logger.warning("Impossible de supprimer LICENCE (%s): %s", path, e)
    snapshot = _app_license_dir() / _LICENSE_SNAPSHOT
    try:
        snapshot.unlink(missing_ok=True)
    except OSError as e:
        logger.warning("Impossible de supprimer la copie de licence (%s): %s", snapshot, e)


def _dump_dt(value):
    if not value:
        return None
    try:
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        return None


def _load_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def persist_license_record(license_row):
    """Copie la licence de cette application hors de son dossier."""
    if license_row is None or not getattr(license_row, "code", None):
        return
    payload = {
        "application": _application_name(),
        "code": str(license_row.code),
        "isactivated": bool(license_row.isactivated),
        "activation_date": _dump_dt(getattr(license_row, "activation_date", None)),
        "can_expired": bool(license_row.can_expired),
        "evaluation": bool(license_row.evaluation),
        "expiration_date": _dump_dt(getattr(license_row, "expiration_date", None)),
        "owner": license_row.owner or "",
    }
    path = _app_license_dir() / _LICENSE_SNAPSHOT
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as e:
        logger.warning("Impossible de mémoriser la licence (%s): %s", path, e)
        return
    write_lcse_file(payload["code"])


def _load_license_snapshot():
    path = _app_license_dir() / _LICENSE_SNAPSHOT
    try:
        if not path.is_file():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.debug("Copie de licence illisible", exc_info=True)
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _payload_grants(payload):
    """Même règle que License.can_use, à partir de la copie partagée."""
    if not payload:
        return False
    if payload.get("isactivated"):
        return True
    if not payload.get("can_expired"):
        return False
    expires = _load_dt(payload.get("expiration_date"))
    return expires is not None and datetime.now() < expires


def _row_grants(row):
    if row is None:
        return False
    if row.isactivated:
        return True
    if not row.can_expired or not row.expiration_date:
        return False
    return datetime.now() < row.expiration_date


def _restore_durable_license(expected_code):
    from Common.models import License

    payload = _load_license_snapshot()
    if not payload:
        return None
    code = str(payload.get("code") or "")
    recorded_app = str(payload.get("application") or "")
    if recorded_app and recorded_app != _application_name():
        return None
    if not code or code != str(expected_code):
        return None
    try:
        row = License.get(License.code == code)
    except License.DoesNotExist:
        row = License(code=code)
    row.isactivated = bool(payload.get("isactivated"))
    row.can_expired = bool(payload.get("can_expired"))
    row.evaluation = bool(payload.get("evaluation"))
    row.owner = payload.get("owner") or row.owner or "USER"
    activated = _load_dt(payload.get("activation_date"))
    if activated is not None:
        row.activation_date = activated
    expires = _load_dt(payload.get("expiration_date"))
    row.expiration_date = expires
    row.save()
    logger.info("Licence de %s restaurée", _application_name())
    return row


def remember_machine():
    """Mémorise la clé de cette application et la rétablit après réinstallation.

    La clé dépend du poste et du nom de l'application. Activer l'une
    ne débloque pas les autres.
    """
    from Common.models import License

    _stable_machine_node()
    code = str(make_lcse())
    saved = _load_license_snapshot()
    saved_ok = bool(saved) and str(saved.get("code") or "") == code

    if saved_ok:
        row = _restore_durable_license(code)
        if row is not None and _payload_grants(saved):
            persist_license_record(row)
        return

    try:
        local = License.get(License.code == code)
    except License.DoesNotExist:
        local = None
    except Exception:
        logger.exception("Lecture de la licence impossible")
        return

    if _row_grants(local):
        persist_license_record(local)
        logger.info("Licence de %s mémorisée pour cette application", _application_name())


def _used_codes_path():
    return _app_license_dir() / _USED_CODES


def _load_used_codes():
    path = _used_codes_path()
    try:
        if not path.is_file():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.debug("Historique des codes illisible", exc_info=True)
        return {}
    if not isinstance(data, dict):
        return {}
    codes = data.get("codes")
    return codes if isinstance(codes, dict) else {}


def _save_used_codes(codes):
    path = _used_codes_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"codes": codes}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _normalize_activation_code(raw):
    return "".join(str(raw or "").strip().replace("|", ":").replace(";", ":").split())


def remember_evaluation_period(expiration):
    """Mémorise une évaluation déjà commencée, sans en reculer ni en avancer la fin."""
    if expiration is None:
        return
    codes = _load_used_codes()
    if _EVALUATION_KEY in codes:
        return
    codes[_EVALUATION_KEY] = {"expiration": _dump_dt(expiration), "days": 60}
    _save_used_codes(codes)


def start_evaluation_once(days=60):
    """Démarre l'évaluation une seule fois. Une période échue ne peut pas être relancée."""
    codes = _load_used_codes()
    entry = codes.get(_EVALUATION_KEY)
    now = datetime.now().replace(microsecond=0)
    if isinstance(entry, dict):
        expires = _load_dt(entry.get("expiration"))
        if expires is not None and now >= expires:
            raise ValueError(
                "La période d'évaluation est terminée et ne peut plus être réutilisée."
            )
        if expires is not None:
            return expires
    expires = now + timedelta(days=int(days))
    codes[_EVALUATION_KEY] = {"expiration": _dump_dt(expires), "days": int(days)}
    _save_used_codes(codes)
    return expires


def register_activation_code(raw, machine_hash, app_slug):
    """Valide un code et fige sa date de fin à la première utilisation.

    Un code à durée limitée déjà expiré est refusé. Le recoller ne
    recommence pas la période. Une licence illimitée n'expire pas.
    Retourne ``(jours ou None, date de fin ou None)``.
    """
    text = _normalize_activation_code(raw)
    days = interpret_activation_code(text, machine_hash, app_slug)
    codes = _load_used_codes()
    entry = codes.get(text)
    now = datetime.now().replace(microsecond=0)
    if isinstance(entry, dict) and "expiration" in entry:
        expires = _load_dt(entry.get("expiration"))
        if expires is not None and now >= expires:
            raise ValueError("Ce code a expiré et ne peut plus être réutilisé.")
        return days, expires
    expires = None if days is None else now + timedelta(days=int(days))
    codes[text] = {"expiration": _dump_dt(expires), "days": days}
    _save_used_codes(codes)
    return days, expires


def interpret_activation_code(raw, machine_hash, app_slug):
    """Valide un code de licence généré et retourne sa durée en jours.

    ``None`` signifie une licence illimitée. Seul le code signé
    ``clé:durée:signature`` est accepté. La clé machine affichée sert à
    reconnaître l'ordinateur et à produire ce code ; elle n'active rien.
    """
    text = str(raw or "").strip()
    machine = str(machine_hash or "").strip().lower()
    if not text:
        raise ValueError("Code de licence vide")
    if ":" not in text and text.lower() == machine:
        raise ValueError(
            "Ce code identifie la machine. Collez le code de licence généré à partir de celui-ci."
        )
    from ..license_code import parse_activation_code

    parsed_machine, days = parse_activation_code(text, app_slug=app_slug)
    if str(parsed_machine).strip().lower() != machine:
        raise ValueError(
            "Ce code ne correspond pas à cette application sur cet ordinateur."
        )
    return days


def apply_signed_license(raw, machine_code, app_slug, evaluation=False):
    """Enregistre localement un code signé renvoyé par le serveur."""
    from Common.models import License

    days, expiration = register_activation_code(raw, machine_code, app_slug)
    try:
        row = License.get(License.code == machine_code)
    except License.DoesNotExist:
        row = License(code=machine_code)
    row.code = machine_code
    row.activation_date = datetime.now()
    row.evaluation = bool(evaluation)
    row.owner = "Évaluation" if evaluation else "En ligne"
    if days is None:
        row.expiration_date = None
        row.activation()
    else:
        row.isactivated = False
        row.can_expired = True
        row.expiration_date = expiration
        row.save()
        if evaluation:
            remember_evaluation_period(expiration)
    write_lcse_file(machine_code)
    persist_license_record(row)
    return row


def _revoke_local_license(machine_code):
    from Common.models import License

    try:
        row = License.get(License.code == machine_code)
    except License.DoesNotExist:
        return
    row.remove_activation()
    persist_license_record(row)


def request_online_license():
    """Demande la licence en ligne seulement si aucune licence locale valide.

    Si l'orga n'est pas encore syncro, laisse ``inscription_client`` gérer
    l'évaluation (un seul envoi, pas get_licence + inscription).
    """
    from urllib.request import Request

    _lcse, status = is_valide_mac()
    if status == CConstants.OK:
        logger.info("Licence locale déjà valide — pas d'envoi get_licence")
        return {
            "ok": True,
            "skipped": True,
            "message": "Licence locale déjà valide.",
        }

    try:
        from Common.models import Organization

        orga = Organization.get(id=1)
        if not orga.is_syncro:
            logger.info(
                "Pas encore inscrit — get_licence omis (inscription_client unique)"
            )
            return {
                "ok": False,
                "deferred": True,
                "message": "Inscription à faire avant get_licence.",
            }
    except Exception:
        pass

    machine = str(make_lcse())
    app_slug = _application_name()
    payload = json.dumps({"app": app_slug, "machine_key": machine}).encode("utf-8")
    url = get_server_url("get_licence")
    body = None
    last_error = None
    request = Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
        logger.info("Licence demandée à %s", url)
    except Exception as exc:
        last_error = exc
        logger.info("Licence injoignable sur %s : %s", url, exc)

    if body is None:
        logger.info("Licence en ligne indisponible : %s", last_error)
        return {
            "ok": False,
            "offline": True,
            "message": "Serveur de licences injoignable.",
        }

    if not isinstance(body, dict):
        return {"ok": False, "offline": False, "message": "Réponse de licence illisible."}

    if body.get("force_kill") or (
        body.get("found") and body.get("can_use") == CConstants.IS_EXPIRED
    ):
        _revoke_local_license(machine)
        return {
            "ok": False,
            "offline": False,
            "refused": True,
            "message": body.get("message") or "Licence refusée par le serveur.",
        }

    code = body.get("code")
    if body.get("found") and code and body.get("can_use") == CConstants.OK:
        try:
            apply_signed_license(
                code,
                machine,
                app_slug,
                evaluation=bool(body.get("evaluation")),
            )
        except ValueError as exc:
            return {"ok": False, "offline": False, "message": str(exc)}
        return {
            "ok": True,
            "offline": False,
            "applied": True,
            "evaluation": bool(body.get("evaluation")),
            "message": body.get("message") or "Licence obtenue en ligne.",
        }

    if body.get("found") and body.get("can_use") == CConstants.OK:
        return {
            "ok": True,
            "offline": False,
            "message": body.get("message") or "Licence en ligne confirmée.",
        }

    return {
        "ok": False,
        "offline": False,
        "refused": True,
        "message": body.get("message") or "Aucune licence en ligne pour ce poste.",
    }


def make_lcse(lcse=None):
    """Clé de cette application sur cette machine. Inutilisable sur un autre ordinateur."""
    if lcse is not None:
        return hashlib.md5(str(lcse).encode("utf-8")).hexdigest()
    raw = _stable_machine_node()
    identity = "%s\n%s" % (_application_name(), raw)
    logger.debug("Clé de licence pour %s", _application_name())
    return hashlib.md5(identity.encode("utf-8")).hexdigest()


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
