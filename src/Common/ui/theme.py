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

# Dimensions UI uniformes (source unique pour boutons, champs, etc.)
UI_CONTROL_MIN_HEIGHT = 36
UI_BUTTON_MIN_WIDTH = 88
UI_BUTTON_PADDING = "8px 16px"
UI_INPUT_PADDING = "8px 12px"

# Valeurs historiques / vides → suivre le système par défaut
_THEME_ALIASES_SYSTEM = frozenset(("", "default"))

# Variantes sémantiques (couleurs / comportement), tailles héritées du thème global
SEMANTIC_CONTROLS_STYLESHEET = """
    QPushButton#primaryButton, QCommandLinkButton#primaryButton {
        background-color: palette(highlight);
        color: palette(highlighted-text);
        border: none;
        font-weight: 600;
    }
    QPushButton#primaryButton:hover, QCommandLinkButton#primaryButton:hover {
        background-color: palette(highlight);
    }
    QPushButton#primaryButton:disabled, QCommandLinkButton#primaryButton:disabled {
        background-color: palette(mid);
        color: palette(placeholder-text);
    }

    QPushButton#dangerButton, QCommandLinkButton#dangerButton {
        background-color: #dc3545;
        color: #ffffff;
        border: 1px solid #c82333;
        font-weight: 600;
    }
    QPushButton#dangerButton:hover, QCommandLinkButton#dangerButton:hover {
        background-color: #c82333;
    }

    QPushButton#warningButton, QCommandLinkButton#warningButton {
        background-color: #ffc107;
        color: #1f2329;
        border: 1px solid #e0a800;
        font-weight: 600;
    }
    QPushButton#warningButton:hover, QCommandLinkButton#warningButton:hover {
        background-color: #e0a800;
    }

    QPushButton#linkButton, QCommandLinkButton#linkButton {
        min-height: 0px;
        min-width: 0px;
        padding: 4px 8px;
        background-color: transparent;
        color: palette(link);
        border: none;
        font-weight: normal;
    }
    QPushButton#linkButton:hover, QCommandLinkButton#linkButton:hover {
        text-decoration: underline;
    }

    QPushButton#compactButton, QCommandLinkButton#compactButton {
        min-width: 0px;
    }
"""


def _system_prefers_dark():
    """True si le système signale un schéma de couleurs sombre (Qt 6.5+)."""
    try:
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QGuiApplication

        scheme = QGuiApplication.styleHints().colorScheme()
        return scheme == Qt.ColorScheme.Dark
    except Exception:
        return False


def _effective_visual_theme(theme_name: str) -> str:
    """
    Thème réellement rendu (clair/sombre). Pour THEME_SYSTEM, suit l’OS.
    """
    if theme_name == THEME_SYSTEM:
        return THEME_DARK if _system_prefers_dark() else THEME_LIGHT
    return theme_name


def _restore_font_scale_qss(app) -> None:
    """Ré-injecte le QSS d’échelle de police après un setStyleSheet complet (thème)."""
    try:
        from ..models import Settings, dbh

        if dbh is not None and dbh.is_closed():
            dbh.connect()
        sttg = Settings.get_or_none(Settings.id == 1)
        if sttg is None:
            return
        apply_font_scale(app, float(getattr(sttg, "font_scale", 1.0) or 1.0), save_to_settings=False)
    except Exception:
        pass


