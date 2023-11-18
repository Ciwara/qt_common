#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
from __future__ import absolute_import, division, print_function, unicode_literals

import errno
import os
import shutil
from datetime import datetime

from PyQt5.QtWidgets import QFileDialog, QWidget

from .models import DB_FILE, Organization, Version
from .ui.util import get_lcse_file, raise_error, raise_success, uopen_file

DATETIME = "{}".format(datetime.now().strftime("%m-%d-%Y_%Hh%Mm%Ss"))


def export_database_as_file():
    destination = QFileDialog.getSaveFileName(
        QWidget(),
        "Sauvegarder la base de Donnée.",
        "Sauvegarde du {} {}.db".format(DATETIME, Organization.get(id=1).name_orga),
        "*.db",
    )
    if not destination:
        return None
    try:
        shutil.copyfile(DB_FILE, destination)
        Version().get(id=1).update_v()
        raise_success(
            "Les données ont été exportées correctement.",
            "Conservez ce fichier précieusement car il contient toutes vos données.\n"
            "Exportez vos données régulièrement.",
        )
    except IOError:
        raise_error(
            "La base de données n'a pas pu être exportée.",
            "Vérifiez le chemin de destination puis re-essayez.\n\n                   "
            "Demandez de l'aide si le problème persiste.",
        )


def export_backup(folder=None, dst_folder=None):
    print("Exporting ...")
    directory = str(QFileDialog.getExistingDirectory(QWidget(), "Select Directory"))
    path_backup = "{path}-{date}-{name}".format(
        path=os.path.join(directory, "BACKUP"),
        date=DATETIME,
        name=Organization.get(id=1).name_orga,
    )

    if not directory:
        return None
    try:
        # TODO Savegarde version incremat de in db
        shutil.copyfile(DB_FILE, os.path.join(path_backup, DB_FILE))
        v = Version().get(id=1).update_v()
    except IOError:
        print("Error of copy database file")
    except Exception as e:
        print(e)

    try:
        if folder:
            copyanything(folder, os.path.join(path_backup, dst_folder))
        raise_success(
            "Le backup à été fait correctement.",
            """Conservez le dossier {} précieusement car il contient toutes vos données. Exportez vos données régulièrement.
            """.format(
                path_backup
            ),
        )
    except OSError as e:
        raise_error(
            "Le backup n'a pas pu être fait correctement.",
            "Vérifiez le chemin de destination puis re-essayez.\n"
            "\n Demandez de l'aide si le problème persiste.",
        )


def import_backup(folder=None, dst_folder=None):
    path_db_file = os.path.join(os.path.dirname(os.path.abspath("__file__")), DB_FILE)
    shutil.copy(path_db_file, "Avant-{}-{}.db".format(DB_FILE, DATETIME))
    name_select_f = QFileDialog.getOpenFileName(
        QWidget(), "Open Data File", "", "CSV data files (*.db)"
    )
    shutil.copy(name_select_f, path_db_file)

    raise_success(
        "Restoration des Donnée.",
        """Les données ont été correctement restorée
                    La version actualle de la base de donnée est {}
                    """.format(
            Version().get(id=1).display_name()
        ),
    )


def upload_file(folder=None, dst_folder=None, type_f=None):
    path_db_file = os.path.join(folder, DB_FILE)
    name_select_f = QFileDialog.getOpenFileName(
        QWidget(),
        "Open Data File",
        "./",
        "Image Files (*.png *.jpg *.bmp)".format(type_f),
    )
    shutil.copy(name_select_f, path_db_file)

    raise_success(
        "Importation.", "Import du fichier '{}' terminé.".format(name_select_f)
    )


def copyanything(src, dest):
    try:
        shutil.copytree(src, dest, ignore=None)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print("Directory not copied. Error: %s" % e)


def export_license_as_file():
    fil = get_lcse_file()
    uopen_file(fil)
