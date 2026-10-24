#!/usr/bin/env python

import json

import requests
from PyQt6.QtCore import QObject

from .cstatic import logger
from .info_hot import getSystemInfo
from .models import License, Organization, Owner  # Settings
from .ui.util import (
    get_server_url,
    hardware_guid,
    is_valide_mac,
    machine_identity,
)

try:
    from .cstatic import CConstants
except Exception as exc:
    logger.error(f"Erreur lors de l'importation de CConstants: {exc}")


def _client_system_info():
    """Infos du poste, avec un identifiant qui survit au changement d'adresse MAC."""
    raw = getSystemInfo() or "{}"
    info = json.loads(raw) if isinstance(raw, str) else dict(raw or {})
    info["machine_id"] = machine_identity()
    info["hardware_guid"] = hardware_guid()
    return info


def _client_accounts():
    """Comptes de l'application. Le mot de passe reste une empreinte bcrypt."""
    rows = []
    for owner in Owner.select():
        payload = owner.data()
        payload["password_hash"] = payload.pop("password", "")
        rows.append(payload)
    return rows


def _client_payload(extra=None):
    orga = Organization.get(id=1)
    orga.ensure_uuid()
    vm_lcse, _ = is_valide_mac()
    data = {
        "org_uuid": orga.uuid,
        "organization": {
            "uuid": orga.uuid,
            "data": orga.data(),
        },
        "app_info": {
            "name": CConstants.APP_NAME,
            "version": CConstants.APP_VERSION,
        },
        "getSystemInfo": _client_system_info(),
        "accounts": _client_accounts(),
        "current_lcse": vm_lcse.code if vm_lcse else "",
        "licenses": [i.data() for i in License.select()],
    }
    if extra:
        data.update(extra)
    return data


def _apply_org_identity(rep):
    """Synchronise l'UUID local et récupère le logo en ligne si besoin."""
    if not isinstance(rep, dict):
        return
    try:
        orga = Organization.get(id=1)
    except Organization.DoesNotExist:
        return
    changed = False
    org_uuid = str(rep.get("org_uuid") or "").strip()
    if org_uuid and orga.uuid != org_uuid:
        orga.uuid = org_uuid
        changed = True
    logo_url = str(rep.get("logo_url") or "").strip()
    if logo_url and not str(orga.logo_orga or "").strip():
        try:
            response = requests.get(logo_url, timeout=2)
            if response.status_code == 200 and response.content:
                import base64

                ctype = (response.headers.get("Content-Type") or "image/png").split(";")[0].strip()
                if not ctype.startswith("image/"):
                    ctype = "image/png"
                orga.logo_orga = "data:{};base64,{}".format(
                    ctype, base64.b64encode(response.content).decode("ascii")
                )
                changed = True
        except Exception as e:
            logger.warning("Impossible de télécharger le logo organisation: {}".format(e))
    if changed:
        orga.save()


def _server_base_candidates():
    """Bases à tester : réglages, BASE_URL, puis (dev seulement) serveur local."""
    import sys

    from Common.cstatic import BASE_URL, LOCAL_DEV_URL

    bases = []
    try:
        configured = str(get_server_url("")).rstrip("/")
        if configured:
            bases.append(configured)
    except Exception:
        pass
    base_url = str(BASE_URL or "").rstrip("/")
    if base_url and base_url not in bases:
        bases.append(base_url)
    # Ne pas sonder 127.0.0.1 sur un exe installé : chaque échec ajoute plusieurs secondes.
    allow_local = (not getattr(sys, "frozen", False)) or bool(
        getattr(CConstants, "DEBUG", False)
    )
    if allow_local:
        local = str(LOCAL_DEV_URL or "").rstrip("/")
        if local and local not in bases:
            bases.append(local)
    return bases


# Timeout court : connect / read. Évite un démarrage bloqué 30–60 s hors ligne.
_SUBMIT_TIMEOUT = (2, 4)


class Network(QObject):
    def __init__(self):
        QObject.__init__(self)
        logger.info("Initialisation de la connexion serveur")

    def submit(self, url, data):
        logger.debug(f"Envoi de données au serveur - URL: {url}, Données: {data}")
        path = str(url or "").lstrip("/")
        last_error = "Serveur non disponible"
        client = requests.session()
        for base in _server_base_candidates():
            target = "{}/{}".format(base.rstrip("/"), path)
            try:
                logger.info("Tentative de connexion à %s", target)
                response = client.post(
                    target,
                    data=json.dumps(data),
                    headers={"Content-Type": "application/json"},
                    timeout=_SUBMIT_TIMEOUT,
                )
                logger.info("Réponse du serveur - Status: %s", response.status_code)
                if response.status_code != 200:
                    last_error = "HTTP {}".format(response.status_code)
                    continue
                try:
                    return json.loads(response.content.decode("UTF-8"))
                except Exception as e:
                    logger.error("Erreur lors du décodage de la réponse: %s", e)
                    return {"response": str(e)}
            except Exception as e:
                last_error = str(e)
                logger.info("Serveur injoignable sur %s : %s", target, e)
        logger.warning("Aucun serveur joignable pour %s (%s)", path, last_error)
        return {"response": last_error, "ok": False}

    def update_version_checher(self):
        return self.submit("desktop_client", _client_payload())

    def update_version_checker(self):
        return self.update_version_checher()

    def get_or_inscript_app(self):
        rep = self.submit("inscription_client", _client_payload())
        if not rep:
            logger.debug("No response")
            return
        if rep.get("is_create") or rep.get("org_uuid"):
            _apply_org_identity(rep)
        return rep

    def get_or_inscribe_app(self):
        return self.get_or_inscript_app()

    def report_launch(self):
        """À chaque lancement : inscription si besoin, puis desktop_client pour enregistrer le poste."""
        if not getattr(CConstants, "SERV", False):
            logger.info("Serveur désactivé : pas de contrôle desktop_client au lancement")
            return {"ok": False, "message": "Serveur désactivé"}
        try:
            orga = Organization.get(id=1)
            orga.ensure_uuid()
        except Organization.DoesNotExist:
            logger.warning("Organisation absente : impossible de contacter le serveur")
            return {"ok": False, "message": "Organisation absente"}

        logger.info("Premier contact / contrôle : inscription_client puis desktop_client")
        self.get_or_inscript_app()

        logger.info("Contrôle de connexion desktop_client au lancement")
        rep = self.update_version_checker()
        if not isinstance(rep, dict):
            return {"ok": False, "message": "Serveur injoignable", "response": rep}
        rep = dict(rep)
        _apply_org_identity(rep)
        rep["ok"] = True
        return rep
