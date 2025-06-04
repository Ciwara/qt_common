#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: fadiga

import os
import sys
from threading import Event

import requests
from Common.ui.util import access_server, get_server_url, internet_on, is_valide_mac
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QLabel, QProgressBar, QPushButton, QStatusBar

from ..cstatic import logger
from ..server import Network

try:
    from ..cstatic import CConstants
except Exception as e:
    print(e)


class GStatusBar(QStatusBar):
    def __init__(self, parent=None):
        super(GStatusBar, self).__init__(parent)

        if not CConstants.SERV:
            # logger.info("Server not configured.")
            return

        logger.info("Server option active.")
        self.stopFlag = Event()
        self.info_label = QLabel()
        self.init_ui()

    def init_ui(self):
        icon_label = QLabel()
        name_label = QLabel()
        name_label.setText(
            'Developed by IBS-Mali | <a href="https://ibsmali.ml/">ibsmali.ml</a>'
        )
        name_label.setOpenExternalLinks(True)
        icon_label.setPixmap(QPixmap(f"{CConstants.IBS_LOGO}"))
        self.addWidget(icon_label, 0)
        self.addWidget(name_label, 1)
        self.addWidget(self.info_label, 1)

        self.check_serv = TaskThreadServer(self)
        self.check_serv.contact_server_signal.connect(self.contact_server)
        self.check_serv.download_signal.connect(self.download)

        try:
            self.check_serv.start()
        except Exception as e:
            logger.error("Failed to start server check thread: {}".format(e))

    def download(self):
        self.download_button = QPushButton("")
        self.download_button.setIcon(
            QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}setup.png"))
        )
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setText(self.check_serv.data.get("message"))
        self.addWidget(self.download_button)

    def start_download(self):
        self.progress_bar = QProgressBar(self)
        self.addWidget(self.progress_bar, 2)
        download_thread = TaskThreadDownload(self)
        download_thread.download_finish_signal.connect(self.download_finish)

        try:
            download_thread.start()
        except Exception as exc:
            logger.error("Failed to start download thread: {exc}")

    def download_finish(self):
        self.download_button.hide()
        self.progress_bar.close()
        self.install_button = QPushButton(
            f"Install Version {self.check_serv.data.get('version')}"
        )
        self.install_button.setIcon(
            QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}setup.png"))
        )
        self.install_button.clicked.connect(self.start_install)
        self.addWidget(self.install_button)

    def start_install(self):
        try:
            os.startfile(os.path.basename(self.installer_name))
            sys.exit()
        except Exception as e:
            self.show_failure_message()

    def download_setup_file(self):
        self.download_button.setEnabled(False)
        self.info_label.setText("Downloading in progress...")

        self.installer_name = "{self.check_serv.data.get('app')}.exe"
        url = get_server_url(self.check_serv.data.get("setup_file_url"))
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            total_length = response.headers.get("content-length")
            with open(self.installer_name, "wb") as file:
                if total_length is None:
                    file.write(response.content)
                else:
                    downloaded_length = 0
                    for data in response.iter_content(chunk_size=4096):
                        downloaded_length += len(data)
                        file.write(data)
                        progress = int(100 * downloaded_length / int(total_length))
                        self.progress_bar.setValue(progress)

        self.info_label.setText("Download complete.")

    def contact_server(self):
        net_style, net_response = "color:red", "Connection lost!"
        lse_style, r_lse = "color:red", "Not allowed"
        sy_style, r_sy = "color:red", "Not allowed"

        if internet_on():
            net_style, net_response = "color:green", "OK"

        if access_server():
            net_style, net_response = "color:green", "Connected"
            if self.check_serv.data.get("backup_online"):
                sy_style, r_sy = "color:green", "Authorized"

        lse, valid = is_valide_mac()
        if lse:
            lse_style, r_lse = (
                "color:green",
                "<b>{lse.remaining_days()}</b>" if valid else "Expired",
            )

        self.info_label.setText(
            f"""
            <strong>Internet:</strong><span style={net_style}>{net_response}</span>
            <strong>Server:</strong><span style={net_style}>{net_response}</span><br>
            <strong>Synchronization:</strong><span style={sy_style}>{r_sy}</span>
            <strong>License:</strong><span style={lse_style}>{r_lse}</span>
            """
        )

        # self.check_serv_contact_server()


class TaskThreadDownload(QThread):
    download_finish_signal = pyqtSignal()

    def __init__(self, parent):
        QThread.__init__(self, parent)
        self.parent = parent

    def run(self):
        self.parent.download_setup_file()
        self.download_finish_signal.emit()


class TaskThreadServer(QThread):
    contact_server_signal = pyqtSignal()
    download_signal = pyqtSignal()

    def __init__(self, parent):
        QThread.__init__(self, parent)
        self.parent = parent
        self.stopped = parent.stopFlag

    def run(self):
        check_interval = 5
        from Common.models import Organization

        while not self.stopped.wait(check_interval):
            if Organization().select().count() > 0:
                orga_slug = Organization.get(id=1).slug
                if access_server():
                    logger.info("Server access is OK")
                    if not orga_slug:
                        Network().get_or_inscribe_app()
                    else:
                        self.data = Network().update_version_checker()
                        check_interval = 150
                        if not self.data:
                            return
                        if not self.data.get("is_last"):
                            self.download_signal.emit()
                else:
                    # logger.info("No server access")
                    pass

                self.contact_server_signal.emit()
