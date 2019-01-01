#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: fadiga

from PyQt4.QtGui import (QStatusBar, QProgressBar, QPixmap,
                         QLabel, QCommandLinkButton)
from PyQt4.QtCore import QThread, SIGNAL, QObject

import os
import requests
from server import Network
from configuration import Config

from Common.ui.util import internet_on

base_url = Config.BASE_URL


class GStatusBar(QStatusBar):

    def __init__(self, parent=None):

        QStatusBar.__init__(self, parent)

        if not Config.SERV:
            # print("Not Serveur ")
            return
        self.info_label = QLabel()
        icon_label = QLabel()
        name_label = QLabel()
        name_label.setText(
            'Développer par IBS-Mali | <a href="http://ibsmali.ml/">ibsmali.ml</a>')
        name_label.setOpenExternalLinks(True)
        icon_label.setPixmap(QPixmap("{}".format(Config.IBS_LOGO)))
        self.addWidget(icon_label, 0)
        self.addWidget(name_label, 1)
        self.addWidget(self.info_label, 1)

        text = """
            <table><tr><th>Internet : </th><td style='color:green'>OK</td></tr>
            <tr><th>Serveur : </th><td style='color:red'>{}</td></tr>
            </table>"""
        if internet_on(Config.BASE_URL):
            css = "color: gray; border: 1px solid gray"
            msg = text.format("No response")

        else:
            css = 'color: red'
            msg = text.format("No connection")
        self.info_label.setText(msg)
        self.info_label.setStyleSheet(css)

        self.check = TaskThreadServer(self)
        QObject.connect(self.check, SIGNAL("download_"), self.download_)
        self.check.start()

    def download_(self):
        # print("download_")
        self.b = QCommandLinkButton("")
        self.b.clicked.connect(self.get_setup)
        self.b.setText(self.check.data.get("message"))
        self.addWidget(self.b)

    def get_setup(self):
        self.progressBar = QProgressBar(self)
        # self.progressBar.setGeometry(430, 30, 400, 25)
        self.addWidget(self.progressBar, 2)
        self.t = TaskThread(self)
        QObject.connect(self.t, SIGNAL("download_finish"),
                        self.download_finish)
        self.t.start()

    def failure(self):
        # print("failure")
        self.info_label.setText("La mise à jour a échoué.")
        self.progressBar.close()
        self.b.setEnabled(True)

    def download_finish(self):
        # print('download_finish')
        self.b.hide()
        self.progressBar.close()
        self.instb = QCommandLinkButton("installer la Ver. {}".format(
            self.check.data.get("version")))
        self.instb.clicked.connect(self.start_install)
        # self.progressBar.close()
        self.addWidget(self.instb)

    def start_install(self):
        try:
            os.startfile(os.path.basename(self.installer_name))
            import sys
            sys.exit()
        except OSError:
            self.failure()

    def download_setup_file(self):
        self.b.setEnabled(False)
        self.info_label.setText("Téléchargement en cours ...")

        self.installer_name = "{}.exe".format(self.check.data.get("app"))
        url = "{}{}".format(base_url, self.check.data.get("setup_file_url"))
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            total_length = r.headers.get('content-length')
            with open(self.installer_name, 'wb') as f:
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


class TaskThread(QThread):

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

    def run(self):
        self.data = Network().update_version_checher()
        # print(self.data)
        if not self.data:
            return
        if not self.data.get("is_last"):
            self.emit(SIGNAL("download_"))
        self.emit(SIGNAL("update_data"))
