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
    /* Base */
    QMainWindow, QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        selection-background-color: #2d7bdc;
        selection-color: #ffffff;
    }

    /* Toolbars + buttons */
    QToolBar {
        background-color: #2b2b2b;
        border: none;
        spacing: 6px;
    }
    QToolBar::separator {
        background-color: #4b4b4b;
        width: 1px;
        margin: 6px 4px;
    }
    QToolButton {
        background-color: transparent;
        color: #ffffff;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 6px 8px;
    }
    QToolButton:hover {
        background-color: #3a3a3a;
        border-color: #555555;
    }
    QToolButton:pressed {
        background-color: #454545;
        border-color: #666666;
    }

    /* Menus */
    QMenuBar {
        background-color: #2f2f2f;
        color: #ffffff;
        border-bottom: 1px solid #3d3d3d;
    }
    QMenuBar::item {
        padding: 6px 10px;
        background: transparent;
    }
    QMenuBar::item:selected {
        background-color: #3a3a3a;
        border-radius: 6px;
    }
    QMenu {
        background-color: #2f2f2f;
        color: #ffffff;
        border: 1px solid #3d3d3d;
        padding: 6px;
    }
    QMenu::item {
        padding: 6px 10px;
        border-radius: 6px;
    }
    QMenu::item:selected {
        background-color: #3a3a3a;
    }
    QMenu::separator {
        height: 1px;
        background-color: #3d3d3d;
        margin: 6px 6px;
    }

    /* Inputs */
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QDateTimeEdit, QComboBox {
        background-color: #303030;
        color: #ffffff;
        border: 1px solid #4f4f4f;
        border-radius: 8px;
        padding: 8px 10px;
    }
    QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QDateTimeEdit:hover, QComboBox:hover {
        border-color: #6a6a6a;
    }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateTimeEdit:focus, QComboBox:focus {
        border: 2px solid #2d7bdc;
        padding: 7px 9px;
    }
    QComboBox::drop-down { border: none; width: 28px; }
    QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #ffffff; margin-right: 8px; }

    /* Buttons */
    QPushButton {
        background-color: #3a3a3a;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 8px;
        padding: 8px 12px;
    }
    QPushButton:hover { background-color: #454545; }
    QPushButton:pressed { background-color: #4f4f4f; }
    QPushButton:disabled {
        background-color: #2f2f2f;
        color: #a0a0a0;
        border-color: #3d3d3d;
    }

    /* Tables / lists */
    QTableView, QTableWidget, QListView, QTreeView {
        background-color: #2b2b2b;
        alternate-background-color: #303030;
        color: #ffffff;
        gridline-color: #3d3d3d;
        border: 1px solid #3d3d3d;
        border-radius: 8px;
    }
    QHeaderView::section {
        background-color: #2f2f2f;
        color: #ffffff;
        padding: 6px;
        border: 1px solid #3d3d3d;
    }

    /* Tooltips */
    QToolTip {
        background-color: #1f1f1f;
        color: #ffffff;
        border: 1px solid #3d3d3d;
        padding: 6px;
        border-radius: 6px;
    }

    /* Scrollbars */
    QScrollBar:vertical {
        background: transparent;
        width: 12px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #4a4a4a;
        min-height: 28px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover { background: #5a5a5a; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    QScrollBar:horizontal {
        background: transparent;
        height: 12px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background: #4a4a4a;
        min-width: 28px;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal:hover { background: #5a5a5a; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
"""

def _dark_palette():
    """
    Palette Qt sombre cohérente.
    On la définit en plus du stylesheet pour que les QSS utilisant palette(...)
    et les widgets basés sur QPalette restent consistants.
    """
    from PyQt6.QtGui import QColor, QPalette

    p = QPalette()
    # Couleurs “source of truth” du thème sombre
    window = QColor("#2b2b2b")
    base = QColor("#303030")
    alt_base = QColor("#363636")
    text = QColor("#ffffff")
    disabled_text = QColor("#a0a0a0")
    placeholder_text = QColor("#9a9a9a")
    mid = QColor("#555555")
    midlight = QColor("#3d3d3d")
    button = QColor("#3a3a3a")
    highlight = QColor("#2d7bdc")
    link = QColor("#5aa7ff")
    tooltip_base = QColor("#1f1f1f")
    highlighted_text = QColor("#ffffff")

    p.setColor(QPalette.ColorRole.Window, window)
    p.setColor(QPalette.ColorRole.WindowText, text)
    p.setColor(QPalette.ColorRole.Base, base)
    p.setColor(QPalette.ColorRole.AlternateBase, alt_base)
    p.setColor(QPalette.ColorRole.Text, text)
    p.setColor(QPalette.ColorRole.Button, button)
    p.setColor(QPalette.ColorRole.ButtonText, text)
    p.setColor(QPalette.ColorRole.Mid, mid)
    p.setColor(QPalette.ColorRole.Midlight, midlight)
    p.setColor(QPalette.ColorRole.Highlight, highlight)
    p.setColor(QPalette.ColorRole.HighlightedText, highlighted_text)
    p.setColor(QPalette.ColorRole.Link, link)
    p.setColor(QPalette.ColorRole.ToolTipBase, tooltip_base)
    p.setColor(QPalette.ColorRole.ToolTipText, text)
    try:
        # Qt >= 5.12 / PyQt6: souvent disponible
        p.setColor(QPalette.ColorRole.PlaceholderText, placeholder_text)
    except Exception:
        pass

    # Etats désactivés
    # Sur certaines builds PyQt6, les surcharges setColor(group, role, color) sont fragiles.
    # On passe via les enum Qt et on protège pour éviter un crash au démarrage.
    try:
        p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled_text)
        p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_text)
        p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_text)
        p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Link, disabled_text)
        try:
            p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, disabled_text)
        except Exception:
            pass
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


def _clamp(v: float, lo: float, hi: float) -> float:
    try:
        v = float(v)
    except Exception:
        v = lo
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


def apply_font_scale(app, font_scale: float, save_to_settings: bool = True) -> bool:
    """
    Applique une échelle de police globale.

    Stratégie:
    - ajuste la police de QApplication (QFont)
    - ajoute un petit QSS global (QWidget { font-size: ...pt; }) pour couvrir
      les widgets qui ne reprennent pas correctement la police applicative.
    """
    from PyQt6.QtGui import QFont
    from ..cstatic import logger

    if app is None:
        return False

    scale = _clamp(font_scale, 0.7, 2.0)

    # Base: mémorisée une seule fois pour pouvoir revenir au "défaut" proprement
    base_pt = getattr(app, "_common_base_font_pt", None)
    if base_pt is None:
        try:
            base_pt = float(app.font().pointSizeF())
        except Exception:
            base_pt = 10.0
        if base_pt <= 0:
            base_pt = 10.0
        setattr(app, "_common_base_font_pt", base_pt)

    target_pt = max(6.0, base_pt * scale)
    try:
        f = QFont(app.font())
        f.setPointSizeF(target_pt)
        app.setFont(f)
    except Exception as exc:
        logger.warning("Application police globale impossible: %s", exc)

    # Ajouter (ou mettre à jour) une règle QSS dédiée.
    marker_begin = "/* COMMON_FONT_SCALE_BEGIN */"
    marker_end = "/* COMMON_FONT_SCALE_END */"
    rule = (
        f"{marker_begin}\n"
        f"QWidget {{ font-size: {target_pt:.1f}pt; }}\n"
        f"{marker_end}"
    )
    try:
        qss = app.styleSheet() or ""
        if marker_begin in qss and marker_end in qss:
            before = qss.split(marker_begin, 1)[0].rstrip()
            after = qss.split(marker_end, 1)[1].lstrip()
            qss = (before + "\n\n" + rule + "\n\n" + after).strip() + "\n"
        else:
            qss = (qss.rstrip() + "\n\n" + rule + "\n").lstrip("\n")
        app.setStyleSheet(qss)
    except Exception as exc:
        logger.debug("Injection QSS font-scale ignorée: %s", exc)

    if save_to_settings:
        try:
            from ..models import Settings, dbh

            if dbh is not None and dbh.is_closed():
                dbh.connect()
            sttg = Settings.get_or_none(Settings.id == 1)
            if sttg is None:
                sttg = Settings.init_settings()
            sttg.font_scale = float(scale)
            sttg.save()
            logger.info("Taille police enregistrée dans Settings: %s", scale)
        except Exception as exc:
            logger.warning("Enregistrement taille police impossible: %s", exc)

    return True


def change_font_scale(app, delta: float) -> bool:
    """Augmente/diminue l'échelle de police en gardant des bornes raisonnables."""
    try:
        from ..models import Settings, dbh

        if dbh is not None and dbh.is_closed():
            dbh.connect()
        st = Settings.init_settings()
        current = float(getattr(st, "font_scale", 1.0) or 1.0)
        new_scale = _clamp(current + float(delta), 0.7, 2.0)
        return apply_font_scale(app, new_scale, save_to_settings=True)
    except Exception:
        return apply_font_scale(app, 1.0, save_to_settings=False)


def get_theme_display_name(theme_name):
    """Retourne un libellé affichable pour le thème."""
    names = {
        THEME_LIGHT: "Clair",
        THEME_DARK: "Sombre",
        THEME_SYSTEM: "Système",
    }
    return names.get(theme_name, theme_name.capitalize())
