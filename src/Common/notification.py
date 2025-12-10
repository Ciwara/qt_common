#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
"""
Module de notification moderne avec interface améliorée
"""

from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QApplication, QPushButton
)


class ModernNotification(QWidget):
    """Widget de notification moderne avec animations"""
    
    def __init__(self, mssg="👋 Bonjour", type_mssg="info", parent=None, duration=5000):
        super().__init__(parent)
        self.message = mssg
        self.type_mssg = type_mssg
        self.duration = duration
        self._close_timer = None
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        self._setup_ui()
        self._setup_style()
        self._position_notification()
        self._setup_animations()
    
    def _setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        icon_map = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
        icon_label = QLabel(icon_map.get(self.type_mssg, "🔔"))
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px;")
        
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        message_label.setStyleSheet("font-size: 14px; font-weight: 500; background: transparent; padding: 0px;")
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setFlat(True)
        self.close_btn.clicked.connect(self.fade_out)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setToolTip("Fermer")
        self.close_btn.setFocusPolicy(Qt.NoFocus)
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, 1)
        layout.addWidget(self.close_btn)
    
    def _setup_style(self):
        """Configure le style selon le type de message"""
        colors = {
            "success": {"bg": "#d4edda", "border": "#c3e6cb", "text": "#155724"},
            "error": {"bg": "#f8d7da", "border": "#f5c6cb", "text": "#721c24"},
            "warning": {"bg": "#fff3cd", "border": "#ffeaa7", "text": "#856404"},
            "info": {"bg": "#d1ecf1", "border": "#bee5eb", "text": "#0c5460"}
        }
        color_scheme = colors.get(self.type_mssg, colors["info"])
        
        self.setStyleSheet(f"""
            ModernNotification {{
                background-color: {color_scheme['bg']};
                border: 2px solid {color_scheme['border']};
                border-radius: 12px;
                min-width: 300px;
                max-width: 500px;
            }}
            QLabel {{ color: {color_scheme['text']}; }}
            QPushButton {{
                color: #7f8c8d;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
                border-radius: 12px;
                padding: 0px;
            }}
            QPushButton:hover {{ color: #e74c3c; background: #ecf0f1; }}
            QPushButton:pressed {{ background: #bdc3c7; }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def _setup_animations(self):
        """Configure les animations d'apparition"""
        self.setWindowOpacity(0.0)
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_in_animation.start()
    
    def _position_notification(self):
        """Positionne la notification en haut à droite"""
        screen = QApplication.primaryScreen().geometry()
        width = 300 if len(self.message) < 30 else (400 if len(self.message) < 60 else 500)
        self.resize(width, 80)
        self.move(screen.width() - width - 20, 20)
    
    def fade_out(self):
        """Animation de disparition"""
        if self._close_timer:
            self._close_timer.stop()
            self._close_timer = None
        
        NotificationManager._remove_notification(self)
        self.close_btn.setEnabled(False)
        
        fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        fade_out_animation.setDuration(300)
        fade_out_animation.setStartValue(1.0)
        fade_out_animation.setEndValue(0.0)
        fade_out_animation.setEasingCurve(QEasingCurve.InCubic)
        fade_out_animation.finished.connect(self._on_fade_out_finished)
        fade_out_animation.start()
    
    def _on_fade_out_finished(self):
        """Appelé après l'animation de fade out"""
        self.hide()
        self.close()
        self.deleteLater()
    
    def showEvent(self, event):
        """Démarre le timer de fermeture automatique"""
        super().showEvent(event)
        self.raise_()
        
        if self.duration > 0 and not self._close_timer:
            self._close_timer = QTimer()
            self._close_timer.setSingleShot(True)
            self._close_timer.timeout.connect(self.fade_out)
            self._close_timer.start(self.duration)


class NotificationManager:
    """Gestionnaire de notifications pour empiler et gérer plusieurs notifications"""
    
    _notifications = []
    _spacing = 10
    _base_y = 20
    
    @classmethod
    def add_notification(cls, notification):
        """Ajoute une notification à la liste et repositionne"""
        cls._notifications.append(notification)
        cls._reposition_all()
        notification.destroyed.connect(lambda: cls._remove_notification(notification))
    
    @classmethod
    def _remove_notification(cls, notification):
        """Retire une notification de la liste"""
        try:
            if notification in cls._notifications:
                cls._notifications.remove(notification)
                cls._reposition_all()
        except (RuntimeError, AttributeError):
            pass
    
    @classmethod
    def _reposition_all(cls):
        """Repositionne toutes les notifications actives"""
        try:
            screen = QApplication.primaryScreen().geometry()
            y_offset = cls._base_y
            
            for notif in [n for n in cls._notifications if n is not None and n.isVisible()]:
                try:
                    notif.move(screen.width() - notif.width() - 20, y_offset)
                    y_offset += notif.height() + cls._spacing
                except (RuntimeError, AttributeError):
                    continue
        except Exception:
            pass


class Notification:
    """Classe wrapper pour créer et afficher des notifications"""
    
    def __init__(self, mssg="👋 Bonjour", type_mssg="info", parent=None, duration=5000):
        """
        Crée et affiche une notification
        
        Args:
            mssg: Message à afficher
            type_mssg: Type de notification (success, error, warning, info)
            parent: Widget parent
            duration: Durée d'affichage en millisecondes (0 = permanent, défaut: 5000ms)
        """
        if parent is None:
            parent = QApplication.activeWindow()
            if parent is None:
                for widget in QApplication.topLevelWidgets():
                    if hasattr(widget, 'isWindow') and widget.isWindow():
                        parent = widget
                        break
        
        self.notification = ModernNotification(mssg, type_mssg, parent, duration)
        NotificationManager.add_notification(self.notification)
        self.notification.show()
