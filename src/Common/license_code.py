#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Génération / validation des codes de licence Common (sans dépendance Qt).

Format : ``clé_machine:durée:signature``
- durée = nombre de jours ou ``INF`` (illimité)
- signature liée à la machine, la durée et le slug ``APP_NAME`` de l'appli
"""

from __future__ import annotations

import hashlib

LICENSE_CODE_SALT = "qt-common-lcse-v2"


def duration_token(days):
    """Jeton de durée embarqué dans le code : « INF » ou nombre de jours."""
    if days is None:
        return "INF"
    days = int(days)
    if days <= 0:
        return "INF"
    return str(days)


def code_signature(machine_hash, duration_token_value, app_slug):
    """Signature MD5 courte liée à machine + durée + slug d'application."""
    app = str(app_slug or "").strip() or "Common"
    payload = "%s:%s:%s:%s" % (
        machine_hash,
        duration_token_value,
        LICENSE_CODE_SALT,
        app,
    )
    return hashlib.md5(payload.encode("utf-8")).hexdigest()[:12]


def make_activation_code(machine_hash, days=None, app_slug="Common"):
    """Construit le code d'activation à coller dans l'appli cible.

    Parameters
    ----------
    machine_hash : str
        Clé machine affichée par l'appli (MD5).
    days : int | None
        Nombre de jours ; ``None`` ou ``<= 0`` → illimité (INF).
    app_slug : str
        ``APP_NAME`` exact de l'appli Common (ex. ``Business``, ``GGarage``).
    """
    machine_hash = str(machine_hash or "").strip()
    if not machine_hash:
        raise ValueError("Clé machine obligatoire")
    app_slug = str(app_slug or "").strip()
    if not app_slug:
        raise ValueError("Slug d'application (APP_NAME) obligatoire")
    token = duration_token(days)
    sig = code_signature(machine_hash, token, app_slug)
    return "%s:%s:%s" % (machine_hash, token, sig)


def parse_activation_code(raw, app_slug="Common"):
    """Valide un code et retourne ``(machine_hash, duration_days|None)``."""
    text = "".join((raw or "").strip().replace("|", ":").replace(";", ":").split())
    if not text:
        raise ValueError("Code de licence vide")

    parts = text.split(":")
    if len(parts) != 3:
        raise ValueError(
            "Le code de licence doit contenir la durée de validité "
            "(format : clé:jours:signature — ex. clé:365:… ou clé:INF:…)"
        )

    machine_hash, duration_raw, signature = parts[0], parts[1], parts[2].lower()
    duration_upper = duration_raw.upper()
    if duration_upper in ("INF", "INFINI", "INFINITE", "UNLIMITED", "0"):
        token = "INF"
        days = None
    elif duration_raw.isdigit():
        days = int(duration_raw)
        if days <= 0:
            token = "INF"
            days = None
        else:
            token = str(days)
    else:
        raise ValueError(
            "Durée invalide dans le code (attendu : nombre de jours ou INF)"
        )

    expected = code_signature(machine_hash, token, app_slug)
    if signature != expected:
        raise ValueError(
            "Code de licence invalide (durée, slug d'app ou signature incorrecte)"
        )
    return machine_hash, days
