#!/usr/bin/env python

import json

import requests
from PyQt6.QtCore import QObject

from .cstatic import logger
from .info_hot import getSystemInfo
from .models import License, Organization, Owner  # Settings
from .ui.util import (
    hardware_guid,
    is_valide_mac,
    machine_identity,
)

try:
    from .cstatic import CConstants
except Exception as exc:
    logger.error(f"Erreur lors de l'importation de CConstants: {exc}")

# Une seule tentative d'inscription par session applicative
_INSCRIPTION_TRIED = False


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


def _organization_payload_data(orga):
    """Données org pour le serveur — phone/logo sûrs (évite HTTP 500 côté web)."""
    org_data = dict(orga.data() or {})
    logo = str(org_data.get("logo_orga") or "")
    # Les logos « data:image/...;base64,... » font échouer l'écriture fichier
    # sur le serveur (HTTP 500 PermissionError) → inscription impossible.
    if logo.startswith("data:") or len(logo) > 4000:
        org_data["logo_orga"] = None
    # Organization.phone serveur = IntegerField : "" provoque ValueError 500
    phone = org_data.get("phone")
    if phone in ("", False) or phone is None:
        org_data["phone"] = None
    else:
        try:
            org_data["phone"] = int(
                "".join(ch for ch in str(phone) if ch.isdigit()) or 0
            ) or None
        except (TypeError, ValueError):
            org_data["phone"] = None
    return org_data


