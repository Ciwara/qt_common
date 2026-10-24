#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
"""
Notifications toast : coin supérieur droit, empilables, durée configurable.
"""

from __future__ import annotations

import re

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    Qt,
    QTimer,
)
from PyQt6.QtGui import QFont, QGuiApplication
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# Emojis éventuellement déjà présents dans le texte (évite le doublon avec l'icône)
_LEADING_EMOJI = re.compile(
    r"^[\s]*(?:✅|❌|⚠️|ℹ️|🔔|🎉|💡|♻️|🗑️|🔓|🔑|📅|📆|👤|⛔|✔|✖)\s*"
)


class Notification(QWidget):
    """Toast empilable en haut à droite de l'écran."""

    _notifications = []
    _spacing = 12
    _margin = 20
    _base_y = 20
    _max_width = 420
    _min_width = 320

    _THEMES = {
        "success": {
            "icon": "✅",
            "title": "Succès",
            "bg": "#ECFDF5",
            "border": "#10B981",
            "accent": "#059669",
            "text": "#065F46",
            "muted": "#047857",
            "bar": "#10B981",
        },
        "error": {
            "icon": "❌",
            "title": "Erreur",
            "bg": "#FEF2F2",
            "border": "#EF4444",
            "accent": "#DC2626",
            "text": "#991B1B",
            "muted": "#B91C1C",
            "bar": "#EF4444",
        },
        "warning": {
            "icon": "⚠️",
            "title": "Attention",
            "bg": "#FFFBEB",
            "border": "#F59E0B",
            "accent": "#D97706",
            "text": "#92400E",
            "muted": "#B45309",
            "bar": "#F59E0B",
        },
        "info": {
            "icon": "ℹ️",
            "title": "Information",
            "bg": "#EFF6FF",
            "border": "#3B82F6",
            "accent": "#2563EB",
            "text": "#1E3A8A",
            "muted": "#1D4ED8",
            "bar": "#3B82F6",
        },
    }

    def __init__(self, mssg="Bonjour", type_mssg="info", parent=None, duration=5000):
        super().__init__(parent)

        if parent is None:
            parent = QApplication.activeWindow()
            if parent is None:
                for widget in QApplication.topLevelWidgets():
                    if widget.isWindow() and widget.isVisible():
                        parent = widget
                        break

        self.type_mssg = (type_mssg or "info").lower()
        if self.type_mssg not in self._THEMES:
            self.type_mssg = "info"
        self.theme = self._THEMES[self.type_mssg]
        self.duration = max(0, int(duration or 0))
        self._close_timer = None
        self._progress_timer = None
        self._elapsed = 0
        self._closing = False

        raw = str(mssg or "").strip()
        self.message = _LEADING_EMOJI.sub("", raw).strip() or raw

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._setup_ui()
        self._apply_size()

        Notification._notifications.append(self)
        Notification._reposition_all(animate=False)

        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(0.0)
        self.show()
        self._fade_in()

        if self.duration > 0:
            self._close_timer = QTimer(self)
            self._close_timer.setSingleShot(True)
            self._close_timer.timeout.connect(self.close_notification)
            self._close_timer.start(self.duration)

            self._progress_timer = QTimer(self)
            self._progress_timer.timeout.connect(self._tick_progress)
            self._progress_timer.start(40)

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.card = QFrame()
        self.card.setObjectName("toastCard")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        body = QHBoxLayout()
        body.setContentsMargins(14, 14, 10, 12)
        body.setSpacing(12)

        accent = QFrame()
        accent.setFixedWidth(4)
        accent.setStyleSheet(
            f"background-color: {self.theme['accent']}; border-radius: 2px;"
        )
        body.addWidget(accent)

        icon = QLabel(self.theme["icon"])
        icon.setFixedSize(28, 28)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 18px; background: transparent; border: none;")
        body.addWidget(icon, 0, Qt.AlignmentFlag.AlignTop)

        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        text_col.setContentsMargins(0, 0, 0, 0)

        title = QLabel(self.theme["title"])
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(
            f"color: {self.theme['accent']}; background: transparent; border: none;"
        )
        text_col.addWidget(title)

        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        self.message_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        msg_font = QFont()
        msg_font.setPointSize(11)
        self.message_label.setFont(msg_font)
        self.message_label.setStyleSheet(
            f"color: {self.theme['text']}; background: transparent; border: none;"
        )
        self.message_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        text_col.addWidget(self.message_label)
        body.addLayout(text_col, 1)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFlat(True)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setToolTip("Fermer")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.close_btn.clicked.connect(self.close_notification)
        self.close_btn.setStyleSheet(
            f"""
            QPushButton {{
                color: {self.theme['muted']};
                background: transparent;
                border: none;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 0, 0, 0.06);
                color: {self.theme['text']};
            }}
            """
        )
        body.addWidget(self.close_btn, 0, Qt.AlignmentFlag.AlignTop)

        card_layout.addLayout(body)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(3)
        self.progress.setRange(0, 1000)
        self.progress.setValue(1000 if self.duration > 0 else 0)
        self.progress.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: rgba(0, 0, 0, 0.06);
                border: none;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {self.theme['bar']};
                border-bottom-left-radius: 10px;
            }}
            """
        )
        if self.duration > 0:
            card_layout.addWidget(self.progress)

        self.card.setStyleSheet(
            f"""
            QFrame#toastCard {{
                background-color: {self.theme['bg']};
                border: 1px solid {self.theme['border']};
                border-radius: 10px;
            }}
            """
        )
        outer.addWidget(self.card)

    def _apply_size(self):
        """Calcule largeur / hauteur selon le contenu (messages multi-lignes inclus)."""
        width = self._min_width
        lines = self.message.count("\n") + 1
        if len(self.message) > 80 or lines > 2:
            width = self._max_width
        elif len(self.message) > 40:
            width = 380

        self.setFixedWidth(width)
        self.message_label.setFixedWidth(width - 14 - 4 - 28 - 12 - 28 - 10 - 24)
        self.message_label.adjustSize()
        self.adjustSize()
        # Hauteur mini confortable
        if self.height() < 72:
            self.setMinimumHeight(72)
            self.adjustSize()

    def _fade_in(self):
        anim = QPropertyAnimation(self._opacity, b"opacity", self)
        anim.setDuration(220)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._fade_anim = anim  # garder une référence

    def _tick_progress(self):
        if self.duration <= 0 or self._closing:
            return
        self._elapsed += 40
        remaining = max(0, self.duration - self._elapsed)
        self.progress.setValue(int(1000 * remaining / self.duration))

    def close_notification(self):
        if self._closing:
            return
        self._closing = True

        if self._close_timer:
            self._close_timer.stop()
            self._close_timer = None
        if self._progress_timer:
            self._progress_timer.stop()
            self._progress_timer = None

        try:
            if self in Notification._notifications:
                Notification._notifications.remove(self)
        except (ValueError, RuntimeError):
            pass

        Notification._reposition_all(animate=True)

        fade = QPropertyAnimation(self._opacity, b"opacity", self)
        fade.setDuration(180)
        fade.setStartValue(self._opacity.opacity())
        fade.setEndValue(0.0)
        fade.setEasingCurve(QEasingCurve.Type.InCubic)
        fade.finished.connect(self._finish_close)
        fade.start()
        self._fade_out_anim = fade

    def _finish_close(self):
        self.hide()
        self.close()
        self.deleteLater()

    def mouseDoubleClickEvent(self, event):
        """Double-clic → fermer (le texte reste sélectionnable au clic simple)."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.close_notification()
        super().mouseDoubleClickEvent(event)

    @classmethod
    def _screen_rect(cls):
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return QRect(0, 0, 1280, 800)
        return screen.availableGeometry()

    @classmethod
    def _reposition_all(cls, animate=False):
        from PyQt6.QtCore import QPoint

        try:
            screen = cls._screen_rect()
            y_offset = cls._base_y
            for notif in list(cls._notifications):
                try:
                    if notif is None:
                        continue
                    x = screen.x() + screen.width() - notif.width() - cls._margin
                    y = screen.y() + y_offset
                    target = QPoint(x, y)
                    if animate and notif.isVisible():
                        move = QPropertyAnimation(notif, b"pos", notif)
                        move.setDuration(200)
                        move.setStartValue(notif.pos())
                        move.setEndValue(target)
                        move.setEasingCurve(QEasingCurve.Type.OutCubic)
                        move.start()
                        notif._move_anim = move
                    else:
                        notif.move(target)
                    y_offset += notif.height() + cls._spacing
                except (RuntimeError, AttributeError):
                    continue
        except Exception:
            pass
