#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: fadiga

from datetime import datetime
from threading import Event

from PyQt5.QtCore import QObject, QThread, pyqtSignal

from .cstatic import CConstants, logger
from .models import Organization
from .server import Network
from .ui.util import access_server, is_valide_mac


class UpdaterInit(QObject):
    contact_server_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.stopFlag = Event()
        self.check = TaskThreadUpdater(self)
        self.check.contact_server_signal.connect(self.contact_server)

        try:
            self.check.start()
        except Exception as exc:
            logger.warning(
                "Exception occurred while starting the updater thread: {}".format(exc)
            )

    def contact_server(self):
        logger.info("Contacting server for updates")
        orga_slug = self.get_organization_slug()

        if orga_slug:
            self.check.update_data(orga_slug)

    def get_organization_slug(self):
        if Organization.select().count() > 0:
            return Organization.get(id=1).slug
        return None


class TaskThreadUpdater(QThread):
    contact_server_signal = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.stopped = parent.stopFlag

    def run(self):
        check_interval_without_server = 5
        check_interval_with_server = 50

        while not self.stopped.wait(check_interval_without_server):
            if access_server():
                orga_slug = self.get_organization_slug()

                if not orga_slug or orga_slug == "-":
                    Network().get_or_inscribe_app()
                else:
                    lcse = is_valide_mac()[0]
                    resp = Network().submit(
                        "check_org", {"orga_slug": orga_slug, "lcse": lcse.code}
                    )
                    if (
                        not resp.get("force_kill")
                        or resp.get("can_use") != CConstants.IS_EXPIRED
                    ):
                        lcse.expiration_date = datetime.fromtimestamp(
                            resp.get("expiration_date")
                        )
                        lcse.save()
                    else:
                        lcse.remove_activation()

                    if resp.get("is_syncro"):
                        self.contact_server_signal.emit()

                    check_interval_without_server = check_interval_with_server
            else:
                # logger.info("No server access")
                pass

    def get_organization_slug(self):
        return self.parent.get_organization_slug()

    def update_data(self, orga_slug):
        logger.info("Updating data")
        from .database import Setup

        self.contact_server_signal.emit()

        for m in Setup.LIST_CREAT:
            for d in m.select().where(m.is_syncro == True):
                resp = Network().submit(
                    "update-data",
                    {"slug": orga_slug, "model": type(d).__name__, "data": d.data()},
                )
                if resp.get("save"):
                    d.updated()
