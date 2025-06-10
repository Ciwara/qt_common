#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Widgets Qt modernes et améliorés
Complément aux widgets existants avec un design moderne
"""

from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QPainterPath, QBrush, QColor, QFont, QFontMetrics, QIcon
from PyQt5.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QComboBox, QGroupBox, QFrame,
    QToolButton, QProgressBar, QSlider, QCheckBox, QRadioButton,
    QTextEdit, QSpinBox, QDoubleSpinBox, QTabWidget, QTabBar,
    QScrollBar, QWidget, QHBoxLayout, QVBoxLayout, QGraphicsEffect,
    QGraphicsDropShadowEffect
)

from .style_manager import Colors

class ModernButton(QPushButton):
    """Bouton moderne avec animations et effets"""
    
    def __init__(self, text="", icon=None, button_type="default", parent=None):
        super().__init__(text, parent)
        
        self.button_type = button_type
        self._original_size = None
        
        # Configuration de base
        self.setMinimumHeight(40)
        from .font_utils import create_system_font
        self.setFont(create_system_font(10, QFont.Medium))
        
        # Icône si fournie
        if icon:
            self.setIcon(icon)
            self.setIconSize(self.size() * 0.7)
        
        # Application du style selon le type
        self._apply_button_style()
        
        # Effet d'ombre
        self._add_shadow_effect()
        
        # Configuration des animations
        self._setup_animations()
    
    def _apply_button_style(self):
        """Applique le style selon le type de bouton"""
        styles = {
            "primary": f"""
                QPushButton {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {Colors.BLUE_PRIMARY}, stop: 1 #0056b3);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: 600;
                    padding: 10px 20px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {Colors.BLUE_LIGHT}, stop: 1 {Colors.BLUE_PRIMARY});
                }}
                QPushButton:pressed {{
                    background: #0056b3;
                }}
            """,
            
            "success": f"""
                QPushButton {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {Colors.GREEN_PRIMARY}, stop: 1 #146c43);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: 600;
                    padding: 10px 20px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #20c997, stop: 1 {Colors.GREEN_PRIMARY});
                }}
            """,
            
            "danger": f"""
                QPushButton {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {Colors.RED_PRIMARY}, stop: 1 #b02a37);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: 600;
                    padding: 10px 20px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #f5c6cb, stop: 1 {Colors.RED_PRIMARY});
                }}
            """,
            
            "default": f"""
                QPushButton {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {Colors.WHITE}, stop: 1 #f8f9fa);
                    border: 1.5px solid #d1d5db;
                    border-radius: 8px;
                    color: #374151;
                    font-weight: 500;
                    padding: 10px 20px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #f8f9fa, stop: 1 #e9ecef);
                    border-color: #9ca3af;
                }}
                QPushButton:pressed {{
                    background: #e9ecef;
                }}
            """
        }
        
        self.setStyleSheet(styles.get(self.button_type, styles["default"]))
    
    def _add_shadow_effect(self):
        """Ajoute un effet d'ombre portée"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
    
    def _setup_animations(self):
        """Configure les animations"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(100)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def enterEvent(self, event):
        """Animation lors du survol"""
        super().enterEvent(event)
        if self._original_size is None:
            self._original_size = self.geometry()
        
        # Légère expansion
        new_rect = QRect(self._original_size)
        new_rect.adjust(-2, -1, 2, 1)
        
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(new_rect)
        self.animation.start()
    
    def leaveEvent(self, event):
        """Animation lors de la sortie du survol"""
        super().leaveEvent(event)
        if self._original_size:
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(self._original_size)
            self.animation.start()

class ModernLineEdit(QLineEdit):
    """Champ de saisie moderne avec label flottant"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        
        self.placeholder_text = placeholder
        self.setPlaceholderText(placeholder)
        
        # Style moderne
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {Colors.WHITE};
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                color: #111827;
                padding: 12px 16px;
                font-size: 14px;
                font-family: "Segoe UI", sans-serif;
            }}
            
            QLineEdit:focus {{
                border-color: {Colors.BLUE_PRIMARY};
                background: {Colors.WHITE};
            }}
            
            QLineEdit:hover {{
                border-color: #9ca3af;
            }}
            
            QLineEdit:disabled {{
                background: #f9fafb;
                border-color: #e5e7eb;
                color: #6b7280;
            }}
        """)
        
        # Effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(1)
        shadow.setColor(QColor(0, 0, 0, 10))
        self.setGraphicsEffect(shadow)
        
        self.setMinimumHeight(44)

class ModernComboBox(QComboBox):
    """ComboBox moderne avec style amélioré"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet(f"""
            QComboBox {{
                background: {Colors.WHITE};
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                color: #111827;
                padding: 12px 16px;
                padding-right: 40px;
                font-size: 14px;
                font-family: "Segoe UI", sans-serif;
                min-height: 20px;
            }}
            
            QComboBox:hover {{
                border-color: #9ca3af;
            }}
            
            QComboBox:focus {{
                border-color: {Colors.BLUE_PRIMARY};
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 32px;
                border-left: 2px solid #e5e7eb;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background: #f9fafb;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #6b7280;
                margin: auto;
            }}
            
            QComboBox QAbstractItemView {{
                background: {Colors.WHITE};
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                selection-background-color: {Colors.BLUE_PRIMARY};
                selection-color: white;
                outline: none;
                padding: 4px;
            }}
            
            QComboBox QAbstractItemView::item {{
                padding: 10px 12px;
                border-radius: 4px;
                margin: 1px;
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background: #f3f4f6;
            }}
            
            QComboBox QAbstractItemView::item:selected {{
                background: {Colors.BLUE_PRIMARY};
                color: white;
            }}
        """)
        
        # Effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(1)
        shadow.setColor(QColor(0, 0, 0, 10))
        self.setGraphicsEffect(shadow)
        
        self.setMinimumHeight(44)

class ModernGroupBox(QGroupBox):
    """GroupBox moderne avec design amélioré"""
    
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        
        self.setStyleSheet(f"""
            QGroupBox {{
                background: {Colors.WHITE};
                border: 2px solid {Colors.BLUE_PRIMARY};
                border-radius: 12px;
                font-weight: 600;
                font-size: 14px;
                font-family: "Segoe UI", sans-serif;
                color: #374151;
                margin-top: 1ex;
                padding-top: 20px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 6px 16px;
                background: {Colors.BLUE_PRIMARY};
                color: white;
                font-weight: 700;
                border-radius: 8px;
                margin-left: 12px;
                margin-top: -2px;
            }}
        """)
        
        # Effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(shadow)

class ModernProgressBar(QProgressBar):
    """Barre de progression moderne avec animations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet(f"""
            QProgressBar {{
                background: #f1f5f9;
                border: none;
                border-radius: 10px;
                text-align: center;
                color: #475569;
                font-weight: 600;
                font-family: "Segoe UI", sans-serif;
                padding: 2px;
            }}
            
            QProgressBar::chunk {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {Colors.BLUE_PRIMARY}, stop: 1 #0056b3);
                border-radius: 8px;
                margin: 1px;
            }}
        """)
        
        self.setMinimumHeight(20)

