#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: fadiga

import os
import re
import subprocess
import sys
import tempfile

import requests
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ..cstatic import logger
from ..server import Network
from .util import access_server, get_server_url, internet_on, is_valide_mac

try:
    from ..cstatic import CConstants
except Exception as e:
    print(e)


def _updates_dir():
    folder = os.path.join(tempfile.gettempdir(), "mpayment_updates")
    os.makedirs(folder, exist_ok=True)
    return folder


def _pending_meta_path():
    return os.path.join(_updates_dir(), "pending_update.json")


def _installer_destination(app_label, suggested_name=None):
    """Chemin local pour l'installateur (dossier temporaire dédié).

    Les setups Mpayment publiés sur le serveur sont des .exe Windows (NSIS) :
    on conserve toujours cette extension, même sous macOS/Linux.
    """
    raw = suggested_name or app_label or "setup"
    name = os.path.basename(str(raw).replace("\\", "/").strip()) or "setup"
    safe = re.sub(r"[^\w.\-]+", "_", name).strip("._") or "setup"
    root, ext = os.path.splitext(safe)
    if ext.lower() not in (".exe", ".msi", ".dmg", ".pkg"):
        safe = f"{root or 'setup'}.exe"
    return os.path.join(_updates_dir(), safe)


def _is_windows_pe(path):
    try:
        with open(path, "rb") as handle:
            return handle.read(2) == b"MZ"
    except Exception:
        return False


def _valid_installer(path):
    """Fichier d'install déjà téléchargé et utilisable (pas un téléchargement tronqué)."""
    if not path or not os.path.isfile(path):
        return False
    try:
        if os.path.getsize(path) < 100 * 1024:
            return False
    except OSError:
        return False
    lower = path.lower()
    if lower.endswith((".exe", ".msi", ".dmg", ".pkg")):
        return True
    return _is_windows_pe(path)


