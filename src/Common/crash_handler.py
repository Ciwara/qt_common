#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga

"""Affiche les erreurs fatales dans une popup au lieu de fermer l'application."""

import sys
import threading
import traceback

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMessageBox

from .cstatic import logger

_dialog_open = False
_hooks_installed = False
_error_bus = None


class _ErrorBus(QObject):
    failed = pyqtSignal(str, str, bool)

    def __init__(self):
        super().__init__()
        self.failed.connect(self._on_failed)

    def _on_failed(self, summary, details, continue_app):
        show_error_popup(
            summary, details, title="Erreur inattendue", continue_app=continue_app
        )


def _parent_window():
    try:
        from .ui.window import FWindow

        window = getattr(FWindow, "window", None)
        if window is not None:
            return window
    except Exception:
        pass
    app = QApplication.instance()
    if app is not None:
        return app.activeWindow()
    return None


def _format_exception(exc_type, exc, tb):
    if exc_type is None:
        return "Erreur inconnue", ""
    summary = str(exc).strip() or getattr(exc_type, "__name__", "Erreur")
    details = "".join(traceback.format_exception(exc_type, exc, tb))
    return summary, details


def show_error_popup(summary, details="", *, title="Erreur", continue_app=True):
    """Affiche une QMessageBox critique. Ne relance pas l'exception."""
    global _dialog_open

    app = QApplication.instance()
    if app is not None and app.closingDown():
        logger.error("%s\n%s", summary, details)
        return

    if _dialog_open:
        logger.error("Erreur supplémentaire pendant l'affichage d'une popup: %s", summary)
        return

    if app is None:
        app = QApplication(sys.argv)

    _dialog_open = True
    try:
        box = QMessageBox(_parent_window())
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle(title)
        if continue_app:
            box.setText(
                "Une erreur inattendue s'est produite.\n"
                "L'application n'a pas été fermée."
            )
        else:
            box.setText("L'application n'a pas pu continuer.")
        box.setInformativeText(summary)
        if details:
            box.setDetailedText(details)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()
    except Exception as popup_error:
        logger.error("Impossible d'afficher la popup d'erreur: %s", popup_error)
        logger.error("%s\n%s", summary, details)
        sys.stderr.write(f"{summary}\n{details}\n")
    finally:
        _dialog_open = False


def report_uncaught_exception(exc_info, *, continue_app=True):
    """Journalise une exception non gérée et l'affiche dans une popup."""
    exc_type, exc, tb = exc_info
    if exc_type is None or issubclass(exc_type, (KeyboardInterrupt, SystemExit, GeneratorExit)):
        return False

    summary, details = _format_exception(exc_type, exc, tb)
    logger.error("Erreur non gérée: %s\n%s", summary, details)

    app = QApplication.instance()
    if (
        _error_bus is not None
        and app is not None
        and threading.current_thread() is not threading.main_thread()
    ):
        _error_bus.failed.emit(summary, details, continue_app)
        return True

    show_error_popup(summary, details, title="Erreur inattendue", continue_app=continue_app)
    return True


def show_startup_error(message, details=""):
    """Erreur de démarrage : popup puis l'appelant quitte l'application."""
    logger.error("Erreur de démarrage: %s\n%s", message, details)
    show_error_popup(message, details, title="Erreur de démarrage", continue_app=False)


def _excepthook(exc_type, exc, tb):
    if not report_uncaught_exception((exc_type, exc, tb)):
        sys.__excepthook__(exc_type, exc, tb)


def _thread_excepthook(args):
    if not report_uncaught_exception((args.exc_type, args.exc_value, args.exc_traceback)):
        if sys.__excepthook__:
            sys.__excepthook__(args.exc_type, args.exc_value, args.exc_traceback)


def install_exception_hooks():
    """Installe les filets de sécurité pour les exceptions non gérées."""
    global _hooks_installed
    if _hooks_installed:
        return
    sys.excepthook = _excepthook
    threading.excepthook = _thread_excepthook
    _hooks_installed = True
    logger.debug("Gestionnaire d'exceptions (popup) installé")


class SafeApplication(QApplication):
    """QApplication qui intercepte les exceptions des slots Qt (évite l'abort)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global _error_bus
        if _error_bus is None:
            _error_bus = _ErrorBus()

    def notify(self, receiver, event):
        try:
            return super().notify(receiver, event)
        except Exception:
            report_uncaught_exception(sys.exc_info(), continue_app=True)
            return False
