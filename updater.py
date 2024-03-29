#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: fadiga

from PyQt4.QtCore import QThread, SIGNAL, QObject, Qt
import json

import requests
from datetime import datetime
from threading import Event
from Common.models import Settings, Organization, License
from Common.ui.util import get_serv_url, acces_server, is_valide_mac
from Common.cstatic import CConstants, logger

from server import Network


class UpdaterInit(QObject):
    def __init__(self):
        QObject.__init__(self)

        # self.status_bar = QStatusBar()
        self.stopFlag = Event()
        self.check = TaskThreadUpdater(self)
        self.connect(
            self.check, SIGNAL("update_data"), self.update_data, Qt.QueuedConnection
        )
        try:
            self.check.start()
        except Exception as exc:
            logger.warning("Exc :", exc)

    def update_data(self, orga_slug):
        logger.info("update data")
        from configuration import Config
        from database import Setup

        # self.base_url = Config.BASE_URL
        logger.info("UpdaterInit start")
        self.emit(SIGNAL("contact_server"))
        for m in Setup.LIST_CREAT:
            for d in m.select().where(m.is_syncro == True):
                # logger.info(type(d).__name__)
                resp = Network().submit(
                    "update-data",
                    {"slug": orga_slug, "model": type(d).__name__, "data": d.data()},
                )
                if resp.get("save"):
                    d.updated()


class TaskThreadUpdater(QThread):
    def __init__(self, parent):
        QThread.__init__(self, parent)
        self.parent = parent
        self.stopped = parent.stopFlag

    def run(self):
        # from Common.ui.statusbar import GStatusBar
        w = 5
        while not self.stopped.wait(w):
            w = 50
            if acces_server():
                if Organization().select().count() == 0:
                    return
                orga_slug = Organization.get(id=1).slug
                if not orga_slug or orga_slug == "-":
                    rep_serv = Network().get_or_inscript_app()
                else:
                    lcse = is_valide_mac()[0]
                    resp = Network().submit(
                        "check_org", {"orga_slug": orga_slug, "lcse": lcse.code}
                    )
                    if (
                        not resp.get("force_kill")
                        or resp.get("can_use") != CConstants.IS_EXPIRED
                    ):
                        # logger.info("resp expiration_date :: ", resp)
                        lcse.expiration_date = datetime.fromtimestamp(
                            resp.get("expiration_date")
                        )
                        lcse.save()
                    else:
                        # logger.info("remove_activation")
                        lcse.remove_activation()

                    if resp.get("is_syncro"):
                        self.parent.update_data(orga_slug)
