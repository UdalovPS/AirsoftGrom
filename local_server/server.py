from PyQt5.QtNetwork import *
from PyQt5.QtCore import pyqtSignal


class Server(QTcpServer):
    activate = pyqtSignal(int)

    def __init__(self, parent=None):
        QTcpServer.__init__(self, parent)
        self.socket = self.makeSocket()

    def makeSocket(self):
        print('server start')
        socket = QTcpSocket(self)
        socket.readyRead.connect(self.onSocketReadyRead)
        return socket

    def onSocketReadyRead(self):
        data = self.socket.readAll().__str__()
        int_data = int(data[2:-1])
        print(int_data)
        index = (int_data // 10) - 1
        self.activate.emit(int_data)

    def incomingConnection(self, socketDescriptor):
        self.socket.setSocketDescriptor(socketDescriptor)

