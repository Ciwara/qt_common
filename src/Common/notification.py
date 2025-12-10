#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
"""
Module de notification moderne avec interface améliorée
"""

from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, QPoint, QRectF
from PyQt5.QtGui import QColor, QPainter, QPainterPath
from PyQt5.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QApplication, QPushButton
)


class ModernNotification(QWidget):
    """Widget de notification moderne avec animations et styles améliorés"""
    
    def __init__(self, mssg="👋 Bonjour", type_mssg="info", parent=None, duration=4000):
        super().__init__(parent)
        self.message = mssg
        self.type_mssg = type_mssg
        self.duration = duration
        self._opacity = 1.0
        
        # Configuration de la fenêtre
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Configuration de l'interface
        self._setup_ui()
        self._setup_style()
        self._setup_animations()
        
        # Positionnement
        self._position_notification()
        
        # Timer pour la fermeture automatique
        if self.duration > 0:
            QTimer.singleShot(self.duration, self.fade_out)
    
    def _setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Icône selon le type
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Définir l'icône selon le type
        icon_map = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        icon_text = icon_map.get(self.type_mssg, "🔔")
        icon_label.setText(icon_text)
        icon_label.setStyleSheet("font-size: 24px;")
        
        # Message (la couleur sera définie dans _setup_style selon le thème)
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 500;
                background: transparent;
                padding: 0px;
            }
        """)
        
        # Bouton de fermeture
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setFlat(True)
        # Le style du bouton sera adapté dans _setup_style selon le thème
        self.close_btn = close_btn
        # Utiliser clicked.connect avec une lambda pour éviter les problèmes de référence
        close_btn.clicked.connect(lambda checked=False: self.fade_out())
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setToolTip("Fermer")
        close_btn.setFocusPolicy(Qt.NoFocus)  # Éviter que le bouton prenne le focus
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, 1)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def _setup_style(self):
        """Configure le style selon le type de message"""
        # Mode clair par défaut
        is_dark = False
        
        # Couleurs selon le type et le thème
        if is_dark:
            # Thème sombre
            colors = {
                "success": {
                    "bg": "#1e4620",
                    "border": "#2d5a31",
                    "text": "#81c784",
                    "icon_bg": "#4caf50"
                },
                "error": {
                    "bg": "#4a1f1f",
                    "border": "#5d2727",
                    "text": "#e57373",
                    "icon_bg": "#f44336"
                },
                "warning": {
                    "bg": "#4a3f1f",
                    "border": "#5d4f27",
                    "text": "#ffb74d",
                    "icon_bg": "#ff9800"
                },
                "info": {
                    "bg": "#1e3a4a",
                    "border": "#2d4d5a",
                    "text": "#64b5f6",
                    "icon_bg": "#2196f3"
                }
            }
        else:
            # Thème clair (par défaut)
            colors = {
                "success": {
                    "bg": "#d4edda",
                    "border": "#c3e6cb",
                    "text": "#155724",
                    "icon_bg": "#28a745"
                },
                "error": {
                    "bg": "#f8d7da",
                    "border": "#f5c6cb",
                    "text": "#721c24",
                    "icon_bg": "#dc3545"
                },
                "warning": {
                    "bg": "#fff3cd",
                    "border": "#ffeaa7",
                    "text": "#856404",
                    "icon_bg": "#ffc107"
                },
                "info": {
                    "bg": "#d1ecf1",
                    "border": "#bee5eb",
                    "text": "#0c5460",
                    "icon_bg": "#17a2b8"
                }
            }
        
        color_scheme = colors.get(self.type_mssg, colors["info"])
        
        # Style avec coins arrondis et ombre
        shadow_opacity = 40 if is_dark else 80
        close_btn_color = "#95a5a6" if is_dark else "#7f8c8d"
        close_btn_hover_bg = "#34495e" if is_dark else "#ecf0f1"
        close_btn_pressed_bg = "#2c3e50" if is_dark else "#bdc3c7"
        
        self.setStyleSheet(f"""
            ModernNotification {{
                background-color: {color_scheme['bg']};
                border: 2px solid {color_scheme['border']};
                border-radius: 12px;
                min-width: 300px;
                max-width: 500px;
            }}
            QLabel {{
                color: {color_scheme['text']};
            }}
            QPushButton {{
                color: {close_btn_color};
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
                border-radius: 12px;
                padding: 0px;
            }}
            QPushButton:hover {{
                color: #e74c3c;
                background: {close_btn_hover_bg};
            }}
            QPushButton:pressed {{
                background: {close_btn_pressed_bg};
            }}
        """)
        
        # Ajouter une ombre portée adaptée au thème
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, shadow_opacity))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def _setup_animations(self):
        """Configure les animations d'apparition et de disparition"""
        # Animation de fade in
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Animation de slide in
        self.slide_animation = QPropertyAnimation(self, b"pos")
        self.slide_animation.setDuration(300)
        self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Démarrer les animations
        self.fade_in_animation.start()
        self._animate_slide_in()
    
    def _animate_slide_in(self):
        """Animation de glissement depuis le haut"""
        screen = QApplication.primaryScreen().geometry()
        # Position finale sera gérée par NotificationManager
        start_pos = QPoint(
            screen.width() - self.width() - 20,
            -self.height()
        )
        # Position temporaire, sera repositionnée par le manager
        end_pos = QPoint(
            screen.width() - self.width() - 20,
            20
        )
        self.move(start_pos)
        self.slide_animation.setStartValue(start_pos)
        self.slide_animation.setEndValue(end_pos)
        self.slide_animation.finished.connect(self._on_slide_finished)
        self.slide_animation.start()
    
    def _on_slide_finished(self):
        """Appelé après l'animation de slide pour repositionner"""
        NotificationManager._reposition_all()
    
    def _position_notification(self):
        """Positionne la notification en haut à droite"""
        screen = QApplication.primaryScreen().geometry()
        # Ajuster la taille selon la longueur du message
        message_length = len(self.message)
        if message_length < 30:
            width = 300
        elif message_length < 60:
            width = 400
        else:
            width = 500
        
        self.resize(width, 80)
        # La position finale sera gérée par NotificationManager
        self.move(
            screen.width() - self.width() - 20,
            20
        )
    
    def fade_out(self):
        """Animation de disparition"""
        # Retirer immédiatement du gestionnaire pour éviter les problèmes de repositionnement
        NotificationManager._remove_notification(self)
        
        # Désactiver le bouton de fermeture pour éviter les clics multiples
        if hasattr(self, 'close_btn'):
            self.close_btn.setEnabled(False)
        
        fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        fade_out_animation.setDuration(300)
        fade_out_animation.setStartValue(1.0)
        fade_out_animation.setEndValue(0.0)
        fade_out_animation.setEasingCurve(QEasingCurve.InCubic)
        fade_out_animation.finished.connect(self._on_fade_out_finished)
        fade_out_animation.start()
    
    def _on_fade_out_finished(self):
        """Appelé après l'animation de fade out pour fermer et nettoyer"""
        self.hide()
        self.close()
        self.deleteLater()
    
    def showEvent(self, event):
        """Affiche la notification avec animation"""
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
    
    def paintEvent(self, event):
        """Dessine les coins arrondis"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        # Convertir QRect en QRectF pour addRoundedRect
        rect = QRectF(self.rect().adjusted(1, 1, -1, -1))
        path.addRoundedRect(rect, 12.0, 12.0)
        
        painter.fillPath(path, QColor(self.palette().color(self.backgroundRole())))


class NotificationManager:
    """Gestionnaire de notifications pour empiler et gérer plusieurs notifications"""
    
    _notifications = []
    _spacing = 10
    _base_y = 20
    
    @classmethod
    def add_notification(cls, notification):
        """Ajoute une notification à la liste et repositionne toutes les notifications"""
        cls._notifications.append(notification)
        cls._reposition_all()
        
        # Nettoyer les notifications fermées
        def on_destroyed():
            cls._remove_notification(notification)
        notification.destroyed.connect(on_destroyed)
    
    @classmethod
    def _remove_notification(cls, notification):
        """Retire une notification de la liste"""
        try:
            if notification in cls._notifications:
                cls._notifications.remove(notification)
                cls._reposition_all()
        except (RuntimeError, AttributeError):
            # Ignorer les erreurs si la notification est déjà supprimée
            pass
    
    @classmethod
    def _reposition_all(cls):
        """Repositionne toutes les notifications actives"""
        try:
            screen = QApplication.primaryScreen().geometry()
            y_offset = cls._base_y
            
            # Filtrer les notifications valides et visibles
            valid_notifications = [
                notif for notif in cls._notifications 
                if notif is not None and notif.isVisible()
            ]
            
            for notif in valid_notifications:
                try:
                    notif.move(
                        screen.width() - notif.width() - 20,
                        y_offset
                    )
                    y_offset += notif.height() + cls._spacing
                except (RuntimeError, AttributeError):
                    # Ignorer les erreurs pour les notifications supprimées
                    continue
        except Exception:
            # Ignorer les erreurs de repositionnement
            pass


class Notification:
    """Classe wrapper pour créer et afficher des notifications"""
    
    def __init__(self, mssg="👋 Bonjour", type_mssg="info", parent=None, duration=4000):
        """
        Crée et affiche une notification
        
        Args:
            mssg: Message à afficher
            type_mssg: Type de notification (success, error, warning, info)
            parent: Widget parent
            duration: Durée d'affichage en millisecondes (0 = permanent)
        """
        # Trouver la fenêtre principale si parent n'est pas fourni
        if parent is None:
            parent = QApplication.activeWindow()
            if parent is None:
                # Chercher la fenêtre principale
                for widget in QApplication.topLevelWidgets():
                    if hasattr(widget, 'isWindow') and widget.isWindow():
                        parent = widget
                        break
        
        self.notification = ModernNotification(mssg, type_mssg, parent, duration)
        
        # Ajouter au gestionnaire de notifications
        NotificationManager.add_notification(self.notification)
        
        self.notification.show()
        
        # Garder une référence pour éviter la suppression par le garbage collector
        self.notification.setAttribute(Qt.WA_DeleteOnClose, False)
