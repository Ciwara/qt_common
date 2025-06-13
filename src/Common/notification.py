###############################
#                             #
#  Coded By: Saurabh Joshi    #
#  Original: 12/10/12         #
#  Date Modified: 20/05/18    #
#  modif by: Fadiga Ibrahima  #
#  File: Notification System  #
###############################
import time
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QFont


class Notification(QtWidgets.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, mssg, parent=None, type_mssg="info", duration=3000, *args, **kwargs):
        super(Notification, self).__init__(parent=parent, *args, **kwargs)
        
        self.mssg = str(mssg)
        self.type_mssg = type_mssg
        self.duration = duration
        self.workThread = None
        
        # Configuration de la fenêtre
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Styles selon le type de message
        self.styles = {
            "success": {
                "bg": "#10b981",
                "border": "#059669",
                "icon": "✅"
            },
            "error": {
                "bg": "#ef4444",
                "border": "#dc2626",
                "icon": "❌"
            },
            "warning": {
                "bg": "#f59e0b",
                "border": "#d97706",
                "icon": "⚠️"
            },
            "info": {
                "bg": "#3b82f6",
                "border": "#2563eb",
                "icon": "ℹ️"
            }
        }
        
        # Style par défaut
        self.current_style = self.styles.get(type_mssg, self.styles["info"])
        
        self.create_notification()
        self.show()

    def create_notification(self):
        # Layout principal
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Label avec le message
        label = QtWidgets.QLabel(self.mssg)
        label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: 500;
            padding: 5px;
        """)
        
        # Bouton de fermeture
        close_btn = QtWidgets.QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
            }
        """)
        close_btn.clicked.connect(self.close_notification)
        
        layout.addWidget(label)
        layout.addWidget(close_btn)
        self.setLayout(layout)
        
        # Animation d'entrée
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Position initiale (hors écran)
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, 300, 50)
        start_pos = QPoint(screen.width(), screen.height() - 100)
        end_pos = QPoint(screen.width() - self.width() - 20, screen.height() - 100)
        
        self.move(start_pos)
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.start()
        
        # Timer pour la fermeture automatique
        QtCore.QTimer.singleShot(self.duration, self.close_notification)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Dessiner le fond avec coins arrondis
        path = QPainterPath()
        rect = QtCore.QRectF(self.rect())  # Conversion en QRectF
        path.addRoundedRect(rect, 10, 10)
        
        # Fond principal
        painter.fillPath(path, QColor(self.current_style["bg"]))
        
        # Bordure
        painter.setPen(QColor(self.current_style["border"]))
        painter.drawPath(path)

    def close_notification(self):
        # Animation de sortie
        self.animation.setDirection(QPropertyAnimation.Backward)
        self.animation.finished.connect(self.close)
        self.animation.start()

    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)
        
    def cleanup(self):
        """Nettoie les ressources avant la fermeture"""
        try:
            if self.workThread and self.workThread.isRunning():
                self.workThread.stop()
                if not self.workThread.wait(1000):
                    self.workThread.terminate()
                    self.workThread.wait()
        except Exception as e:
            print(f"Erreur lors du nettoyage de la notification: {e}")


class WorkThread(QtCore.QThread):
    update = QtCore.pyqtSignal()
    vanish = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def __init__(self, mv):
        super(WorkThread, self).__init__()
        self.should_stop = False

    def stop(self):
        """Arrête le thread proprement"""
        self.should_stop = True

    def run(self):
        try:
            # Animation initiale
            for i in range(30):
                if self.should_stop:
                    return
                time.sleep(0.01)
                self.update.emit()
                
            if self.should_stop:
                return
                
            time.sleep(0.1)
            self.vanish.emit()
            time.sleep(0.1)
            self.finished.emit()
        except Exception as e:
            print(f"Erreur dans WorkThread: {e}")
        finally:
            self.should_stop = True