def attach_system_theme_listener(app) -> None:
    """
    Ré-applique le thème lorsque l’OS bascule clair/sombre si le réglage est « système ».
    """
    if app is None:
        return
    if getattr(app, "_common_theme_scheme_listener_attached", False):
        return
    setattr(app, "_common_theme_scheme_listener_attached", True)
    try:
        from PyQt6.QtGui import QGuiApplication

        def _on_color_scheme_changed(_scheme=None):
            try:
                from ..models import Settings, dbh

                if dbh is None:
                    return
                if dbh.is_closed():
                    dbh.connect()
                st = Settings.get_or_none(Settings.id == 1)
                raw = (getattr(st, "theme", "") or "").strip().lower()
                if raw in _THEME_ALIASES_SYSTEM:
                    raw = THEME_SYSTEM
                if raw == THEME_SYSTEM:
                    apply_theme(app, THEME_SYSTEM, save_to_settings=False)
            except Exception:
                pass

        QGuiApplication.styleHints().colorSchemeChanged.connect(_on_color_scheme_changed)
    except Exception:
        pass


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
        min-height: 36px;
        min-width: 36px;
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
        padding: 8px 12px;
        min-height: 36px;
    }
    QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QDateTimeEdit:hover, QComboBox:hover {
        border-color: #6a6a6a;
    }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateTimeEdit:focus, QComboBox:focus {
        border: 2px solid #2d7bdc;
        padding: 7px 11px;
    }
    QComboBox::drop-down { border: none; width: 28px; }
    QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #ffffff; margin-right: 8px; }

    /* Buttons */
    QPushButton, QCommandLinkButton {
        background-color: #3a3a3a;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 8px;
        padding: 8px 16px;
        min-height: 36px;
        min-width: 88px;
        text-decoration: none;
    }
    QPushButton:hover, QCommandLinkButton:hover { background-color: #454545; }
    QPushButton:pressed, QCommandLinkButton:pressed { background-color: #4f4f4f; }
    QPushButton:disabled, QCommandLinkButton:disabled {
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

# Stylesheet pour le thème clair (moderne, cohérent avec le thème sombre)
THEME_LIGHT_STYLESHEET = """
    /* Base */
    QMainWindow, QWidget {
        background-color: #f4f6f9;
        color: #1f2329;
        selection-background-color: #2d7bdc;
        selection-color: #ffffff;
    }

    /* Toolbars + buttons */
    QToolBar {
        background-color: #ffffff;
        border: none;
        border-bottom: 1px solid #e3e7ec;
        spacing: 6px;
    }
    QToolBar::separator {
        background-color: #e0e4ea;
        width: 1px;
        margin: 6px 4px;
    }
    QToolButton {
        background-color: transparent;
        color: #1f2329;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 6px 8px;
        min-height: 36px;
        min-width: 36px;
    }
    QToolButton:hover {
        background-color: #eef2f7;
        border-color: #d6dce4;
    }
    QToolButton:pressed {
        background-color: #e1e8f1;
        border-color: #c2cbd6;
    }

    /* Menus */
    QMenuBar {
        background-color: #ffffff;
        color: #1f2329;
        border-bottom: 1px solid #e3e7ec;
    }
    QMenuBar::item {
        padding: 6px 10px;
        background: transparent;
    }
    QMenuBar::item:selected {
        background-color: #eef2f7;
        border-radius: 6px;
    }
    QMenu {
        background-color: #ffffff;
        color: #1f2329;
        border: 1px solid #e0e4ea;
        padding: 6px;
    }
    QMenu::item {
        padding: 6px 10px;
        border-radius: 6px;
    }
    QMenu::item:selected {
        background-color: #eef2f7;
    }
    QMenu::separator {
        height: 1px;
        background-color: #e8ebf0;
        margin: 6px 6px;
    }

    /* Inputs */
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QDateTimeEdit, QComboBox {
        background-color: #ffffff;
        color: #1f2329;
        border: 1px solid #cdd4dd;
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 36px;
    }
    QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QDateTimeEdit:hover, QComboBox:hover {
        border-color: #aab4c0;
    }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateTimeEdit:focus, QComboBox:focus {
        border: 2px solid #2d7bdc;
        padding: 7px 11px;
    }
    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QDateTimeEdit:disabled, QComboBox:disabled {
        background-color: #f0f2f5;
        color: #9aa3af;
        border-color: #e3e7ec;
    }
    QComboBox::drop-down { border: none; width: 28px; }
    QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #5a6470; margin-right: 8px; }

    /* Buttons */
    QPushButton, QCommandLinkButton {
        background-color: #ffffff;
        color: #1f2329;
        border: 1px solid #cdd4dd;
        border-radius: 8px;
        padding: 8px 16px;
        min-height: 36px;
        min-width: 88px;
        text-decoration: none;
    }
    QPushButton:hover, QCommandLinkButton:hover { background-color: #eef2f7; border-color: #aab4c0; }
    QPushButton:pressed, QCommandLinkButton:pressed { background-color: #e1e8f1; }
    QPushButton:disabled, QCommandLinkButton:disabled {
        background-color: #f0f2f5;
        color: #9aa3af;
        border-color: #e3e7ec;
    }

    /* Tables / lists */
    QTableView, QTableWidget, QListView, QTreeView {
        background-color: #ffffff;
        alternate-background-color: #f6f8fa;
        color: #1f2329;
        gridline-color: #e8ebf0;
        border: 1px solid #e0e4ea;
        border-radius: 8px;
    }
    QTableView::item:selected, QTableWidget::item:selected, QListView::item:selected, QTreeView::item:selected {
        background-color: #2d7bdc;
        color: #ffffff;
    }
    QHeaderView::section {
        background-color: #f0f3f7;
        color: #353b43;
        padding: 6px;
        border: none;
        border-right: 1px solid #e3e7ec;
        border-bottom: 1px solid #e3e7ec;
    }

    /* Tooltips */
    QToolTip {
        background-color: #2b2f36;
        color: #ffffff;
        border: 1px solid #2b2f36;
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
        background: #c5ccd6;
        min-height: 28px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover { background: #aab4c0; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    QScrollBar:horizontal {
        background: transparent;
        height: 12px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background: #c5ccd6;
        min-width: 28px;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal:hover { background: #aab4c0; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
"""


def _light_palette():
    """
    Palette Qt claire cohérente avec THEME_LIGHT_STYLESHEET.
    Définie en plus du stylesheet pour que les styles utilisant palette(...)
    et les widgets basés sur QPalette restent consistants.
    """
    from PyQt6.QtGui import QColor, QPalette

    p = QPalette()
    window = QColor("#f4f6f9")
    base = QColor("#ffffff")
    alt_base = QColor("#f6f8fa")
    text = QColor("#1f2329")
    disabled_text = QColor("#9aa3af")
    placeholder_text = QColor("#8a93a0")
    mid = QColor("#cdd4dd")
    midlight = QColor("#e0e4ea")
    button = QColor("#ffffff")
    highlight = QColor("#2d7bdc")
    link = QColor("#1a66c9")
    tooltip_base = QColor("#2b2f36")
    tooltip_text = QColor("#ffffff")
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
    p.setColor(QPalette.ColorRole.ToolTipText, tooltip_text)
    try:
        p.setColor(QPalette.ColorRole.PlaceholderText, placeholder_text)
    except Exception:
        pass

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
        pass

    return p


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
        theme_name: "light", "dark" ou "system" (pour "system", utiliser d’abord
            _effective_visual_theme pour obtenir light/dark effectif).

    Returns:
        str: Stylesheet à appliquer (thème clair ou sombre selon le cas).
    """
    if theme_name == THEME_DARK:
        return THEME_DARK_STYLESHEET + SEMANTIC_CONTROLS_STYLESHEET
    return THEME_LIGHT_STYLESHEET + SEMANTIC_CONTROLS_STYLESHEET


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

    normalized = str(theme_name or "").strip().lower()
    if normalized in _THEME_ALIASES_SYSTEM:
        normalized = THEME_SYSTEM
    elif normalized not in THEME_NAMES:
        normalized = THEME_LIGHT

    visual = _effective_visual_theme(normalized)
    stylesheet = get_stylesheet(visual)
    app.setStyleSheet(stylesheet)

    # Palette: indispensable pour les styles qui utilisent palette(...)
    if visual == THEME_DARK:
        app.setPalette(_dark_palette())
    else:
        # Palette claire dédiée (cohérente avec THEME_LIGHT_STYLESHEET)
        try:
            app.setPalette(_light_palette())
        except Exception:
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
            sttg.theme = normalized
            sttg.save()
            logger.info("Thème enregistré dans Settings: %s", normalized)
        except Exception as exc:
            logger.warning("Enregistrement du thème impossible: %s", exc)

    _restore_font_scale_qss(app)
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
