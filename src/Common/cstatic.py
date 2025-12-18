#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# Maintainer: Fad

import logging
import os
import re
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Configuration du logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Création du dossier logs s'il n'existe pas
log_dir = Path(__file__).parent.parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# Configuration du format des logs
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handler pour la console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Handler pour le fichier de log
file_handler = RotatingFileHandler(
    log_dir / 'app.log',
    maxBytes=1024*1024,  # 1MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Ajout des handlers au logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Configuration du logger Peewee pour réduire les logs DEBUG SQL
peewee_logger = logging.getLogger('peewee')
peewee_logger.setLevel(logging.INFO)  # Masquer les requêtes SQL DEBUG

logger.debug("Initialisation du module cstatic")


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
APP_LOGO = os.path.join(img_media, "logo.png")
APP_LOGO_ICO = os.path.join(img_media, "logo.ico")
ExportFolders = []
ExportFiles = []
BASE_URL = "https://file-repo.ml"


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
    APP_LOGO = APP_LOGO
    APP_LOGO_ICO = APP_LOGO_ICO
    ExportFolders = ExportFolders
    ExportFiles = ExportFiles
    BASE_URL = BASE_URL

    def __init__(self):
        logger.debug("Initialisation de CConstants")

# Exportation explicite des symboles
__all__ = ['CConstants', 'logger']