def _save_pending_update(version, path, app_label=None, setup_url=None):
    try:
        import json

        payload = {
            "version": str(version or "").strip(),
            "path": path,
            "app": app_label or "",
            "setup_file_url": setup_url or "",
        }
        with open(_pending_meta_path(), "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
    except Exception as exc:
        logger.debug("Impossible d'enregistrer le cache MAJ : %s", exc)


def _find_cached_installer(data):
    """Retrouve un installateur déjà téléchargé pour la version proposée."""
    import json

    version = str((data or {}).get("version") or "").strip()
    app_label = (data or {}).get("app") or "setup"
    setup_url = str((data or {}).get("setup_file_url") or "").strip()

    try:
        with open(_pending_meta_path(), encoding="utf-8") as handle:
            meta = json.load(handle)
    except Exception:
        meta = None

    if isinstance(meta, dict):
        meta_path = meta.get("path") or ""
        meta_ver = str(meta.get("version") or "").strip()
        meta_url = str(meta.get("setup_file_url") or "").strip()
        same_version = (not version) or meta_ver == version
        same_url = (not setup_url) or (not meta_url) or meta_url == setup_url
        if same_version and same_url and _valid_installer(meta_path):
            return meta_path

    candidates = [_installer_destination(app_label)]
    if version:
        candidates.append(_installer_destination(f"{app_label}-{version}"))
        candidates.append(_installer_destination(f"setup-{version}"))
    for path in candidates:
        if _valid_installer(path):
            return path

    # Dernier recours : .exe du dossier dont le nom contient la version
    try:
        for name in os.listdir(_updates_dir()):
            lower = name.lower()
            if not lower.endswith((".exe", ".msi")):
                continue
            if version and str(version) not in name and str(version).replace(".", "") not in name.replace(".", ""):
                continue
            path = os.path.join(_updates_dir(), name)
            if _valid_installer(path):
                return path
    except OSError:
        pass
    return None


def _launch_installer(path):
    """Lance l'installateur. Sur Windows, quitte l'app pour libérer les fichiers."""
    if not path or not os.path.isfile(path):
        raise FileNotFoundError(path)
    if sys.platform == "win32":
        os.startfile(path)  # noqa: S606
        sys.exit(0)
    # Les paquets serveur sont des installateurs Windows : inutilisables via open/xdg-open.
    if path.lower().endswith((".exe", ".msi")) or _is_windows_pe(path):
        raise RuntimeError(
            "Cet installateur est un fichier Windows (.exe). "
            "Copiez-le sur un PC Windows pour l'installer :\n{}".format(path)
        )
    if sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


class GStatusBar(QStatusBar):
    """Disponibilité, téléchargement et installation de mise à jour."""

    _CHECK_DELAY_MS = 2000
    _CHECK_INTERVAL_MS = 30 * 60 * 1000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.check_serv = None
        self._thread = None
        self._download = None
        self._data = {}
        self._installer_path = ""
        self._phase = "idle"  # idle | available | downloading | ready

        self._info = QLabel("")
        self._info.hide()
        self.addWidget(self._info, 1)

        self._progress = QProgressBar(self)
        self._progress.setMaximumWidth(180)
        self._progress.setMaximumHeight(16)
        self._progress.hide()
        self.addPermanentWidget(self._progress)

        self._action_btn = QPushButton(self)
        self._action_btn.hide()
        self._action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._action_btn.setStyleSheet(
            "QPushButton { color: #b35900; font-weight: 700; padding: 2px 10px; }"
            "QPushButton:hover { color: #8a4200; }"
            "QPushButton:disabled { color: #999; }"
        )
        self._action_btn.clicked.connect(self._on_action)
        self.addPermanentWidget(self._action_btn)
        self.hide()

        self._timer = QTimer(self)
        self._timer.setInterval(self._CHECK_INTERVAL_MS)
        self._timer.timeout.connect(self.refresh)

        if getattr(CConstants, "SERV", False):
            QTimer.singleShot(self._CHECK_DELAY_MS, self.refresh)
            self._timer.start()

    def cleanup(self):
        try:
            self._timer.stop()
        except Exception:
            pass
        for thread in (self._thread, self._download):
            if thread is None:
                continue
            try:
                if thread.isRunning():
                    thread.quit()
                    thread.wait(800)
            except RuntimeError:
                pass
        self._thread = None
        self._download = None

    def set_context(self, context=None):
        return

    def refresh(self):
        if self._phase in ("downloading", "ready"):
            return
        if not getattr(CConstants, "SERV", False):
            self._clear_update_notice()
            return
        if _is_thread_running(self._thread):
            return
        self._thread = _CallThread(check_app_update, parent=self)
        self._thread.done.connect(self._apply_update_status)
        self._thread.finished.connect(self._clear_thread)
        self._thread.start()

    def _clear_thread(self):
        self._thread = None

    def _clear_download(self):
        self._download = None

    def _clear_update_notice(self):
        self._data = {}
        self._installer_path = ""
        self._phase = "idle"
        self._action_btn.hide()
        self._action_btn.setEnabled(True)
        self._action_btn.setText("")
        self._progress.hide()
        self._progress.setValue(0)
        self._info.hide()
        self._info.setText("")
        self.hide()

    def _apply_update_status(self, result):
        try:
            if self._phase in ("downloading", "ready"):
                return
            if not isinstance(result, dict) or not result.get("ok"):
                self._clear_update_notice()
                return
            data = result.get("data") or {}
            self._data = data
            if data.get("is_last", True):
                self._clear_update_notice()
                return
            if not data.get("setup_file_url"):
                self._clear_update_notice()
                return
            version = data.get("version") or ""
            cached = _find_cached_installer(data)
            if cached:
                self._show_ready(cached, version, already_downloaded=True)
                return
            self._phase = "available"
            self._action_btn.setText(
                f"⬆ Télécharger la mise à jour {version}".strip()
                if version
                else "⬆ Télécharger la mise à jour"
            )
            self._action_btn.setToolTip(
                data.get("message") or "Télécharger et installer la nouvelle version"
            )
            self._action_btn.setEnabled(True)
            self._action_btn.show()
            self._progress.hide()
            self._info.hide()
            self.show()
        except RuntimeError:
            return

    def _show_ready(self, path, version="", already_downloaded=False):
        self._installer_path = path
        self._phase = "ready"
        self._progress.hide()
        self._action_btn.setText(
            f"Installer la version {version}".strip()
            if version
            else "Installer la mise à jour"
        )
        self._action_btn.setEnabled(True)
        self._action_btn.show()
        if already_downloaded:
            self._info.setText("Mise à jour déjà téléchargée — prête à installer.")
        else:
            self._info.setText("Téléchargement terminé — prêt à installer.")
        self._info.show()
        self.show()

    def _on_action(self):
        if self._phase == "available":
            self._start_download()
        elif self._phase == "ready":
            self._start_install()

    def _start_download(self):
        if _is_thread_running(self._download):
            return
        cached = _find_cached_installer(self._data)
        if cached:
            self._show_ready(
                cached, self._data.get("version") or "", already_downloaded=True
            )
            return
        url_path = self._data.get("setup_file_url")
        if not url_path:
            self._info.setText("Aucun fichier d'installation n'est proposé.")
            self._info.show()
            return
        try:
            url = get_server_url(url_path)
        except Exception:
            self._info.setText("Adresse du serveur indisponible.")
            self._info.show()
            return
        self._installer_path = _installer_destination(self._data.get("app") or "setup")
        self._phase = "downloading"
        self._action_btn.setEnabled(False)
        self._action_btn.setText("Téléchargement…")
        self._progress.setValue(0)
        self._progress.show()
        self._info.setText("Téléchargement de la mise à jour en cours…")
        self._info.show()
        self.show()
        self._download = _DownloadThread(url, self._installer_path, parent=self)
        self._download.progress.connect(self._progress.setValue)
        self._download.finished_ok.connect(self._download_done)
        self._download.failed.connect(self._download_failed)
        self._download.finished.connect(self._clear_download)
        self._download.start()

    def _download_done(self, path):
        try:
            self._progress.setValue(100)
            version = self._data.get("version") or ""
            _save_pending_update(
                version,
                path,
                app_label=self._data.get("app"),
                setup_url=self._data.get("setup_file_url"),
            )
            self._show_ready(path, version, already_downloaded=False)
        except RuntimeError:
            return

    def _download_failed(self, message):
        try:
            self._phase = "available"
            self._progress.hide()
            self._action_btn.setEnabled(True)
            version = self._data.get("version") or ""
            self._action_btn.setText(
                f"⬆ Télécharger la mise à jour {version}".strip()
                if version
                else "⬆ Télécharger la mise à jour"
            )
            self._info.setText(message or "Le téléchargement a échoué.")
            self._info.show()
            self.show()
        except RuntimeError:
            return

    def _start_install(self):
        path = self._installer_path
        if not path or not os.path.isfile(path):
            self._info.setText("Le fichier d'installation est introuvable.")
            self._info.show()
            self._phase = "available"
            return
        try:
            self._info.setText("Lancement de l'installation…")
            self._info.show()
            _launch_installer(path)
            if sys.platform != "win32":
                self._info.setText(
                    "Installateur ouvert. Fermez l'application pour terminer la mise à jour."
                )
        except RuntimeError as exc:
            self._info.setText(str(exc))
            self._info.show()
            # Révéler le fichier dans le Finder / explorateur pour transfert Windows
            try:
                if sys.platform == "darwin":
                    subprocess.Popen(["open", "-R", path])
                elif sys.platform.startswith("linux"):
                    subprocess.Popen(["xdg-open", os.path.dirname(path)])
            except Exception:
                pass
        except Exception:
            logger.error("Lancement de l'installation impossible", exc_info=True)
            self._info.setText("Impossible de lancer l'installation.")
            self._info.show()


def _status_color(ok):
    return "#1e7e34" if ok else "#c0392b"


def _set_status(label, text, ok=None):
    label.setText(text)
    if ok is None:
        label.setStyleSheet("color: #6c757d; font-weight: 600;")
    else:
        label.setStyleSheet(f"color: {_status_color(ok)}; font-weight: 600;")


def collect_connection_status():
    """État Internet, serveur, synchronisation et licence."""
    internet = False
    server = False
    sync_ok = False
    license_text = "Inconnue"
    license_ok = None
    server_note = "Injoignable"

    try:
        internet = bool(internet_on())
    except Exception:
        internet = False

    try:
        if not CConstants.SERV:
            server_note = "Non activé"
        elif access_server():
            server = True
            server_note = "Connecté"
            data = Network().update_version_checker() or {}
            sync_ok = bool(data.get("backup_online"))
        else:
            server_note = "Injoignable"
    except Exception as exc:
        logger.debug("Statut serveur indisponible : %s", exc)
        server = False
        server_note = "Injoignable"

    try:
        license_row, valid = is_valide_mac()
        if license_row:
            if valid:
                license_text = str(license_row.remaining_days())
                license_ok = True
            else:
                license_text = "Expirée"
                license_ok = False
        elif valid == CConstants.OK:
            license_text = "Non requise"
            license_ok = None
        else:
            license_text = "Non activée"
            license_ok = False
    except Exception as exc:
        logger.debug("Statut licence indisponible : %s", exc)

    return {
        "internet": internet,
        "server": server,
        "server_note": server_note,
        "sync_ok": sync_ok,
        "license_text": license_text,
        "license_ok": license_ok,
    }


def check_app_update():
    """Interroge le serveur pour savoir si une version plus récente existe."""
    if not getattr(CConstants, "SERV", False):
        return {"ok": False, "message": "Le serveur n'est pas activé."}
    try:
        if not access_server():
            return {"ok": False, "message": "Serveur injoignable."}
        data = Network().update_version_checker() or {}
    except Exception as exc:
        logger.info("Vérification de mise à jour impossible : %s", exc)
        return {"ok": False, "message": "Serveur injoignable."}
    if not data:
        return {"ok": False, "message": "Aucune réponse du serveur."}
    return {"ok": True, "data": data}


def _is_thread_running(thread):
    if thread is None:
        return False
    try:
        return thread.isRunning()
    except RuntimeError:
        return False


class _CallThread(QThread):
    done = pyqtSignal(object)

    def __init__(self, func, parent=None):
        super().__init__(parent)
        self._func = func

    def run(self):
        try:
            self.done.emit(self._func())
        except Exception as exc:
            self.done.emit({"ok": False, "message": str(exc)})


class ConnectionStatusWidget(QWidget):
    """Internet, serveur et synchronisation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
        self._started = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        intro = QLabel(
            "État de la connexion, du serveur et de la synchronisation."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        form_host = QWidget(self)
        form = QFormLayout(form_host)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.internet_label = QLabel("—")
        self.server_label = QLabel("—")
        self.sync_label = QLabel("—")
        form.addRow("Internet :", self.internet_label)
        form.addRow("Serveur :", self.server_label)
        form.addRow("Synchronisation :", self.sync_label)
        layout.addWidget(form_host)

        actions = QHBoxLayout()
        actions.addStretch(1)
        self.refresh_button = QPushButton("Rafraîchir")
        self.refresh_button.clicked.connect(self.refresh_status)
        actions.addWidget(self.refresh_button)
        layout.addLayout(actions)
        layout.addStretch(1)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._started:
            self._started = True
            self.refresh_status()

    def refresh_status(self):
        if _is_thread_running(self._thread):
            return
        self.refresh_button.setEnabled(False)
        _set_status(self.internet_label, "Vérification…", None)
        _set_status(self.server_label, "Vérification…", None)
        _set_status(self.sync_label, "Vérification…", None)
        self._thread = _CallThread(collect_connection_status, parent=self)
        self._thread.done.connect(self._apply_status)
        self._thread.finished.connect(self._clear_thread)
        self._thread.start()

    def _clear_thread(self):
        self._thread = None

    def _apply_status(self, status):
        try:
            self.refresh_button.setEnabled(True)
            if not isinstance(status, dict) or "internet" not in status:
                _set_status(self.server_label, "Indisponible", False)
                return
            _set_status(
                self.internet_label,
                "Connecté" if status["internet"] else "Hors ligne",
                status["internet"],
            )
            server_ok = True if status["server"] else None if status["server_note"] == "Non activé" else False
            _set_status(self.server_label, status["server_note"], server_ok)
            if status["server"]:
                _set_status(
                    self.sync_label,
                    "Autorisée" if status["sync_ok"] else "Non autorisée",
                    status["sync_ok"],
                )
            else:
                _set_status(self.sync_label, "—", None)
        except RuntimeError:
            return


def _filename_from_content_disposition(header):
    if not header:
        return None
    match = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', header, re.I)
    if not match:
        return None
    return os.path.basename(match.group(1).strip().strip('"'))


class _DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished_ok = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, url, dest, parent=None):
        super().__init__(parent)
        self._url = url
        self._dest = dest

    def run(self):
        try:
            # connect=15s, read=None : gros installateurs (dizaines de Mo)
            response = requests.get(self._url, stream=True, timeout=(15, None))
            if response.status_code != 200:
                self.failed.emit(f"Téléchargement refusé ({response.status_code}).")
                return
            remote_name = _filename_from_content_disposition(
                response.headers.get("Content-Disposition")
            )
            if remote_name:
                self._dest = _installer_destination(remote_name, suggested_name=remote_name)
            total = response.headers.get("content-length")
            downloaded = 0
            parent = os.path.dirname(self._dest)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(self._dest, "wb") as handle:
                if not total:
                    handle.write(response.content)
                    self.progress.emit(100)
                else:
                    total_n = int(total)
                    for chunk in response.iter_content(chunk_size=64 * 1024):
                        if not chunk:
                            continue
                        handle.write(chunk)
                        downloaded += len(chunk)
                        self.progress.emit(min(100, int(100 * downloaded / total_n)))
            if not os.path.isfile(self._dest) or os.path.getsize(self._dest) == 0:
                self.failed.emit("Le fichier téléchargé est vide.")
                return
            self.finished_ok.emit(self._dest)
        except Exception as exc:
            logger.error("Téléchargement de mise à jour : %s", exc)
            self.failed.emit("Le téléchargement a échoué.")


class AppUpdateWidget(QWidget):
    """Vérification, téléchargement et lancement d'une mise à jour."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
        self._download = None
        self._data = {}
        self._installer_path = ""
        self._started = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Mise à jour")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(title)

        version = getattr(CConstants, "APP_VERSION", "")
        self.current_label = QLabel(f"Version installée : {version}")
        layout.addWidget(self.current_label)

        self.message = QLabel("Vérifiez si une nouvelle version est disponible.")
        self.message.setWordWrap(True)
        layout.addWidget(self.message)

        self.check_button = QPushButton("Vérifier les mises à jour")
        self.check_button.clicked.connect(self.check_update)
        layout.addWidget(self.check_button, 0, Qt.AlignmentFlag.AlignLeft)

        self.download_button = QPushButton("Télécharger")
        self.download_button.hide()
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button, 0, Qt.AlignmentFlag.AlignLeft)

        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)

        self.install_button = QPushButton("Installer")
        self.install_button.hide()
        self.install_button.clicked.connect(self.start_install)
        layout.addWidget(self.install_button, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._started:
            self._started = True
            self.check_update()

    def check_update(self):
        if _is_thread_running(self._thread):
            return
        self.check_button.setEnabled(False)
        self.download_button.hide()
        self.install_button.hide()
        self.progress.hide()
        self.message.setText("Vérification en cours…")
        self._thread = _CallThread(check_app_update, parent=self)
        self._thread.done.connect(self._apply_update)
        self._thread.finished.connect(self._clear_thread)
        self._thread.start()

    def _clear_thread(self):
        self._thread = None

    def _clear_download(self):
        self._download = None

    def _apply_update(self, result):
        try:
            self.check_button.setEnabled(True)
            if not isinstance(result, dict) or not result.get("ok"):
                self.message.setText((result or {}).get("message") or "Serveur injoignable.")
                return
            data = result.get("data") or {}
            self._data = data
            if data.get("is_last", True):
                version = data.get("version") or getattr(CConstants, "APP_VERSION", "")
                self.message.setText(f"Vous avez la dernière version ({version}).")
                return
            self.message.setText(data.get("message") or "Une mise à jour est disponible.")
            if not data.get("setup_file_url"):
                self.message.setText(
                    (data.get("message") or "Mise à jour signalée")
                    + " — aucun installateur n'est publié sur le serveur."
                )
                return
            cached = _find_cached_installer(data)
            if cached:
                self._show_ready(cached, already_downloaded=True)
                return
            self.download_button.setEnabled(True)
            self.download_button.show()
        except RuntimeError:
            return

    def _show_ready(self, path, already_downloaded=False):
        self._installer_path = path
        self.download_button.hide()
        self.progress.hide()
        self.install_button.show()
        if already_downloaded:
            self.message.setText(
                f"Mise à jour déjà téléchargée — prête à installer.\n{path}"
            )
        else:
            self.message.setText(f"Téléchargement terminé : {path}")

    def start_download(self):
        if _is_thread_running(self._download):
            return
        cached = _find_cached_installer(self._data)
        if cached:
            self._show_ready(cached, already_downloaded=True)
            return
        url_path = self._data.get("setup_file_url")
        if not url_path:
            self.message.setText("Aucun fichier d'installation n'est proposé.")
            return
        try:
            url = get_server_url(url_path)
        except Exception:
            self.message.setText("Adresse du serveur indisponible.")
            return
        self._installer_path = _installer_destination(self._data.get("app") or "setup")
        self.download_button.setEnabled(False)
        self.install_button.hide()
        self.progress.setValue(0)
        self.progress.show()
        self.message.setText("Téléchargement en cours…")
        self._download = _DownloadThread(url, self._installer_path, parent=self)
        self._download.progress.connect(self.progress.setValue)
        self._download.finished_ok.connect(self._download_done)
        self._download.failed.connect(self._download_failed)
        self._download.finished.connect(self._clear_download)
        self._download.start()

    def _download_done(self, path):
        try:
            self.progress.setValue(100)
            _save_pending_update(
                self._data.get("version"),
                path,
                app_label=self._data.get("app"),
                setup_url=self._data.get("setup_file_url"),
            )
            self._show_ready(path, already_downloaded=False)
        except RuntimeError:
            return

    def _download_failed(self, message):
        try:
            self.download_button.setEnabled(True)
            self.progress.hide()
            self.message.setText(message)
        except RuntimeError:
            return

    def start_install(self):
        path = self._installer_path
        if not path or not os.path.isfile(path):
            self.message.setText("Le fichier d'installation est introuvable.")
            return
        try:
            self.message.setText("Lancement de l'installation…")
            _launch_installer(path)
            if sys.platform != "win32":
                self.message.setText(
                    "Le fichier d'installation a été ouvert. "
                    "Fermez l'application pour terminer la mise à jour."
                )
        except RuntimeError as exc:
            self.message.setText(str(exc))
            try:
                if sys.platform == "darwin":
                    subprocess.Popen(["open", "-R", path])
            except Exception:
                pass
        except Exception:
            logger.error("Lancement de l'installation impossible", exc_info=True)
            self.message.setText("Impossible de lancer l'installation.")
