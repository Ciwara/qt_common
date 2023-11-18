#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import absolute_import, division, print_function, unicode_literals

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QMenuBar, QMessageBox

from ..exports import export_backup, export_database_as_file, import_backup
from ..models import Owner, Settings
from .clean_db import DBCleanerWidget
from .common import FWidget
from .license_view import LicenseViewWidget

try:
    from ..cstatic import CConstants
except Exception as e:
    print(e)


class FMenuBar(QMenuBar, FWidget):
    def __init__(self, parent=None, admin=False, *args, **kwargs):
        QMenuBar.__init__(self, parent=parent, *args, **kwargs)

        self.setWindowIcon(QIcon(QPixmap("{}".format(CConstants.APP_LOGO_ICO))))

        self.parent = parent

        exclude_mn = CConstants.EXCLUDE_MENU_ADMIN
        # Menu File
        self.file_ = self.addMenu("&Fichier")
        # Export
        backup = self.file_.addMenu("&Base de données")
        backup.setIcon(QIcon("{}db.png".format(CConstants.img_cmedia)))
        # Sauvegarde
        savegarder = QAction(
            QIcon.fromTheme("", QIcon("{}export.png".format(CConstants.img_cmedia))),
            "Sauvegarder",
            self,
        )
        savegarder.setShortcut("Alt+E")
        savegarder.triggered.connect(self.goto_export_db)
        backup.addAction(savegarder)

        # Importer db
        import_db = QAction(
            QIcon.fromTheme("", QIcon("{}import_db.png".format(CConstants.img_cmedia))),
            "Importation db",
            self,
        )
        import_db.setShortcut("Alt+I")

        import_db.triggered.connect(self.goto_import_backup)
        backup.addAction(import_db)

        ow = Owner.select().where(Owner.islog == True)
        if ow.exists():
            if ow.get().group == Owner.ADMIN and "del_all" not in exclude_mn:
                backup.addAction(
                    "Suppression de tout les enregistrements", self.goto_clean_db
                )

        # Comptes utilisateur
        admin = self.file_.addMenu("&Outils")

        preference = self.addMenu("&Préference")

        if "theme" not in exclude_mn:
            _theme = preference.addMenu("Theme")
            styles = Settings.THEME
            list_theme = [
                (
                    {
                        "name": k.upper(),
                        "icon": "",
                        "admin": False,
                        "shortcut": "",
                        "theme": k,
                    }
                )
                for k in styles.keys()
            ]
            for m in list_theme:
                icon = ""
                if m.get("theme") == Settings.get(id=1).theme:
                    icon = "accept"
                el_menu = QAction(
                    QIcon("{}{}.png".format(CConstants.img_cmedia, icon)),
                    m.get("name"),
                    self,
                )
                el_menu.setShortcut(m.get("shortcut"))
                el_menu.triggered.connect(
                    lambda checked, goto=m["theme"]: self.change_theme(goto)
                )
                _theme.addSeparator()
                _theme.addAction(el_menu)
                _theme.setIcon(QIcon("{}theme.png".format(CConstants.img_cmedia)))

        if ow.exists():
            if ow.get().group == Owner.ADMIN:
                admin_ = QAction(
                    QIcon.fromTheme(
                        "", QIcon("{}settings.png".format(CConstants.img_cmedia))
                    ),
                    "Gestion Administration",
                    self,
                )
                admin_.setShortcut("Ctrl+G")
                admin_.triggered.connect(self.goto_admin)
                preference.addAction(admin_)
        # logout
        lock = QAction(
            QIcon("{}login.png".format(CConstants.img_cmedia)), "Verrouiller", self
        )
        lock.setShortcut("Ctrl+V")
        lock.setToolTip("Verrouiller l'application")
        lock.triggered.connect(self.logout)
        self.file_.addAction(lock)
        # R
        log_file = QAction(QIcon(), "Log ", self)
        log_file.setShortcut("Ctrl+l")
        # log_file.setToolTip(u"Verrouiller l'application")
        log_file.triggered.connect(self.open_logo_file)
        admin.addAction(log_file)

        g_license = self.addMenu("&Licence")
        if "license" not in exclude_mn:
            license = QAction(
                QIcon.fromTheme(
                    "emblem-system",
                    QIcon("{}licence.png".format(CConstants.img_cmedia)),
                ),
                "Activation",
                self,
            )
            license.setShortcut("Alt+A")
            license.triggered.connect(self.goto_license)
            g_license.addAction(license)

        # Exit
        exit_ = QAction(QIcon.fromTheme("application-exit", QIcon("")), "Exit", self)
        exit_.setShortcut("Ctrl+Q")
        exit_.setToolTip("Quiter l'application")
        # exit_.triggered.connect(self.parent.close())
        self.file_.addAction(exit_)

    def logout(self):
        from .login import LoginWidget

        LoginWidget(hibernate=True).exec_()

    # Export the database.
    def goto_export_db(self):
        export_database_as_file()

    def goto_export_backup(self):
        export_backup(folder=CConstants.des_image_record, dst_folder=CConstants.ARMOIRE)

    def goto_import_backup(self):
        # QMessageBox.about(self, u"Fonctionalité",
        # u"<h3>Cette fonction n'est pas fini... </h3>")
        import_backup(folder=CConstants.des_image_record, dst_folder=CConstants.ARMOIRE)

    def goto_clean_db(self):
        self.open_dialog(DBCleanerWidget, modal=True)

    # Admin

    def goto_admin(self):
        from .admin import AdminViewWidget

        self.change_main_context(AdminViewWidget)

    # G. license
    def goto_license(self):
        self.open_dialog(LicenseViewWidget, modal=True)

    def change_theme(self, theme):
        sttg = Settings.get(id=1)
        sttg.theme = theme
        sttg.save()
        self.restart()

    def restart(self):
        import subprocess
        import sys
        import os

        self.parent.close()
        path_main_name = os.path.join(
            os.path.dirname(os.path.abspath("__file__")), CConstants.NAME_MAIN
        )
        try:
            subprocess.Popen([sys.executable, path_main_name])
        except Exception as e:
            subprocess.call("python.exe " + path_main_name, shell=True)

    def goto(self, goto):
        self.change_main_context(goto)

    # Aide
    def goto_help(self):
        self.open_dialog(HTMLView, modal=True)

    def open_logo_file(self):
        from .util import uopen_file

        try:
            uopen_file(CConstants.NAME_MAIN.replace(".py", ".log"))
        except Exception as e:
            print("show log file ", e)

    # About
    def goto_about(self):
        QMessageBox.about(
            self,
            "À propos",
            """ <h2>{app_name}  version: {version_app} </h2>
                            <hr>
                            <h4><i>Logiciel de {app_name}.</i></h4>
                            <ul><li></li> <li><b>Developper par : </b>IBS-Mali </li>
                                <li><b>Adresse : </b>Bamako, Boulkassoumbougou Rue : 580 Porte : 388 </li>
                                <li><b>Tel: </b> +223 76 43 38 90 </li>
                                <li><b>E-mail : </b> info@ibsmali.ml <br/></li>
                                <li><a herf="https://ibsmali.ml"/> ibsmail.ml</li>
                            </ul>
                            """.format(
                app_name=CConstants.APP_NAME,
                autor=CConstants.AUTOR,
                version_app=CConstants.APP_VERSION,
            ),
        )