class ModernSlider(QSlider):
    """Slider moderne avec design amélioré"""
    
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        
        if orientation == Qt.Horizontal:
            self.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    border: none;
                    height: 8px;
                    background: #e2e8f0;
                    border-radius: 4px;
                }}
                
                QSlider::handle:horizontal {{
                    background: {Colors.BLUE_PRIMARY};
                    border: 3px solid white;
                    width: 24px;
                    height: 24px;
                    margin: -8px 0;
                    border-radius: 12px;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
                }}
                
                QSlider::handle:horizontal:hover {{
                    background: {Colors.BLUE_LIGHT};
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                }}
                
                QSlider::sub-page:horizontal {{
                    background: {Colors.BLUE_PRIMARY};
                    border-radius: 4px;
                }}
                
                QSlider::add-page:horizontal {{
                    background: #e2e8f0;
                    border-radius: 4px;
                }}
            """)

class AnimatedLabel(QLabel):
    """Label avec effet d'apparition animé"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        
        self.setStyleSheet("""
            QLabel {
                color: #374151;
                font-family: "Segoe UI", sans-serif;
                font-weight: 500;
            }
        """)
        
        # Animation d'opacité
        self.opacity_effect = QGraphicsEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def fade_in(self):
        """Animation d'apparition"""
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
    
    def fade_out(self):
        """Animation de disparition"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()

class ModernTabWidget(QTabWidget):
    """Widget d'onglets modernes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet(f"""
            QTabWidget::pane {{
                background: {Colors.WHITE};
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                border-top-left-radius: 0;
                padding: 0;
                margin-top: -1px;
            }}
            
            QTabBar::tab {{
                background: #f8fafc;
                border: 2px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                color: #64748b;
                font-weight: 600;
                font-family: "Segoe UI", sans-serif;
                margin-right: 2px;
                padding: 12px 24px;
                min-width: 100px;
            }}
            
            QTabBar::tab:selected {{
                background: {Colors.WHITE};
                border-bottom: 2px solid {Colors.WHITE};
                color: {Colors.BLUE_PRIMARY};
                font-weight: 700;
            }}
            
            QTabBar::tab:hover:!selected {{
                background: #f1f5f9;
                color: #475569;
            }}
        """)

class StatusIndicator(QWidget):
    """Indicateur de statut coloré"""
    
    def __init__(self, status="inactive", size=12, parent=None):
        super().__init__(parent)
        
        self.status = status
        self.indicator_size = size
        self.setFixedSize(size, size)
        
        # Animation de pulsation
        self.pulse_animation = QPropertyAnimation(self, b"geometry")
        self.pulse_animation.setDuration(1000)
        self.pulse_animation.setEasingCurve(QEasingCurve.InOutSine)
        self.pulse_animation.setLoopCount(-1)  # Boucle infinie
    
    def paintEvent(self, event):
        """Dessine l'indicateur de statut"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        colors = {
            "active": "#10b981",      # Vert
            "inactive": "#6b7280",    # Gris
            "warning": "#f59e0b",     # Orange
            "error": "#ef4444",       # Rouge
            "processing": "#3b82f6"   # Bleu
        }
        
        color = QColor(colors.get(self.status, colors["inactive"]))
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        
        painter.drawEllipse(0, 0, self.indicator_size, self.indicator_size)
    
    def set_status(self, status):
        """Change le statut et met à jour l'affichage"""
        self.status = status
        self.update()
        
        # Animation pour les statuts actifs
        if status in ["active", "processing"]:
            self.start_pulse()
        else:
            self.stop_pulse()
    
    def start_pulse(self):
        """Démarre l'animation de pulsation"""
        original_rect = self.geometry()
        expanded_rect = QRect(
            original_rect.x() - 2,
            original_rect.y() - 2,
            original_rect.width() + 4,
            original_rect.height() + 4
        )
        
        self.pulse_animation.setStartValue(original_rect)
        self.pulse_animation.setEndValue(expanded_rect)
        self.pulse_animation.start()
    
    def stop_pulse(self):
        """Arrête l'animation de pulsation"""
        self.pulse_animation.stop()

