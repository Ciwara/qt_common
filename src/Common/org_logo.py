"""Décodage du logo organisation (fichier, data URL, base64). Partagé par exports PDF / XLSX."""

from __future__ import annotations

import base64
import os
import tempfile
from io import BytesIO
from pathlib import Path


def decode_org_logo_bytes(logo_field) -> bytes | None:
    """logo_orga : chemin fichier, data URL base64 ou chaîne base64."""
    if not logo_field:
        return None
    if isinstance(logo_field, (bytes, bytearray)):
        return bytes(logo_field)
    s = str(logo_field).strip()
    if not s:
        return None
    if s.startswith("data:") and "," in s:
        b64_part = "".join(s.split(",", 1)[1].split())
        try:
            return base64.b64decode(b64_part, validate=False)
        except Exception:
            return None
    try:
        if len(s) <= 8192:
            p = Path(s)
            if p.is_file():
                return p.read_bytes()
    except OSError:
        pass
    compact = "".join(s.split())
    try:
        return base64.b64decode(compact, validate=False)
    except Exception:
        return None


def image_suffix_from_bytes(raw: bytes) -> str:
    """Extension plausible pour un fichier image (xlsxwriter a besoin d’un chemin disque)."""
    if len(raw) >= 8 and raw[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if len(raw) >= 2 and raw[:2] == b"\xff\xd8":
        return ".jpg"
    if len(raw) >= 6 and raw[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return ".webp"
    return ".png"


def write_org_logo_temp_file(logo_field) -> str | None:
    """
    Écrit le logo sur disque (PNG via Pillow si possible, sinon octets bruts).
    L’appelant doit supprimer le fichier après usage (xlsxwriter lit le chemin).
    """
    raw = decode_org_logo_bytes(logo_field)
    if not raw:
        return None
    try:
        from PIL import Image

        pil = Image.open(BytesIO(raw))
        pil.load()
        fd, path = tempfile.mkstemp(suffix=".png", prefix="orglogo_")
        os.close(fd)
        pil.save(path, format="PNG")
        return path
    except Exception:
        pass
    suf = image_suffix_from_bytes(raw)
    try:
        fd, path = tempfile.mkstemp(suffix=suf, prefix="orglogo_")
        with os.fdopen(fd, "wb") as f:
            f.write(raw)
        return path
    except Exception:
        return None
