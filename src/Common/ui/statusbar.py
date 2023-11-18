#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: fadiga

import os
import sys
from threading import Event

import requests
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QLabel, QProgressBar, QPushButton, QStatusBar

from ..cstatic import logger
from ..server import Network
from .util import acces_server, get_serv_url, internet_on, is_valide_mac

try:
    from ..cstatic import CConstants
except Exception as e:
    print(e)

# base_url = CConstants.BASE_URL


class GStatusBar(QStatusBar):
    def __init__(self, parent=None):
        QStatusBar.__init__(self, parent)
        if not CConstants.SERV:
            logger.info("Not Serveur ")
            return
        logger.info("Option server active")
        self.stopFlag = Event()
        self.info_label = QLabel()
        icon_label = QLabel()
        name_label = QLabel()
        name_label.setText(
            'Développer par IBS-Mali | <a href="https://ibsmali.ml/">ibsmali.ml</a>'
        )
        name_label.setOpenExternalLinks(True)
        icon_label.setPixmap(QPixmap("{}".format(CConstants.IBS_LOGO)))
        self.addWidget(icon_label, 0)
        self.addWidget(name_label, 1)
        self.addWidget(self.info_label, 1)

        self.check_serv = TaskThreadServer(self)
        QObject.connect(
            self.check_serv,
            SIGNAL("contact_server"),
            self.contact_server,
            Qt.QueuedConnection,
        )
        QObject.connect(
            self.check_serv, SIGNAL("download_"), self.download_, Qt.QueuedConnection
        )
        try:
            logger.info("check_serv")
            self.check_serv.start()
        except Exception as e:
            logger.error("Failed start check serv ", e)

    def download_(self):
        # print("download_")
        self.b = QPushButton("")
        self.b.setIcon(
            QIcon.fromTheme(
                "",
                QIcon(
                    "{img_media}{img}".format(
                        img_media=CConstants.img_cmedia, img="setup.png"
                    )
                ),
            )
        )
        self.b.clicked.connect(self.get_setup)
        self.b.setText(self.check_serv.data.get("message"))
        self.addWidget(self.b)

    def get_setup(self):
        self.progressBar = QProgressBar(self)
        # self.progressBar.setGeometry(430, 30, 400, 25)
        self.addWidget(self.progressBar, 2)
        self.t = TaskThreadDowload(self)
        QObject.connect(self.t, SIGNAL("download_finish"), self.download_finish)

        try:
            self.t.start()
        except Exception as exc:
            logger.error("exc :", exc)

    def failure(self):
        logger.warning("La mise à jour a échoué.")
        self.info_label.setText("La mise à jour a échoué.")
        self.progressBar.close()
        self.b.setEnabled(True)

    def download_finish(self):
        logger.info("download_finish")
        self.b.hide()
        self.progressBar.close()
        self.instb = QPushButton(
            "installer la Ver. {}".format(self.check_serv.data.get("version"))
        )
        self.instb.setIcon(
            QIcon.fromTheme(
                "",
                QIcon(
                    "{img_media}{img}".format(
                        img_media=CConstants.img_cmedia, img="setup.png"
                    )
                ),
            )
        )
        self.instb.clicked.connect(self.start_install)
        # self.progressBar.close()
        self.addWidget(self.instb)

    def start_install(self):
        try:
            os.startfile(os.path.basename(self.installer_name))
            sys.exit()
        except Exception as e:
            # print(e)
            self.failure()

    def download_setup_file(self):
        logger.info("download setup")
        self.b.setEnabled(False)
        self.info_label.setText("Téléchargement en cours ...")

        self.installer_name = "{}.exe".format(self.check_serv.data.get("app"))
        url = get_serv_url(self.check_serv.data.get("setup_file_url"))
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            total_length = r.headers.get("content-length")
            with open(self.installer_name, "wb") as f:
                if total_length is None:  # no content length header
                    f.write(r.content)
                else:
                    dl = 0
                    for data in r.iter_content(chunk_size=4096):
                        dl += len(data)
                        f.write(data)
                        done = int(100 * dl / int(total_length))
                        self.progressBar.setValue(done)
        self.info_label.setText("Fin de téléchargement ...")

    def contact_server(self):
        logger.info("check contact")

        s_style, response_s = "color:red", "Connexion perdue !"
        net_style, net_response = "color:red", "Connexion perdue !"
        lse_style, r_lse = "color:red", "Non autorisée"
        sy_style, r_sy = "color:red", "Non autorisée"
        if internet_on():
            net_style, net_response = "color:green", "ok"
        if acces_server():
            s_style, response_s = "color:green", "Connecté"
            if self.check_serv.data.get("backup_online"):
                sy_style, r_sy = "color:green", "autorisé"

        lse, valide = is_valide_mac()
        if lse:
            lse_style, r_lse = (
                "color:green",
                "<b>{}</b>".format(lse.remaining_days()) if valide else "Expirée",
            )
        self.info_label.setText(
            """
            <strong>internet : </strong><span style={net_style}>{net_response} </span> 
            <strong>Serveur : </strong><span style={s_style}>{response_s}</span><br>
            <strong> Synchronisation : </strong><span style={sy_style}>{r_sy}</span>
            <strong> License : </strong><span style={lse_style}>{r_lse}</span>
            """.format(
                s_style=s_style,
                response_s=response_s,
                net_style=net_style,
                net_response=net_response,
                lse_style=lse_style,
                r_lse=r_lse,
                sy_style=sy_style,
                r_sy=r_sy,
            )
        )
        self.emit(SIGNAL("contact_server"))


class TaskThreadDowload(QThread):
    def __init__(self, parent):
        QThread.__init__(self, parent)
        self.parent = parent

    def run(self):
        self.parent.download_setup_file()
        self.emit(SIGNAL("download_finish"))


class TaskThreadServer(QThread):
    def __init__(self, parent):
        QThread.__init__(self, parent)
        self.parent = parent
        self.stopped = parent.stopFlag

    def run(self):
        p = 1
        w = 5
        from .models import Organization

        while not self.stopped.wait(w):
            if Organization().select().count() > 0:
                orga_slug = Organization.get(id=1).slug
                # print('QStatusBar orga_slug', orga_slug)
                if acces_server():
                    logger.info("Server acces is OK")
                    if not orga_slug:
                        rep_serv = Network().get_or_inscript_app()
                    else:
                        self.data = Network().update_version_checher()
                        # print("Contact server : ", self.data)

                        w = 50
                        if not self.data:
                            return
                        if not self.data.get("is_last") and p == 1:
                            p += 1
                            self.emit(SIGNAL("download_"))
                else:
                    logger.info("Not server acces")
                self.emit(SIGNAL("contact_server"))