class ModernCard(QFrame):
    """Carte moderne avec ombre et coins arrondis"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background: {Colors.WHITE};
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        # Effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 10))
        self.setGraphicsEffect(shadow)
        
        # Layout par défaut
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)
    
    def add_widget(self, widget):
        """Ajoute un widget à la carte"""
        self.layout.addWidget(widget)
    
    def add_title(self, title, subtitle=None):
        """Ajoute un titre à la carte"""
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 700;
                color: #1f2937;
                margin-bottom: 4px;
            }
        """)
        self.layout.addWidget(title_label)
        
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #6b7280;
                    margin-bottom: 12px;
                }
            """)
            self.layout.addWidget(subtitle_label)

class LoadingSpinner(QWidget):
    """Spinner de chargement animé"""
    
    def __init__(self, size=32, parent=None):
        super().__init__(parent)
        
        self.size = size
        self.setFixedSize(size, size)
        
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        self.timer.setInterval(50)  # 20 FPS
    
    def paintEvent(self, event):
        """Dessine le spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)
        
        # Dessiner les segments du spinner
        for i in range(8):
            alpha = 255 - (i * 30)
            if alpha < 0:
                alpha = 0
                
            color = QColor(Colors.BLUE_PRIMARY)
            color.setAlpha(alpha)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            
            painter.drawEllipse(
                self.size // 4,
                -self.size // 12,
                self.size // 6,
                self.size // 6
            )
            painter.rotate(45)
    
    def rotate(self):
        """Fait tourner le spinner"""
        self.angle = (self.angle + 15) % 360
        self.update()
    
    def start(self):
        """Démarre l'animation"""
        self.timer.start()
        self.show()
    
    def stop(self):
        """Arrête l'animation"""
        self.timer.stop()
        self.hide()

