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
        self.close()

    def disappear(self):
        self.f -= 0.0002
        self.setWindowOpacity(self.f)

    def animate(self):
        self.move(self.x, self.y)
        self.y += 0.5


class WorkThread(QtCore.QThread):
    update = QtCore.pyqtSignal()
    vanish = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def __init__(self, mv):
        super(WorkThread, self).__init__()

    def run(self):
        while True:
            for i in range(30):
                time.sleep(0.01)
                self.update.emit()
            time.sleep(0.1)
            self.vanish.emit()
            time.sleep(0.1)
            self.finished.emit()
            return
