#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

"""
Gestion centralisée des thèmes (clair, sombre, système) pour les applications
utilisant Common. Les applications (ex: G-Sady) appellent apply_theme() ou
délèguent à la fenêtre principale (set_theme) qui utilise ce module.
"""

THEME_LIGHT = "light"
THEME_DARK = "dark"
THEME_SYSTEM = "system"

THEME_NAMES = (THEME_LIGHT, THEME_DARK, THEME_SYSTEM)

# Stylesheet pour le thème sombre
THEME_DARK_STYLESHEET = """
    QMainWindow {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QToolBar {
        background-color: #2b2b2b;
        border: none;
        spacing: 6px;
    }
    QToolBar::separator {
        background-color: #555555;
        width: 1px;
        margin: 6px 4px;
    }
    QToolButton {
        background-color: transparent;
        color: #ffffff;
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 6px;
    }
    QToolButton:hover {
        background-color: #404040;
        border: 1px solid #555555;
    }
    QToolButton:pressed {
        background-color: #505050;
        border: 1px solid #666666;
    }
    QMenuBar {
        background-color: #3c3c3c;
        color: #ffffff;
    }
    QMenuBar::item:selected {
        background-color: #505050;
    }
    QMenu {
        background-color: #3c3c3c;
        color: #ffffff;
    }
    QMenu::item:selected {
        background-color: #505050;
    }
    QPushButton {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #505050;
    }
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
    }
    QTableWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        gridline-color: #555555;
    }
    QHeaderView::section {
        background-color: #3c3c3c;
        color: #ffffff;
        padding: 4px;
        border: 1px solid #555555;
    }
"""

def _dark_palette():
    """
    Palette Qt sombre cohérente.
    On la définit en plus du stylesheet pour que les QSS utilisant palette(...)
    et les widgets basés sur QPalette restent consistants.
    """
    from PyQt6.QtGui import QColor, QPalette

    p = QPalette()
    window = QColor("#2b2b2b")
    base = QColor("#303030")
    alt_base = QColor("#363636")
    text = QColor("#ffffff")
    disabled_text = QColor("#a0a0a0")
    mid = QColor("#555555")
    button = QColor("#404040")
    highlight = QColor("#2d7bdc")
    highlighted_text = QColor("#ffffff")

    p.setColor(QPalette.ColorRole.Window, window)
    p.setColor(QPalette.ColorRole.WindowText, text)
    p.setColor(QPalette.ColorRole.Base, base)
    p.setColor(QPalette.ColorRole.AlternateBase, alt_base)
    p.setColor(QPalette.ColorRole.Text, text)
    p.setColor(QPalette.ColorRole.Button, button)
    p.setColor(QPalette.ColorRole.ButtonText, text)
    p.setColor(QPalette.ColorRole.Mid, mid)
    p.setColor(QPalette.ColorRole.Highlight, highlight)
    p.setColor(QPalette.ColorRole.HighlightedText, highlighted_text)

    # Etats désactivés
    # Sur certaines builds PyQt6, les surcharges setColor(group, role, color) sont fragiles.
    # On passe via les enum Qt et on protège pour éviter un crash au démarrage.
    try:
        p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled_text)
        p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_text)
        p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_text)
    except Exception:
        # Fallback: au minimum garder une palette cohérente sans états disabled
        pass

    return p


def get_stylesheet(theme_name):
    """
    Retourne le stylesheet Qt correspondant au thème.

    Args:
        theme_name: "light", "dark" ou "system"

    Returns:
        str: Stylesheet à appliquer (chaîne vide pour light/system).
    """
    if theme_name == THEME_DARK:
        return THEME_DARK_STYLESHEET
    return ""


def apply_theme(app, theme_name, save_to_settings=True):
    """
    Applique le thème à l'application (QApplication).

    Args:
        app: Instance de QApplication (ex: QApplication.instance()).
        theme_name: "light", "dark" ou "system".
        save_to_settings: Si True, enregistre le thème dans Settings (id=1).
    """
    from PyQt6.QtWidgets import QApplication

    from ..cstatic import logger

    if app is None:
        return False
    if not theme_name or str(theme_name).strip().lower() in ("default",):
        theme_name = THEME_LIGHT
    elif theme_name not in THEME_NAMES:
        theme_name = THEME_LIGHT

    stylesheet = get_stylesheet(theme_name)
    app.setStyleSheet(stylesheet)

    # Palette: indispensable pour les styles qui utilisent palette(...)
    if theme_name == THEME_DARK:
        app.setPalette(_dark_palette())
    else:
        # Revenir à la palette par défaut du style courant (light / system)
        try:
            app.setPalette(QApplication.style().standardPalette())
        except Exception:
            pass
    if save_to_settings:
        try:
            from ..models import Settings, dbh

            if dbh is not None and dbh.is_closed():
                dbh.connect()
            sttg = Settings.get_or_none(Settings.id == 1)
            if sttg is None:
                sttg = Settings.init_settings()
            sttg.theme = theme_name
            sttg.save()
            logger.info("Thème enregistré dans Settings: %s", theme_name)
        except Exception as exc:
            logger.warning("Enregistrement du thème impossible: %s", exc)
    return True


def get_theme_display_name(theme_name):
    """Retourne un libellé affichable pour le thème."""
    names = {
        THEME_LIGHT: "Clair",
        THEME_DARK: "Sombre",
        THEME_SYSTEM: "Système",
    }
    return names.get(theme_name, theme_name.capitalize())
