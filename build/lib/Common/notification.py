#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
"""
Module de notification simple et efficace
"""

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QApplication, QPushButton
)


class Notification(QWidget):
    """Widget de notification simple"""
    
    _notifications = []  # Liste globale des notifications actives
    _spacing = 10
    _base_y = 20
    
    def __init__(self, mssg="👋 Bonjour", type_mssg="info", parent=None, duration=5000):
        """
        Crée et affiche une notification
        
        Args:
            mssg: Message à afficher
            type_mssg: Type de notification (success, error, warning, info)
            parent: Widget parent
            duration: Durée d'affichage en millisecondes (0 = permanent, défaut: 5000ms)
        """
        super().__init__(parent)
        
        # Trouver le parent si non fourni
        if parent is None:
            parent = QApplication.activeWindow()
            if parent is None:
                for widget in QApplication.topLevelWidgets():
                    if hasattr(widget, 'isWindow') and widget.isWindow():
                        parent = widget
                        break
        
        self.message = mssg
        self.type_mssg = type_mssg
        self.duration = duration
        self._close_timer = None
        
        # Configuration de la fenêtre
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # Interface utilisateur
        self._setup_ui()
        self._setup_style()
        self._position_notification()
        
        # Ajouter à la liste et afficher
        Notification._notifications.append(self)
        Notification._reposition_all()
        self.show()
        
        # Timer de fermeture automatique
        if self.duration > 0:
            self._close_timer = QTimer()
            self._close_timer.setSingleShot(True)
            self._close_timer.timeout.connect(self.close_notification)
            self._close_timer.start(self.duration)
    
    def _setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Icône selon le type
        icon_map = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
        icon_label = QLabel(icon_map.get(self.type_mssg, "🔔"))
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # icon_label.setStyleSheet("font-size: 24px;")
        
        # Message
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # message_label.setStyleSheet("font-size: 14px; font-weight: 500; background: transparent; padding: 0px;")
        
        # Bouton de fermeture
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setFlat(True)
        self.close_btn.clicked.connect(self.close_notification)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setToolTip("Fermer")
        self.close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, 1)
        layout.addWidget(self.close_btn)
    
    def _setup_style(self):
        """Configure le style de la notification selon le type"""
        # Styles selon le type de notification
        styles = {
            "success": """
                QWidget {
                    background-color: #d4edda;
                    border: 2px solid #28a745;
                    border-radius: 8px;
                    color: #155724;
                }
            """,
            "error": """
                QWidget {
                    background-color: #f8d7da;
                    border: 2px solid #dc3545;
                    border-radius: 8px;
                    color: #721c24;
                }
            """,
            "warning": """
                QWidget {
                    background-color: #fff3cd;
                    border: 2px solid #ffc107;
                    border-radius: 8px;
                    color: #856404;
                }
            """,
            "info": """
                QWidget {
                    background-color: #d1ecf1;
                    border: 2px solid #17a2b8;
                    border-radius: 8px;
                    color: #0c5460;
                }
            """
        }
        
        # Appliquer le style selon le type
        style = styles.get(self.type_mssg, styles["info"])
        self.setStyleSheet(style)
    
    def _position_notification(self):
        """Positionne la notification en haut à droite"""
        screen = QApplication.primaryScreen().geometry()
        width = 300 if len(self.message) < 30 else (400 if len(self.message) < 60 else 500)
        self.resize(width, 80)
        self.move(screen.width() - width - 20, Notification._base_y)
    
    def close_notification(self):
        """Ferme la notification"""
        if self._close_timer:
            self._close_timer.stop()
            self._close_timer = None
        
        # Retirer de la liste
        try:
            if self in Notification._notifications:
                Notification._notifications.remove(self)
        except (ValueError, RuntimeError):
            pass
        
        # Repositionner les autres notifications
        Notification._reposition_all()
        
        # Fermer le widget
        self.hide()
        self.close()
        self.deleteLater()
    
    def mousePressEvent(self, event):
        """Permet de fermer en cliquant sur la notification"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Si on ne clique pas sur le bouton, fermer quand même
            child = self.childAt(event.pos())
            if child != self.close_btn:
                self.close_notification()
        super().mousePressEvent(event)
    
    @classmethod
    def _reposition_all(cls):
        """Repositionne toutes les notifications actives"""
        try:
            screen = QApplication.primaryScreen().geometry()
            y_offset = cls._base_y
            
            for notif in [n for n in cls._notifications if n is not None]:
                try:
                    if notif.isVisible():
                        notif.move(screen.width() - notif.width() - 20, y_offset)
                        y_offset += notif.height() + cls._spacing
                except (RuntimeError, AttributeError):
                    continue
        except Exception:
            pass
