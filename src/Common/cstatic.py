#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# Maintainer: Fad

import logging
import os
import re
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Configuration du logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _resolve_log_dir():
    """Dossier des logs : à côté de l'exe (installé) ou du script lancé (dev)."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        argv0 = sys.argv[0] if sys.argv else ""
        base = None
        if argv0:
            try:
                script = Path(argv0).resolve()
                if script.is_file():
                    base = script.parent
            except OSError:
                base = None
        if base is None:
            base = Path.cwd()
    d = base / "logs"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError:
        d = Path.cwd() / "logs"
        d.mkdir(parents=True, exist_ok=True)
    return d


log_dir = _resolve_log_dir()

# Configuration du format des logs
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class StartupLogFilter(logging.Filter):
    """Filtre pour ne garder que les logs de démarrage et les erreurs"""
    
    # Mots-clés qui indiquent un log de démarrage
    STARTUP_KEYWORDS = [
        'initialisation', 'démarrage', 'connexion', 'base de données',
        'database', 'migration', 'paramètres', 'settings', 'version',
        'organisation', 'superuser', 'tables créées', 'connectée',
        'modules', 'chargés', 'fermeture', 'sauvegarde'
    ]
    
    def filter(self, record):
        """Filtre les logs pour ne garder que les infos de démarrage et les erreurs"""
        # Toujours garder les erreurs et warnings
        if record.levelno >= logging.WARNING:
            return True
        
        # Pour les logs INFO et DEBUG, vérifier s'ils contiennent des mots-clés de démarrage
        message_lower = record.getMessage().lower()
        return any(keyword in message_lower for keyword in self.STARTUP_KEYWORDS)


# Handler pour la console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Handler pour le fichier de log (uniquement infos de démarrage et erreurs)
LOG_FILE = log_dir / 'app.log'
try:
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1024*1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)  # Niveau INFO pour capturer les infos de démarrage
    file_handler.addFilter(StartupLogFilter())  # Filtrer pour ne garder que les logs de démarrage
    file_handler.setFormatter(formatter)
except OSError:
    file_handler = None

# Ajout des handlers au logger
logger.addHandler(console_handler)
if file_handler is not None:
    logger.addHandler(file_handler)

logger.info("Fichier de log: %s", LOG_FILE)

# Configuration du logger Peewee pour réduire les logs DEBUG SQL
peewee_logger = logging.getLogger('peewee')
peewee_logger.setLevel(logging.INFO)  # Masquer les requêtes SQL DEBUG


def _version_from_metadata(dist_name: str) -> str | None:
    try:
        # Py 3.8+: importlib.metadata (backport intégré à partir de 3.8)
        from importlib import metadata as importlib_metadata  # type: ignore

        return importlib_metadata.version(dist_name)
    except Exception:
        return None


def _version_from_pyproject() -> str | None:
    """Lit la version depuis pyproject.toml sans dépendance TOML.

    Objectif: éviter de maintenir 2 versions (UI vs package).
    """
    try:
        root = Path(__file__).resolve().parents[2]  # .../qt_common/
        pyproject = root / "pyproject.toml"
        if not pyproject.exists():
            return None

        in_project = False
        for raw in pyproject.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                in_project = line == "[project]"
                continue
            if not in_project:
                continue

            m = re.match(r'version\s*=\s*"([^"]+)"\s*$', line)
            if m:
                return m.group(1)
    except Exception:
        return None
    return None


def get_app_version() -> str:
    """Retourne la version de l'app (source unique: packaging/pyproject)."""
    # 1) si on est dans le repo (pyproject présent), c'est la référence
    v = _version_from_pyproject()
    if v:
        return v

    # 2) sinon (package installé), lire les métadonnées
    v = _version_from_metadata("Common")
    if v:
        return v

    # 3) fallback
    return "dev"

# ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# PERIODS
W = "week"
M = "month"
OK = "ok"
IS_NOT_ACTIVATED = "is_not_activated"
IS_EXPIRED = "is_expired"
img_media = "static/images/"
NAME_MAIN = "main.py"
# img_media = os.path.join(ROOT_DIR, "static", "images/")
img_cmedia = str(Path(__file__).parent.joinpath("cimages").resolve()) + "/"

IBS_LOGO = os.path.join(img_cmedia, "ibs.jpg")
# ------------------------- Autor --------------------------#
AUTOR = "Fadiga Ibrahima"
EMAIL_AUT = "ibfadiga@gmail.com"
TEL_AUT = "(+223)76 43 38 90"
ADRESS_AUT = "Boulkassoumbougou Bamako"
ORG_AUT = "Copyright © 2012 xxxx"
# ------------------------- Application --------------------------#
inco_exit = ""
inco_dashboard = ""
EMAIL_ORGA = ""
APP_NAME = "Projet en dev"
APP_DATE = "02/2013"
APP_VERSION = get_app_version()
DEBUG = False
ARMOIRE = "."

