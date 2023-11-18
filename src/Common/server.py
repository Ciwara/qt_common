#!/usr/bin/env python

import json

import requests
from PyQt5.QtCore import QObject

from .cstatic import logger
from .info_hot import getSystemInfo
from .models import License, Organization, Owner, Settings, Version
from .ui.util import (
    acces_server,
    datetime_to_str,
    get_serv_url,
    internet_on,
    is_valide_mac,
)

try:
    from .cstatic import CConstants
except Exception as exc:
    print(exc)


class Network(QObject):
    def __init__(self):
        QObject.__init__(self)

        logger.info("Connexion serveur ...")

    def submit(self, url, data):
        logger.debug("submit", "data", " url ", url)
        resp_dict = {"response": {"message": "-"}}
        if acces_server():
            client = requests.session()
            try:
                response = client.get(get_serv_url(url), data=json.dumps(data))
                logger.info(response)
                if response.status_code == 200:
                    # logger.debug(response.status_code)
                    try:
                        return json.loads(response.content.decode("UTF-8"))
                    except Exception as e:
                        return {"response": e}
            except:
                return resp_dict.update({"response": "Serveur non disponible"})
        else:
            return resp_dict.update({"response": "Pas d'internet"})

    def update_version_checher(self):
        # logger.debug("update_version_checher")

        orga = Organization.get(id=1)
        data = {
            "org_slug": orga.slug,
            "app_info": {
                "name": CConstants.APP_NAME,
                "version": CConstants.APP_VERSION,
            },
            "getSystemInfo": json.loads(getSystemInfo()),
            "current_lcse": is_valide_mac()[0].code,
        }

        lcse_dic = []
        # if CConstants.LSE:
        for lcse in License.select():
            acttn_date = datetime_to_str(lcse.activation_date)
            lcse_dic.append(
                {
                    "code": lcse.code,
                    "isactivated": lcse.isactivated,
                    "activation_date": acttn_date,
                    "can_expired": lcse.can_expired,
                    "expiration_date": datetime_to_str(lcse.expiration_date)
                    if lcse.can_expired
                    else acttn_date,
                }
            )
        data.update({"licenses": lcse_dic})

        return self.submit("desktop_client", data)

    def get_or_inscript_app(self):
        orga = Organization.get(id=1)
        sttg = Settings.get(id=1)
        data = {
            "app_info": {
                "name": CConstants.APP_NAME,
                "version": CConstants.APP_VERSION,
            },
            "getSystemInfo": json.loads(getSystemInfo()),
            "organization": {"slug": orga.slug, "data": orga.data()},
            "licenses": [i.data() for i in License.all()],
        }

        rep = self.submit("inscription_client", data)
        if not rep:
            logger.debug("No response")
            return
        if rep.get("is_create"):
            orga.slug = rep.get("org_slug")
            orga.save()
        return rep
