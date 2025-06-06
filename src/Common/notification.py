###############################
#                             #
#  Coded By: Saurabh Joshi    #
#  Original: 12/10/12         #
#  Date Modified: 20/05/18    #
#  modif by: Fadiga Ibrahima  #
#  File: Notification System  #
###############################
import time

from PyQt5 import QtCore, QtWidgets


class Notification(QtWidgets.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, mssg, parent=None, type_mssg="", *args, **kwargs):
        super(Notification, self).__init__(parent=parent, *args, **kwargs)

        self.mssg = str(mssg)
        self.workThread = None
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        if type_mssg == "success":
            background = "green"
        elif type_mssg == "error":
            background = "red"
        elif type_mssg == "warning":
            background = "grey"
        else:
            background = "black"

        css = """ color: white;background: {}; """.format(background)
        self.setStyleSheet(css)
        self.create_notification()
        self.show()

    def create_notification(self):
        self.x = 2
        self.y = 1
        self.f = 1.0
        self.workThread = WorkThread(self)
        self.workThread.update.connect(self.animate, QtCore.Qt.QueuedConnection)
        self.workThread.vanish.connect(self.disappear, QtCore.Qt.QueuedConnection)
        self.workThread.finished.connect(self.done, QtCore.Qt.QueuedConnection)

        self.workThread.start()

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(QtWidgets.QLabel(self.mssg))
        self.setLayout(vbox)

    def done(self):
        self.cleanup()
        self.close()
        
    def cleanup(self):
        """Nettoie les ressources avant la fermeture"""
        try:
            if self.workThread and self.workThread.isRunning():
                self.workThread.stop()
                if not self.workThread.wait(1000):  # Attendre 1 seconde max
                    self.workThread.terminate()
                    self.workThread.wait()
        except Exception as e:
            print(f"Erreur lors du nettoyage de la notification: {e}")

    def disappear(self):
        self.f -= 0.0002
        self.setWindowOpacity(self.f)

    def animate(self):
        self.move(self.x, self.y)
        self.y += 1

    def closeEvent(self, event):
        """Override closeEvent pour nettoyer les threads"""
        self.cleanup()
        super().closeEvent(event)


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