des_image_record = Path(__file__)
EXCLUDE_MENU_ADMIN = []
LSE = True
ORG = False
SERV = False
list_models = []
# Tables proposées dans « Suppression des enregistrements » (libellé, classe Peewee).
# Les applis peuvent faire CLEANABLE_MODELS.extend([...]) pour remplir la liste partagée.
CLEANABLE_MODELS = []
# Prérequis : avant de vider une table, vider d’abord ces modèles (clé → liste de classes).
CLEAN_MODEL_PREREQUISITES = {}
# Rempli par l’appli (ex. G-Sady) : callable sans argument retournant les lignes
# pour l’onglet « Historique » de l’admin (liste de tuples pour le tableau).
ADMIN_HISTORY_FETCH = None
APP_LOGO = os.path.join(img_media, "logo.png")
APP_LOGO_ICO = os.path.join(img_media, "logo.ico")
ExportFolders = []
ExportFiles = []
BASE_URL = "http://176.58.116.12:9001"
# Si le serveur distant ne répond pas, essayer ce serveur de développement local.
LOCAL_DEV_URL = "http://127.0.0.1:8001"

# Contrôle de licence au démarrage. False = pas de fenêtre d'activation (install / démo).
# Peut aussi être désactivé sans recompiler : variable d'environnement COMMON_SKIP_LICENSE=1
# (valeurs acceptées : 1, true, yes, on).
LICENSE_REQUIRED = True

# True = sauvegarde auto à la fermeture uniquement sur clé USB (dialogues).
# False = copie silencieuse dans le dossier backups/ à côté de database.db (recommandé, exe / atexit).
BACKUP_TO_USB = False

# Valeur par défaut (nouveaux paramètres) : sauvegarde auto à la fermeture.
# L’utilisateur peut activer/désactiver via Préférences → Paramètre.
AUTO_BACKUP_ON_EXIT = False


def license_required():
    """Retourne False si la licence ne doit pas bloquer l'application."""
    v = (os.environ.get("COMMON_SKIP_LICENSE") or "").strip().lower()
    if v in ("1", "true", "yes", "on"):
        return False
    return LICENSE_REQUIRED


class CConstants:
    """Classe contenant les constantes de l'application"""
    
    # PERIODS
    W = W
    M = M
    OK = OK
    IS_NOT_ACTIVATED = IS_NOT_ACTIVATED
    IS_EXPIRED = IS_EXPIRED
    
    # Chemins
    img_media = img_media
    NAME_MAIN = NAME_MAIN
    img_cmedia = img_cmedia
    IBS_LOGO = IBS_LOGO
    
    # Informations sur l'auteur
    AUTOR = AUTOR
    EMAIL_AUT = EMAIL_AUT
    TEL_AUT = TEL_AUT
    ADRESS_AUT = ADRESS_AUT
    ORG_AUT = ORG_AUT
    
    # Configuration de l'application
    inco_exit = inco_exit
    inco_dashboard = inco_dashboard
    EMAIL_ORGA = EMAIL_ORGA
    APP_NAME = APP_NAME
    APP_DATE = APP_DATE
    APP_VERSION = APP_VERSION
    DEBUG = DEBUG
    ARMOIRE = ARMOIRE
    
    # Chemins et fichiers
    des_image_record = des_image_record
    EXCLUDE_MENU_ADMIN = EXCLUDE_MENU_ADMIN
    LSE = LSE
    ORG = ORG
    SERV = SERV
    list_models = list_models
    CLEANABLE_MODELS = CLEANABLE_MODELS
    CLEAN_MODEL_PREREQUISITES = CLEAN_MODEL_PREREQUISITES
    ADMIN_HISTORY_FETCH = ADMIN_HISTORY_FETCH
    APP_LOGO = APP_LOGO
    APP_LOGO_ICO = APP_LOGO_ICO
    ExportFolders = ExportFolders
    ExportFiles = ExportFiles
    BASE_URL = BASE_URL
    LOCAL_DEV_URL = LOCAL_DEV_URL
    LICENSE_REQUIRED = LICENSE_REQUIRED
    BACKUP_TO_USB = BACKUP_TO_USB
    AUTO_BACKUP_ON_EXIT = AUTO_BACKUP_ON_EXIT

    def __init__(self):
        pass


_ARGV_DEBUG_APPLIED = False


def apply_argv_debug_flag(argv=None):
    """Active DEBUG si ``--debug`` (ou ``-d``) est passé en ligne de commande.

    Retire le flag de ``sys.argv`` (évite les warnings Qt) et met à jour
    ``DEBUG`` / ``CConstants.DEBUG``. Sans flag → ``False``.
    Idempotent : un second appel (ex. cmain après main) ne réécrit pas le flag.
    """
    global DEBUG, _ARGV_DEBUG_APPLIED
    if _ARGV_DEBUG_APPLIED:
        return DEBUG
    if argv is None:
        argv = sys.argv
    flags = {"--debug", "-d"}
    debug = any(arg in flags for arg in argv[1:])
    if argv is sys.argv:
        sys.argv[:] = [argv[0]] + [a for a in argv[1:] if a not in flags]
    DEBUG = bool(debug)
    CConstants.DEBUG = DEBUG
    _ARGV_DEBUG_APPLIED = True
    if DEBUG:
        logger.info("Mode DEBUG activé (--debug) → serveur %s", LOCAL_DEV_URL)
    return DEBUG


# Exportation explicite des symboles
__all__ = [
    "CConstants",
    "logger",
    "license_required",
    "LICENSE_REQUIRED",
    "apply_argv_debug_flag",
]