# ===== EXEMPLES D'UTILISATION =====

class ModernWidgetShowcase(QWidget):
    """Widget de démonstration des composants modernes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Widgets Modernes - Démonstration")
        self.setMinimumSize(800, 600)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title = AnimatedLabel("Composants UI Modernes")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 700;
                color: #1f2937;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title)
        title.fade_in()
        
        # Carte avec boutons
        button_card = ModernCard()
        button_card.add_title("Boutons Modernes", "Différents styles de boutons")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(ModernButton("Défaut", button_type="default"))
        button_layout.addWidget(ModernButton("Primaire", button_type="primary"))
        button_layout.addWidget(ModernButton("Succès", button_type="success"))
        button_layout.addWidget(ModernButton("Danger", button_type="danger"))
        
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        button_card.add_widget(button_widget)
        main_layout.addWidget(button_card)
        
        # Carte avec champs de saisie
        input_card = ModernCard()
        input_card.add_title("Champs de Saisie", "Inputs modernes avec animations")
        
        input_card.add_widget(ModernLineEdit("Nom d'utilisateur"))
        input_card.add_widget(ModernLineEdit("Email"))
        
        combo = ModernComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        input_card.add_widget(combo)
        
        main_layout.addWidget(input_card)
        
        # Carte avec indicateurs
        status_card = ModernCard()
        status_card.add_title("Indicateurs de Statut", "Status et chargement")
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Actif:"))
        status_layout.addWidget(StatusIndicator("active"))
        status_layout.addWidget(QLabel("Inactif:"))
        status_layout.addWidget(StatusIndicator("inactive"))
        status_layout.addWidget(QLabel("Traitement:"))
        status_layout.addWidget(StatusIndicator("processing"))
        status_layout.addWidget(LoadingSpinner(24))
        
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        status_card.add_widget(status_widget)
        
        main_layout.addWidget(status_card)
        
        # Démarrer les animations
        QTimer.singleShot(100, self._start_animations)
    
    def _start_animations(self):
        """Démarre les animations des indicateurs"""
        # Démarrer les spinners et indicateurs de statut
        for child in self.findChildren(StatusIndicator):
            if child.status in ["active", "processing"]:
                child.start_pulse()
        
        for child in self.findChildren(LoadingSpinner):
            child.start()

# ===== FONCTIONS UTILITAIRES =====

def create_modern_layout(spacing=12, margins=(16, 16, 16, 16)):
    """Crée un layout avec un espacement moderne"""
    layout = QVBoxLayout()
    layout.setSpacing(spacing)
    layout.setContentsMargins(*margins)
    return layout

def apply_modern_font(widget, size=14, weight=QFont.Normal):
    """Applique une police moderne à un widget"""
    from .font_utils import create_system_font
    font = create_system_font(size, weight)
    widget.setFont(font)

# Exportation des widgets principaux
__all__ = [
    'ModernButton', 'ModernLineEdit', 'ModernComboBox', 'ModernGroupBox',
    'ModernProgressBar', 'ModernSlider', 'AnimatedLabel', 'ModernTabWidget',
    'StatusIndicator', 'ModernCard', 'LoadingSpinner', 'ModernWidgetShowcase',
    'create_modern_layout', 'apply_modern_font'
] 