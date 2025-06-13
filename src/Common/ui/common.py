#!/usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad
# Version 3.0 - Intégration thèmes modernes et améliorations UI

from datetime import date
from typing import Optional, Union, Any

from PyQt5.QtCore import QSize, QSortFilterProxyModel, Qt, QBasicTimer, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QDoubleValidator,
    QFont,
    QIcon,
    QIntValidator,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
    QPixmap,
    QRadialGradient,
    QFontMetrics,
)
from PyQt5.QtWidgets import (
    QComboBox,
    QCommandLinkButton,
    QCompleter,
    QDateTimeEdit,
    QDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTabBar,
    QTextEdit,
    QToolButton,
    QWidget,
    QFrame,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
)

from ..periods import Period
from .statusbar import GStatusBar

try:
    from ..cstatic import CConstants
except Exception as e:
    print(e)


class FMainWindow(QMainWindow):
    """Fenêtre principale moderne avec support complet des thèmes"""
    
    themeChanged = pyqtSignal(str)  # Signal émis lors du changement de thème
    
    def __init__(self, parent=None, *args, **kwargs):
        QMainWindow.__init__(self)
        print("🚀 FMainWindow v3.0 - Mode moderne activé avec succès")
        
        # Configuration de base
        self.current_theme = "light_modern"  # Thème par défaut
        self._setup_window()
        self._setup_theme_system()
        self._setup_animations()
        
        # Configuration existante
        try:
            self.setWindowIcon(
                QIcon.fromTheme(f"logo", QIcon(f"{CConstants.img_media}logo.png"))
            )
            self.setWindowTitle(CConstants.APP_NAME)
            self.setWindowIcon(QIcon(CConstants.APP_LOGO))
        except:
            print("⚠️ Configuration des icônes échouée - mode dégradé activé")
        
        # StatusBar moderne
        self.statusbar = GStatusBar(self)
        self.setStatusBar(self.statusbar)
        
        # Dimensions et redimensionnement
        self.wc = self.width()
        self.hc = self.height()
        self.resize(self.wc, self.hc)
        
    def _setup_window(self):
        """Configuration moderne de la fenêtre"""
        # Fenêtre moderne avec coins arrondis sur les systèmes supportés
        self.setMinimumSize(800, 600)
        
        # Ombres modernes pour la fenêtre
        if hasattr(self, 'setWindowFlag'):
            try:
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(20)
                shadow.setColor(QColor(0, 0, 0, 60))
                shadow.setOffset(0, 10)
                # Note: L'ombre de fenêtre est gérée par l'OS moderne
            except Exception:
                pass
                
    def _setup_theme_system(self):
        """Configuration du système de thèmes"""
        try:
            from .themes.styles import get_available_themes
            self.available_themes = get_available_themes()
            self.apply_theme(self.current_theme)
        except ImportError:
            print("🎨 Système de thèmes non disponible - utilisation du style par défaut")
            
    def _setup_animations(self):
        """Configuration des animations modernes"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def apply_theme(self, theme_key: str):
        """Applique un thème moderne à la fenêtre"""
        try:
            from .themes.styles import get_theme_style
            style = get_theme_style(theme_key)
            self.setStyleSheet(style)
            self.current_theme = theme_key
            self.themeChanged.emit(theme_key)
            print(f"🎨 Thème appliqué avec succès: {theme_key}")
            
            # Appliquer le thème à tous les widgets enfants
            self._apply_theme_to_children()
            
        except Exception as e:
            print(f"❌ Erreur lors de l'application du thème {theme_key}: {e}")
            
    def _apply_theme_to_children(self):
        """Applique le thème à tous les widgets enfants"""
        for widget in self.findChildren(QWidget):
            if hasattr(widget, 'apply_theme'):
                widget.apply_theme(self.current_theme)
                
    def get_current_theme(self) -> str:
        """Retourne le thème actuel"""
        return self.current_theme
        
    def get_available_themes(self) -> dict:
        """Retourne les thèmes disponibles"""
        return getattr(self, 'available_themes', {})

    def set_window_title(self, page_name):
        self.setWindowTitle(" > ".join([CConstants.APP_NAME, page_name]))

    def resizeEvent(self, event):
        """lancé à chaque redimensionnement de la fenêtre"""
        # trouve les dimensions du container
        self.wc = self.width()
        self.hc = self.height()

    def change_context(self, context_widget, *args, **kwargs):
        # instanciate context
        # print("change_context Window")
        self.view_widget = context_widget(parent=self, *args, **kwargs)
        # attach context to window
        self.setCentralWidget(self.view_widget)

    def open_dialog(self, dialog, modal=False, opacity=1, *args, **kwargs):
        d = dialog(parent=self, *args, **kwargs)
        d.setModal(modal)
        # d.setWindowFlags(Qt.FramelessWindowHint)
        d.setWindowOpacity(opacity)
        d.exec_()

    def logout(self):
        from ..models import Owner
        for ur in Owner.select().where(Owner.islog):
            ur.islog = False
            ur.save()


    def exit(self):   
        print("Fermeture de l'application")
        from ..models import Settings
        print("settings", Settings.select().where(Settings.id == 1).first())
        settings = Settings.select().where(Settings.id == 1).first()
        if not settings.is_login:
            print("logout")
            self.logout()
        import sys
        self.close()
        sys.exit(0)

    def Notify(self, mssg="👋 Bonjour", type_mssg="info"):
        """Affiche une notification moderne avec émojis"""
        from ..notification import Notification

        # Ajouter des émojis selon le type de message
        if not any(emoji in mssg for emoji in ["🎉", "✅", "⚠️", "❌", "ℹ️", "💡", "🔔"]):
            if type_mssg == "success":
                mssg = f"✅ {mssg}"
            elif type_mssg == "warning":
                mssg = f"⚠️ {mssg}"
            elif type_mssg == "error":
                mssg = f"❌ {mssg}"
            elif type_mssg == "info":
                mssg = f"ℹ️ {mssg}"
            else:
                mssg = f"🔔 {mssg}"

        self.notify = Notification(mssg=mssg, type_mssg=type_mssg)


class FWidget(QWidget):
    """Widget de base moderne avec support des thèmes"""
    
    def __init__(self, parent=None, *args, **kwargs):
        QWidget.__init__(self, parent=parent, *args, **kwargs)
        self.pp = parent
        self.current_theme = "light_modern"
        
        # Auto-application du thème si le parent en a un
        self._inherit_parent_theme()
        
        # Configuration moderne
        self._setup_modern_features()

    def _inherit_parent_theme(self):
        """Hérite automatiquement du thème du parent"""
        if hasattr(self.pp, 'get_current_theme'):
            try:
                self.current_theme = self.pp.get_current_theme()
                self.apply_theme(self.current_theme)
            except Exception as e:
                print(f"⚠️ Erreur lors de l'héritage du thème: {e}")

    def _setup_modern_features(self):
        """Configuration des fonctionnalités modernes"""
        # Activation des effets visuels modernes
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
    def apply_theme(self, theme_key: str):
        """Applique un thème à ce widget"""
        try:
            from .themes.styles import get_theme_style
            # S'assurer que current_theme existe
            if not hasattr(self, 'current_theme'):
                self.current_theme = "light_modern"
            # Appliquer seulement si le thème a changé
            if theme_key != self.current_theme:
                style = get_theme_style(theme_key)
                self.setStyleSheet(style)
                self.current_theme = theme_key
                self.update()  # Force le rafraîchissement visuel
        except Exception as e:
            print(f"❌ Erreur lors de l'application du thème au widget: {e}")

    def page_names(self, app_name, txt):
        self.parentWidget().setWindowTitle("{} | {}".format(app_name, txt.upper()))

    def refresh(self):
        """Méthode de rafraîchissement - peut être surchargée"""
        pass

    def change_main_context(self, context_widget, *args, **kwargs):
        # print("change_main_context")
        return self.parentWidget().change_context(context_widget, *args, **kwargs)

    def open_dialog(self, dialog, modal=False, *args, **kwargs):
        return self.parentWidget().open_dialog(dialog, modal=modal, *args, **kwargs)
        
    def get_current_theme(self) -> str:
        """Retourne le thème actuel du widget"""
        if not hasattr(self, 'current_theme'):
            self.current_theme = "light_modern"
        return self.current_theme


class FDialog(QDialog, FWidget):
    def __init__(self, parent=None, *args, **kwargs):
        QDialog.__init__(self, parent=parent, *args, **kwargs)
        
        # S'assurer que le dialogue hérite automatiquement du thème de l'application
        self.ensure_theme_inheritance()

    def page_names(self, app_name, txt):
        self.setWindowTitle("{} | {}".format(app_name, txt.upper()))
    
    def ensure_theme_inheritance(self):
        """S'assure que ce dialogue hérite du thème de l'application"""
        try:
            from .theme_utils import ensure_dialog_theme_inheritance
            ensure_dialog_theme_inheritance(self)
        except ImportError:
            # Si theme_utils n'est pas disponible, essayer d'hériter du style de l'application
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance()
                if app and app.styleSheet():
                    # Le dialogue hérite automatiquement, mais on force le rafraîchissement
                    self.update()
            except Exception:
                pass  # Ignorer silencieusement les erreurs pour ne pas casser l'application


class PyTextViewer(QTextEdit):
    # Initialise the instance.
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)

        self.setReadOnly(True)


class TabPane(QTabBar):
    def __init__(self, parent=None):
        super(TabPane, self).__init__(parent)

    def addBox(self, box):
        self.setLayout(box)


class FLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(FLabel, self).__init__(*args, **kwargs)
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        # self.setFont(font)
        self.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)


class FRLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(FRLabel, self).__init__(*args, **kwargs)
        # self.setFont(QFont("Times New Roman", 50))
       

        self.setAlignment(Qt.AlignVCenter | Qt.AlignRight)


class FPageTitle(FLabel):
    def __init__(self, *args, **kwargs):
        super(FPageTitle, self).__init__(*args, **kwargs)
        # self.setFont(QFont("Times New Roman", 50))
        self.setAlignment(Qt.AlignCenter)



class FBoxTitle(FLabel):
    def __init__(self, *args, **kwargs):
        super(FBoxTitle, self).__init__(*args, **kwargs)
        self.setFont(QFont("Times New Roman", 12, QFont.Bold, True))
        self.setAlignment(Qt.AlignLeft)


class ErrorLabel(FLabel):
    def __init__(self, text, parent=None):
        FLabel.__init__(self, text, parent)
        font = QFont()
        self.setFont(font)
        red = QColor(Qt.red)
        palette = QPalette()
        palette.setColor(QPalette.WindowText, red)
        self.setPalette(palette)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)


class FormLabel(FLabel):
    def __init__(self, text, parent=None):
        FLabel.__init__(self, text, parent)
        font = QFont()
        font.setBold(True)
        self.setFont(font)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)


class QBadgeButton(QPushButton):
    def __init__(self, icon=None, text=None, parent=None):
        if icon:
            QPushButton.__init__(self, icon, text, parent)
        elif text:
            QPushButton.__init__(self, text, parent)
        else:
            QPushButton.__init__(self, parent)

        self.badge_counter = 0
        self.badge_size = 25

        self.redGradient = QRadialGradient(
            0.0, 0.0, 17.0, self.badge_size - 3, self.badge_size - 3
        )
        self.redGradient.setColorAt(0.0, QColor(0xE0, 0x84, 0x9B))
        self.redGradient.setColorAt(0.5, QColor(0xE9, 0x34, 0x43))
        self.redGradient.setColorAt(1.0, QColor(0xDC, 0x0C, 0x00))

    def setSize(self, size):
        self.badge_size = size

    def setCounter(self, counter):
        self.badge_counter = counter
        self.update()

    def paintEvent(self, event):
        QPushButton.paintEvent(self, event)
        p = QPainter(self)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.setRenderHint(QPainter.Antialiasing)

        if self.badge_counter > 0:
            point = self.rect().topRight()
            self.drawBadge(
                p,
                point.x() - self.badge_size - 1,
                point.y() + 1,
                self.badge_size,
                str(self.badge_counter),
                QBrush(self.redGradient),
            )

    def fillEllipse(self, painter, x, y, size, brush):
        path = QPainterPath()
        path.addEllipse(x, y, size, size)
        painter.fillPath(path, brush)

    def drawBadge(self, painter, x, y, size, text, brush):
        painter.setFont(QFont(painter.font().family(), 11, QFont.Bold))

        while (size - painter.fontMetrics().width(text)) < 10:
            pointSize = painter.font().pointSize() - 1
            weight = QFont.Normal if (pointSize < 8) else QFont.Bold
            painter.setFont(
                QFont(painter.font().family(), painter.font().pointSize() - 1, weight)
            )

        shadowColor = QColor(0, 0, 0, size)
        self.fillEllipse(painter, x + 1, y, size, shadowColor)
        self.fillEllipse(painter, x - 1, y, size, shadowColor)
        self.fillEllipse(painter, x, y + 1, size, shadowColor)
        self.fillEllipse(painter, x, y - 1, size, shadowColor)

        painter.setPen(QPen(Qt.white, 2))
        self.fillEllipse(painter, x, y, size - 3, brush)
        painter.drawEllipse(x, y, size - 3, size - 3)

        painter.setPen(QPen(Qt.white, 1))
        painter.drawText(x, y, size - 2, size - 2, Qt.AlignCenter, text)


class QToolBadgeButton(QToolButton):
    def __init__(self, parent=None):
        QToolButton.__init__(self, parent)

        self.badge_counter = 0
        self.badge_size = 5

        self.redGradient = QRadialGradient(
            0.0, 0.0, 17.0, self.badge_size - 3, self.badge_size - 3
        )
        self.redGradient.setColorAt(0.0, QColor(0xE0, 0x84, 0x9B))
        self.redGradient.setColorAt(0.5, QColor(0xE9, 0x34, 0x43))
        self.redGradient.setColorAt(1.0, QColor(0xDC, 0x0C, 0x00))

    def setSize(self, size):
        self.badge_size = size

    def setCounter(self, counter):
        self.badge_counter = counter

    def paintEvent(self, event):
        QToolButton.paintEvent(self, event)
        p = QPainter(self)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.setRenderHint(QPainter.Antialiasing)
        if self.badge_counter > 0:
            point = self.rect().topRight()
            self.drawBadge(
                p,
                point.x() - self.badge_size,
                point.y(),
                self.badge_size,
                str(self.badge_counter),
                QBrush(self.redGradient),
            )

    def fillEllipse(self, painter, x, y, size, brush):
        path = QPainterPath()
        path.addEllipse(x, y, size, size)
        painter.fillPath(path, brush)

    def drawBadge(self, painter, x, y, size, text, brush):
        painter.setFont(QFont(painter.font().family(), 11, QFont.Bold))

        while (size - painter.fontMetrics().width(text)) < 10:
            pointSize = painter.font().pointSize() - 1
            weight = QFont.Normal if (pointSize < 8) else QFont.Bold
            painter.setFont(
                QFont(painter.font().family(), painter.font().pointSize() - 1, weight)
            )

        shadowColor = QColor(0, 0, 0, size)
        self.fillEllipse(painter, x + 1, y, size, shadowColor)
        self.fillEllipse(painter, x - 1, y, size, shadowColor)
        self.fillEllipse(painter, x, y + 1, size, shadowColor)
        self.fillEllipse(painter, x, y - 1, size, shadowColor)

        painter.setPen(QPen(Qt.white, 2))
        self.fillEllipse(painter, x, y, size - 3, brush)
        painter.drawEllipse(x, y, size - 2, size - 2)

        painter.setPen(QPen(Qt.white, 1))
        painter.drawText(x, y, size - 2, size - 2, Qt.AlignCenter, text)


class Button(QCommandLinkButton):
    """Bouton de base amélioré avec support des thèmes"""
    
    def __init__(self, *args, **kwargs):
        super(Button, self).__init__(*args, **kwargs)
        
        self.current_theme = "light_modern"
        self.setAutoDefault(True)
        self.setIcon(QIcon.fromTheme("", QIcon("")))
        self.setCursor(Qt.PointingHandCursor)
        
        # Amélioration de l'accessibilité
        self.setToolTip("Cliquez pour exécuter l'action")
        
        # Configuration moderne
        self._setup_modern_button()
        self._inherit_theme()
        
    def _setup_modern_button(self):
        """Configuration moderne du bouton"""
        self.setMinimumHeight(35)
        
        # Ombre légère
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
    def _inherit_theme(self):
        """Hérite du thème du parent si disponible"""
        if hasattr(self.parent(), 'get_current_theme'):
            try:
                self.apply_theme(self.parent().get_current_theme())
            except:
                pass
                
    def apply_theme(self, theme_key: str):
        """Applique un thème au bouton"""
        try:
            from .themes.styles import get_theme_colors
            colors = get_theme_colors(theme_key)
            
            primary_color = colors.get("primary", "#0d6efd")
            bg_color = colors.get("bg", "#ffffff")
            
            style = f"""
            QCommandLinkButton {{
                background-color: {primary_color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            QCommandLinkButton:hover {{
                background-color: {primary_color}dd;
                transform: translateY(-1px);
            }}
            QCommandLinkButton:pressed {{
                background-color: {primary_color}aa;
            }}
            """
            self.setStyleSheet(style)
            self.current_theme = theme_key
        except:
            pass


class MenuBtt(Button):
    def __init__(self, *args, **kwargs):
        super(MenuBtt, self).__init__(*args, **kwargs)
        self.setIcon(QIcon.fromTheme("", QIcon("")))

        css = """
            QCommandLinkButton {
                max-width:4em;
                border: 1px solid #0D00FF;
                font-size: 30px;
                border-top-left-radius: 5px;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
                background-color: #fff;
                color: #000;
                padding: 35px 30px 15px 32px;
                }
            QCommandLinkButton:hover {
                    background-color: #0095ff;
                    color: #FFF;
            }
            """
        # self.setStyleSheet(css)


class BttRond(Button):
    def __init__(self, *args, **kwargs):
        super(BttRond, self).__init__(*args, **kwargs)
        self.setIcon(QIcon.fromTheme("", QIcon("")))
        css = """
                border-radius:9px;
                border:1px solid #4b8f29;
                color:#ffffff;
                font-family:arial;
                font-size:13px;
                font-weight:bold;
                padding:6px 12px;

        """
        # self.setStyleSheet(css)


class DeletedBtt(Button):
    def __init__(self, *args, **kwargs):
        super(DeletedBtt, self).__init__(*args, **kwargs)
        self.setIcon(QIcon.fromTheme("edit-delete", QIcon("")))
        
        # Amélioration de l'accessibilité avec avertissement
        self.setToolTip("🗑️ Supprimer définitivement - Action irréversible")
        
        css = """
                background-color:#dc3545;
                border-radius:8px;
                border:1px solid #c82333;
                color:#ffffff;
                font-family:arial;
                font-size:15px;
                font-weight:bold;
                padding:8px 24px;
                text-decoration:none;
                """
        self.setStyleSheet(css)


class WarningBtt(Button):
    def __init__(self, *args, **kwargs):
        super(WarningBtt, self).__init__(*args, **kwargs)
        self.setIcon(
            QIcon.fromTheme(
                "save",
                QIcon(
                    "{img_media}{img}".format(
                        img_media=CConstants.img_media, img="warning.png"
                    )
                ),
            )
        )
        
        # Amélioration de l'accessibilité
        self.setToolTip("⚠️ Attention - Action nécessitant une vigilance particulière")
        
        css = """
                    background-color:#ffc107;
                    border-radius:8px;
                    border:1px solid #e0a800;
                    color:#000000;
                    font-family:arial;
                    font-size:15px;
                    font-weight:bold;
                    padding:8px 24px;
                    """
        self.setStyleSheet(css)


class ButtonSave(Button):
    def __init__(self, *args, **kwargs):
        super(ButtonSave, self).__init__(*args, **kwargs)

        self.setIcon(
            QIcon.fromTheme(
                "",
                QIcon(
                    "{img_media}{img}".format(
                        img_media=CConstants.img_media, img="save.png"
                    )
                ),
            )
        )
        
        # Amélioration de l'accessibilité
        self.setToolTip("💾 Sauvegarder les modifications")
        
        # Style moderne
        font = QFont()
        font.setBold(True)
        self.setFont(font)


class Button_menu(Button):
    def __init__(self, *args, **kwargs):
        super(Button_menu, self).__init__(*args, **kwargs)

        # self.setFont(QFont("Times New Roman", 20))
        # self.setStyleSheet("width: 20px;")
        self.setIconSize(QSize(80, 80))
        self.setFocusPolicy(Qt.TabFocus)
        font = QFont()
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(40)
        # font.setStrikeOut(False)
        # font.setKerning(True)
        # self.setFont(font)


class BttSmall(Button):
    def __init__(self, *args, **kwargs):
        super(BttSmall, self).__init__(*args, **kwargs)
        chart_count = len(self.text())
        # print(chart_count)
        self.setFixedWidth(chart_count + 45)
        # self.setFixedHeight(30)


class BttExport(Button):
    def __init__(self, img, parent=None):
        super(BttExport, self).__init__()

        self.pixmap = QPixmap(
            "{img_media}{img}".format(
                img_media=CConstants.img_cmedia, img="{}.png".format(img)
            )
        )
        self.setFixedHeight(85)
        self.setFixedWidth(85)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()


class BttExportXLSX(BttExport):
    def __init__(self, img):
        super(BttExportXLSX, self).__init__("xlsx")
        self.pixmap = QPixmap(
            "{img_media}{img}".format(
                img_media=CConstants.img_cmedia, img="{}.png".format(img)
            )
        )


class BttExportPDF(BttExport):
    def __init__(self, img):
        super(BttExportPDF, self).__init__("pdf")
        self.pixmap = QPixmap(
            "{img_media}{img}".format(
                img_media=CConstants.img_cmedia, img="{}.png".format(img)
            )
        )


# class FLineEdit(QLineEdit):
# textModified = QtCore.pyqtSignal(str, str)  # (before, after)

#     def __init__(self, contents='', parent=None):
#         super(FLineEdit, self).__init__(contents, parent)
#         self.returnPressed.connect(self.checkText)
#         self._before = contents

#     def focusInEvent(self, event):
#         if event.reason() != QtCore.Qt.PopupFocusReason:
#             self._before = self.text()
#         super(FLineEdit, self).focusInEvent(event)

#     def focusOutEvent(self, event):
#         if event.reason() != QtCore.Qt.PopupFocusReason:
#             self.checkText()
#         super(FLineEdit, self).focusOutEvent(event)

#     def checkText(self):
#         if self._before != self.text():
#             self._before = self.text()
#             self.textModified.emit(self._before, self.text())


class LineEdit(QLineEdit):

    """Accepter que des nombre positive"""

    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)


class IntLineEdit(LineEdit):
    """Champ de saisie pour nombres entiers positifs uniquement"""

    def __init__(self, parent=None):
        LineEdit.__init__(self, parent)
        self.setValidator(QIntValidator(self))
        self.setAlignment(Qt.AlignRight)
        self.setText(self.text().replace(" ", ""))
        
        # Amélioration de l'accessibilité
        self.setToolTip("🔢 Saisissez uniquement des nombres entiers positifs")
        self.setPlaceholderText("0")


class FloatLineEdit(LineEdit):
    """Champ de saisie pour nombres décimaux positifs uniquement"""

    def __init__(self, parent=None):
        LineEdit.__init__(self, parent)
        self.setAlignment(Qt.AlignRight)
        self.setValidator(QDoubleValidator(0.1, 999999.99, 2, self))
        
        # Amélioration de l'accessibilité
        self.setToolTip("🔢 Saisissez des nombres décimaux (ex: 12.50)")
        self.setPlaceholderText("0.00")


class FPeriodHolder(object):
    def __init__(self, main_date=date.today(), *args, **kwargs):
        self.duration = "week"
        self.main_date = Period(
            main_date.year, self.duration, main_date.isocalendar()[1]
        )
        self.periods_bar = self.gen_bar_for(self.main_date)

    def gen_bar_for(self, main_date):
        return FPeriodTabBar(parent=self, main_date=self.main_date)

    def change_period(self, main_date):
        self.main_date = main_date

    def getmain_date(self):
        return self._main_date

    def setmain_date(self, value):
        self._main_date = value

    main_date = property(getmain_date, setmain_date)


class FormatDate(QDateTimeEdit):
    def __init__(self, *args, **kwargs):
        super(FormatDate, self).__init__(*args, **kwargs)
        self.setDisplayFormat("dd/MM/yyyy")
        self.setCalendarPopup(True)


class FPeriodTabBar(TabPane):
    def __init__(self, parent, main_date, *args, **kwargs):
        super(FPeriodTabBar, self).__init__(*args, **kwargs)

        for i in range(0, 3):
            self.addTab("{}".format(i))
        self.set_data_from(main_date)
        self.build_tab_list()

        self.currentChanged.connect(self.changed_period)

    def set_data_from(self, period):
        self.main_period = Period(period.year, period.duration, period.duration_number)
        self.periods = [
            self.main_period.previous,
            self.main_period.current,
            self.main_period.next,
        ]

    def build_tab_list(self):
        for index, period in enumerate(self.periods):
            self.setTabText(index, str(period.display_name()))
            self.setTabToolTip(index, str(period))
        self.setTabTextColor(1, QColor("SeaGreen"))
        self.setCurrentIndex(1)

    def changed_period(self, index):
        if index == -1 or index == 1:
            return False
        else:
            np = self.periods[index]
            self.set_data_from(np)
            self.build_tab_list()
            self.parentWidget().main_date = np
            self.parentWidget().change_period(np)


class EnterDoesTab(QWidget):
    def keyReleaseEvent(self, event):
        super(EnterDoesTab, self).keyReleaseEvent(event)
        if event.key() == Qt.Key_Return:
            self.focusNextChild()


class EnterTabbedLineEdit(LineEdit, EnterDoesTab):
    pass


class ExtendedComboBox(QComboBox):
    def __init__(self, parent=None):
        super(ExtendedComboBox, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)

        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)
        # connect signals
        self.lineEdit().textEdited[str].connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    # on selection of an item from the completer, select the corresponding
    # item from combobox

    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)

    # on model change, update the models of the filter and completer as well
    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    # on model column change, update the model column of the filter and
    # completer as well
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)


class WigglyWidget(QWidget):
    def __init__(self, test, parent=None):
        super(WigglyWidget, self).__init__(parent)

        self.setBackgroundRole(QPalette.Midlight)
        # print(test)
        newFont = self.font()
        newFont.setPointSize(newFont.pointSize() + 20)
        self.setFont(newFont)

        self.timer = QBasicTimer()
        self.text = str(test)  # Conversion directe en string

        self.step = 0
        self.timer.start(60, self)

    def paintEvent(self, event):
        sineTable = [
            0,
            38,
            71,
            92,
            100,
            92,
            71,
            38,
            0,
            -38,
            -71,
            -92,
            -100,
            -92,
            -71,
            -38,
        ]

        metrics = QFontMetrics(self.font())
        x = (self.width() - metrics.horizontalAdvance(self.text)) / 2
        y = (self.height() + metrics.ascent() - metrics.descent()) / 2
        color = QColor()

        painter = QPainter(self)

        for i in range(len(self.text)):
            index = (self.step + i) % 16
            color.setHsv((15 - index) * 16, 255, 191)
            painter.setPen(color)
            painter.drawText(
                int(x),
                int(y - ((sineTable[index] * metrics.height()) / 400)),
                self.text[i],
            )
            x += metrics.horizontalAdvance(self.text[i])

    def setText(self, newText):
        self.text = str(newText)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.step = self.step + 1
            self.update()
        else:
            super(WigglyWidget, self).timerEvent(event)


# ===== NOUVEAUX WIDGETS MODERNES =====

class ModernButton(QPushButton):
    """Bouton moderne avec effets visuels et support des thèmes"""
    
    def __init__(self, text="", icon=None, button_type="primary", parent=None):
        super().__init__(text, parent)
        
        self.button_type = button_type  # primary, secondary, success, warning, danger
        self.current_theme = "light_modern"
        self._is_hovered = False
        self._is_pressed = False
        
        # Configuration de base
        self._setup_button()
        self._setup_animations()
        
        if icon:
            self.setIcon(icon)
            
    def _setup_button(self):
        """Configuration du bouton moderne"""
        self.setMinimumHeight(40)
        self.setMinimumWidth(100)
        self.setCursor(Qt.PointingHandCursor)
        
        # Ombre moderne
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(0, 0, 0, 30))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
        
    def _setup_animations(self):
        """Configuration des animations"""
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def apply_theme(self, theme_key: str):
        """Applique un thème spécifique au bouton"""
        self.current_theme = theme_key
        self._update_button_style()
        
    def _update_button_style(self):
        """Met à jour le style selon le type et le thème"""
        try:
            from .themes.styles import get_theme_colors
            colors = get_theme_colors(self.current_theme)
            
            if self.button_type == "primary":
                bg_color = colors.get("primary", "#0d6efd")
                text_color = "#ffffff"
            elif self.button_type == "success":
                bg_color = "#28a745"
                text_color = "#ffffff"
            elif self.button_type == "warning":
                bg_color = "#ffc107"
                text_color = "#000000"
            elif self.button_type == "danger":
                bg_color = "#dc3545"
                text_color = "#ffffff"
            else:  # secondary
                bg_color = "#6c757d"
                text_color = "#ffffff"
                
            style = f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(bg_color)};
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(bg_color)};
                transform: translateY(0px);
            }}
            """
            self.setStyleSheet(style)
        except:
            pass
            
    def _lighten_color(self, color_hex: str) -> str:
        """Éclaircit une couleur hexadécimale"""
        try:
            color = QColor(color_hex)
            color = color.lighter(110)
            return color.name()
        except:
            return color_hex
            
    def _darken_color(self, color_hex: str) -> str:
        """Assombrit une couleur hexadécimale"""
        try:
            color = QColor(color_hex)
            color = color.darker(110)
            return color.name()
        except:
            return color_hex
            
    def enterEvent(self, event):
        """Animation d'entrée de souris"""
        self._is_hovered = True
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 4)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Animation de sortie de souris"""
        self._is_hovered = False
        self.shadow.setBlurRadius(10)
        self.shadow.setOffset(0, 2)
        super().leaveEvent(event)


class ModernCard(QFrame):
    """Carte moderne avec ombres et coins arrondis"""
    
    def __init__(self, parent=None, title="", content_widget=None):
        super().__init__(parent)
        
        self.current_theme = "light_modern"
        self._setup_card()
        self._setup_layout(title, content_widget)
        
    def _setup_card(self):
        """Configuration de la carte"""
        self.setFrameStyle(QFrame.NoFrame)
        
        # Ombre moderne
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        # Style de base
        self.setStyleSheet("""
        QFrame {
            background-color: white;
            border-radius: 12px;
            padding: 16px;
        }
        """)
        
    def _setup_layout(self, title, content_widget):
        """Configuration du layout de la carte"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 8px;
            }
            """)
            layout.addWidget(title_label)
            
        if content_widget:
            layout.addWidget(content_widget)
            
    def apply_theme(self, theme_key: str):
        """Applique un thème à la carte"""
        try:
            from .themes.styles import get_theme_colors
            colors = get_theme_colors(theme_key)
            
            bg_color = colors.get("bg", "#ffffff")
            text_color = "#2c3e50" if "light" in theme_key else "#e2e8f0"
            
            style = f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 12px;
                padding: 16px;
            }}
            QLabel {{
                color: {text_color};
            }}
            """
            self.setStyleSheet(style)
            self.current_theme = theme_key
        except:
            pass


class ModernLineEdit(QLineEdit):
    """Champ de saisie moderne avec animations"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        
        self.current_theme = "light_modern"
        self._setup_line_edit(placeholder)
        self._setup_animations()
        
    def _setup_line_edit(self, placeholder):
        """Configuration du champ de saisie"""
        if placeholder:
            self.setPlaceholderText(placeholder)
            
        self.setMinimumHeight(45)
        
        # Style de base
        apply_theme_to_widget(self, "input_field")
        
    def _setup_animations(self):
        """Configuration des animations"""
        self.focus_animation = QPropertyAnimation(self, b"geometry")
        self.focus_animation.setDuration(200)
        self.focus_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def apply_theme(self, theme_key: str):
        """Applique un thème au champ de saisie"""
        try:
            from .themes.styles import get_theme_colors
            colors = get_theme_colors(theme_key)
            
            bg_color = colors.get("bg", "#ffffff")
            primary_color = colors.get("primary", "#0d6efd")
            
            style = f"""
            QLineEdit {{
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: {bg_color};
            }}
            QLineEdit:focus {{
                border-color: {primary_color};
                box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
            }}
            """
            self.setStyleSheet(style)
            self.current_theme = theme_key
        except:
            pass


# ThemeSelector supprimé - utiliser le système centralisé theme_manager.py


# ===== UTILITAIRES MODERNES =====

class WidgetFactory:
    """Factory pour créer facilement des widgets modernes"""
    
    @staticmethod
    def create_button(text: str, button_type: str = "primary", icon: QIcon = None, parent=None) -> ModernButton:
        """Crée un bouton moderne"""
        return ModernButton(text=text, button_type=button_type, icon=icon, parent=parent)
    
    @staticmethod
    def create_card(title: str = "", content_widget: QWidget = None, parent=None) -> ModernCard:
        """Crée une carte moderne"""
        return ModernCard(parent=parent, title=title, content_widget=content_widget)
    
    @staticmethod
    def create_input(placeholder: str = "", parent=None) -> ModernLineEdit:
        """Crée un champ de saisie moderne"""
        return ModernLineEdit(placeholder=placeholder, parent=parent)
    
    # create_theme_selector supprimé - utiliser theme_manager.py
    
    @staticmethod
    def create_form_layout(fields: list, parent=None) -> QVBoxLayout:
        """Crée un layout de formulaire moderne"""
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        for field in fields:
            if isinstance(field, dict):
                label_text = field.get('label', '')
                widget_type = field.get('type', 'input')
                placeholder = field.get('placeholder', '')
                
                if label_text:
                    label = QLabel(label_text)
                    label.setStyleSheet("font-weight: 600; margin-bottom: 4px;")
                    layout.addWidget(label)
                
                if widget_type == 'input':
                    widget = WidgetFactory.create_input(placeholder, parent)
                elif widget_type == 'button':
                    widget = WidgetFactory.create_button(
                        field.get('text', 'Button'),
                        field.get('button_type', 'primary'),
                        parent=parent
                    )
                else:
                    continue
                    
                layout.addWidget(widget)
            else:
                layout.addWidget(field)
                
        return layout


# ThemeManager supprimé - utiliser le système centralisé theme_manager.py


# Fonctions de thèmes supprimées - utiliser theme_manager.py

# COMPATIBILITÉ - Fonctions obsolètes redirigées vers le système moderne
def get_complete_themes_list() -> dict:
    """
    Liste complète des 10 thèmes ultra-modernes disponibles
    
    Returns:
        dict: Dictionnaire complet des thèmes avec descriptions françaises
    """
    return {
        # Thèmes de base modernes
        "light_modern": "🌟 Moderne Clair",
        "dark_modern": "🌙 Moderne Sombre",
        
        # Thèmes colorés avancés
        "professional_blue": "💼 Professionnel Bleu",
        "nature_green": "🌿 Nature Verte",
        "warm_orange": "🔥 Chaleureux Orange",
        "creative_purple": "🎨 Créatif Violet",
        
        # Thèmes ultra-modernes révolutionnaires
        "glassmorphism": "💎 Glassmorphism",
        "neumorphism": "🎯 Neumorphism",
        "cyberpunk_neon": "⚡ Cyberpunk Néon",
        
        # Thème par défaut (pour compatibilité)
        "default": "📋 Défaut Système"
    }

# get_theme_categories supprimé - utiliser theme_manager.py

# Toutes les fonctions et classes de thèmes supprimées - utiliser theme_manager.py