def _client_payload(extra=None):
    orga = Organization.get(id=1)
    orga.ensure_uuid()
    vm_lcse, _ = is_valide_mac()
    data = {
        "org_uuid": orga.uuid,
        "organization": {
            "uuid": orga.uuid,
            "data": _organization_payload_data(orga),
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


# Timeout court : connect / read. Évite un démarrage bloqué 30–60 s hors ligne.
_SUBMIT_TIMEOUT = (2, 4)


class Network(QObject):
    def __init__(self):
        QObject.__init__(self)
        logger.info("Initialisation de la connexion serveur")

    def submit(self, url, data):
        logger.debug(f"Envoi de données au serveur - URL: {url}, Données: {data}")
        from .ui.util import resolve_server_base_url

        path = str(url or "").lstrip("/")
        base = resolve_server_base_url()
        target = "{}/{}".format(base.rstrip("/"), path)
        try:
            logger.info("Tentative de connexion à %s", target)
            response = requests.session().post(
                target,
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
                timeout=_SUBMIT_TIMEOUT,
            )
            logger.info("Réponse du serveur - Status: %s", response.status_code)
            if response.status_code != 200:
                return {"response": "HTTP {}".format(response.status_code), "ok": False}
            try:
                return json.loads(response.content.decode("UTF-8"))
            except Exception as e:
                logger.error("Erreur lors du décodage de la réponse: %s", e)
                return {"response": str(e), "ok": False}
        except Exception as e:
            logger.warning("Serveur injoignable sur %s : %s", target, e)
            return {"response": str(e), "ok": False}

    def update_version_checher(self):
        return self.submit("desktop_client", _client_payload())

    def update_version_checker(self):
        return self.update_version_checher()

    @staticmethod
    def _registration_ok(rep):
        """True si le serveur a bien enregistré le poste / l'organisation."""
        if not isinstance(rep, dict) or rep.get("ok") is False:
            return False
        if rep.get("host_id") or rep.get("org_uuid") or rep.get("is_create"):
            return True
        if str(rep.get("response") or "").upper() == "OK":
            return True
        if str(rep.get("status") or "").upper() == "OK":
            return True
        return False

    def _apply_inscription_license(self, rep):
        """Applique le code d'évaluation / licence renvoyé par inscription_client."""
        if not isinstance(rep, dict):
            return
        code = rep.get("code")
        if not (code and (rep.get("found") or rep.get("can_use") == getattr(CConstants, "OK", "ok"))):
            return
        try:
            from .ui.util import apply_signed_license, make_lcse

            apply_signed_license(
                code,
                str(make_lcse()),
                getattr(CConstants, "APP_NAME", "") or "",
                evaluation=bool(rep.get("evaluation")),
            )
            logger.info("Licence issue de l'inscription appliquée localement")
        except Exception as exc:
            logger.warning("Licence inscription non appliquée: %s", exc)

    def get_or_inscript_app(self):
        rep = self.submit("inscription_client", _client_payload())
        if not rep:
            logger.debug("No response")
            return {"ok": False, "message": "Pas de réponse inscription"}
        if not isinstance(rep, dict):
            return {"ok": False, "message": "Réponse inscription illisible", "response": rep}
        rep = dict(rep)
        if self._registration_ok(rep):
            _apply_org_identity(rep)
            self._apply_inscription_license(rep)
            rep["ok"] = True
        else:
            rep["ok"] = False
        return rep

    def get_or_inscribe_app(self):
        return self.get_or_inscript_app()

    def _has_local_license(self):
        """True si une licence locale valide existe déjà (pas d'envoi inutile)."""
        try:
            _lcse, status = is_valide_mac()
            return status == getattr(CConstants, "OK", "ok")
        except Exception:
            return False

    def ensure_registered(self, max_attempts=1):
        """Inscrit une seule fois si pas encore syncro / pas de licence locale."""
        global _INSCRIPTION_TRIED
        if not getattr(CConstants, "SERV", False):
            return {"ok": False, "message": "Serveur désactivé"}
        try:
            orga = Organization.get(id=1)
            orga.ensure_uuid()
        except Organization.DoesNotExist:
            return {"ok": False, "message": "Organisation absente"}

        if orga.is_syncro and self._has_local_license():
            logger.info("Licence locale OK et déjà inscrit — pas d'envoi inscription_client")
            return {"ok": True, "skipped": True, "message": "Déjà inscrit"}

        if _INSCRIPTION_TRIED:
            logger.info("Inscription déjà tentée cette session — pas de nouvel envoi")
            return {
                "ok": bool(orga.is_syncro),
                "skipped": True,
                "message": "Inscription déjà tentée",
            }

        _INSCRIPTION_TRIED = True
        logger.info("Inscription serveur (une seule fois)")
        last = self.get_or_inscript_app()
        if self._registration_ok(last):
            try:
                orga.updated()
            except Exception:
                orga.is_syncro = True
                orga.save()
            logger.info(
                "Application enregistrée sur le serveur (host_id=%s)",
                last.get("host_id"),
            )
            return last
        logger.warning(
            "Inscription échouée: %s",
            (last or {}).get("message") or (last or {}).get("response") or last,
        )
        return last or {"ok": False, "message": "Inscription impossible"}

    def report_launch(self):
        """À chaque lancement : inscription seulement si besoin, puis 1× desktop_client."""
        if not getattr(CConstants, "SERV", False):
            logger.info("Serveur désactivé : pas de contrôle desktop_client au lancement")
            return {"ok": False, "message": "Serveur désactivé"}
        try:
            orga = Organization.get(id=1)
            orga.ensure_uuid()
        except Organization.DoesNotExist:
            logger.warning("Organisation absente : impossible de contacter le serveur")
            return {"ok": False, "message": "Organisation absente"}

        inscript = self.ensure_registered()

        logger.info("Contrôle de connexion desktop_client au lancement")
        rep = self.update_version_checker()
        if not isinstance(rep, dict):
            if self._registration_ok(inscript) or inscript.get("skipped"):
                out = dict(inscript)
                out["ok"] = True
                out["message"] = out.get("message") or "Inscrit (desktop_client injoignable)"
                return out
            return {"ok": False, "message": "Serveur injoignable", "response": rep}
        rep = dict(rep)
        _apply_org_identity(rep)
        if self._registration_ok(rep):
            try:
                orga.updated()
            except Exception:
                orga.is_syncro = True
                orga.save()
            self._apply_inscription_license(rep)
        rep["ok"] = bool(
            self._registration_ok(rep)
            or self._registration_ok(inscript)
            or inscript.get("skipped")
        )
        if not rep.get("message") and isinstance(inscript, dict):
            rep["message"] = inscript.get("message") or "OK"
        return rep
