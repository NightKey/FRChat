# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'clirnt.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import socket
import ssl
import select
import errno, json, connector
from message import message

HEADERSIZE = 10
IP = ""
PORT = 0
username = None
client_socket = None
sending = False

def __init__():
    with open("client.ini", 'r') as f:
        data = json.load(f)
    global IP
    global PORT
    global username
    IP = data['ip']
    PORT = data['port']
    username = data['name']

class retriver(QtCore.QThread):
    return_value = QtCore.pyqtSignal(str)

    def run(self, first=False):
        while True:
            try:
                while True:
                    msg = connector.retrive(client_socket, HEADERSIZE, username)
                    if msg is False:
                        self.return_value.emit("CONNECTION TO THE SERVER WAS CLOSED")
                    else:
                        self.return_value.emit(msg.get_message_formated('> '))
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print("Reading error!")
                    print(str(e))
                    exit(0)
                continue
            except Exception as e:
                print("General error")
                print(str(e))
                exit(0)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, server_name):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(805, 555)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.My_Message = QtWidgets.QLineEdit(self.centralwidget)
        self.My_Message.setGeometry(QtCore.QRect(20, 490, 601, 20))
        self.My_Message.setObjectName("My_Message")
        self.Incoming_Message = QtWidgets.QTextEdit(self.centralwidget)
        self.Incoming_Message.setGeometry(QtCore.QRect(20, 10, 681, 471))
        self.Incoming_Message.setObjectName("Incoming_Message")
        self.Incoming_Message.setReadOnly(True)
        self.Send = QtWidgets.QPushButton(self.centralwidget)
        self.Send.setGeometry(QtCore.QRect(630, 490, 75, 23))
        self.Send.setObjectName("Send")
        self.Roll = QtWidgets.QPushButton(self.centralwidget)
        self.Roll.setGeometry(QtCore.QRect(710, 140, 75, 23))
        self.Roll.setObjectName("Roll")
        self.D_Num = QtWidgets.QSpinBox(self.centralwidget)
        self.D_Num.setGeometry(QtCore.QRect(760, 50, 41, 22))
        self.D_Num.setObjectName("D_Num")
        self.D_Type = QtWidgets.QSpinBox(self.centralwidget)
        self.D_Type.setGeometry(QtCore.QRect(760, 80, 41, 22))
        self.D_Type.setObjectName("D_Type")
        self.D_Mod = QtWidgets.QSpinBox(self.centralwidget)
        self.D_Mod.setGeometry(QtCore.QRect(760, 110, 41, 22))
        self.D_Mod.setObjectName("D_Mod")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(710, 50, 47, 13))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(710, 80, 31, 21))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(710, 110, 47, 21))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(716, 13, 71, 21))
        self.label_4.setObjectName("label_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 805, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow, server_name)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.Send.clicked.connect(self.send_message)
        self.Roll.clicked.connect(self.roll_dice)
        self.My_Message.returnPressed.connect(self.send_message)
        self.msg_ret = retriver()
        self.msg_ret.return_value.connect(self.retrive_msg)
        self.msg_ret.start()

    def retranslateUi(self, MainWindow, server_name):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", server_name))
        self.Send.setText(_translate("MainWindow", "Send"))
        self.Roll.setText(_translate("MainWindow", "Roll"))
        self.label.setText(_translate("MainWindow", "Number"))
        self.label_2.setText(_translate("MainWindow", "Type"))
        self.label_3.setText(_translate("MainWindow", "Modifyer"))
        self.label_4.setText(_translate("MainWindow", "Dice setup"))

    def retrive_msg(self, value):
        self.Incoming_Message.append(f"{value}")

    def send_message(self):
        if self.My_Message.text() != "":
            msg = message(False, HEADERSIZE)
            msg.set_msg(self.My_Message.text())
            msg.set_sender(username)
            self.msg_ret.terminate()
            connector.send(client_socket, HEADERSIZE, msg)
            self.msg_ret.start()
            self.My_Message.setText("")

    def roll_dice(self):
        if self.D_Num.value() != 0 and self.D_Type.value() != 0:
            dice = message(False, HEADERSIZE)
            dice.set_sender(username)
            dice.set_msg(f"roll {self.D_Num.value()}d{self.D_Type.value()}+{self.D_Mod.value()}")
            self.msg_ret.terminate()
            connector.send(client_socket, HEADERSIZE, dice)
            self.msg_ret.start()

def init_socket():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(True)

    context = ssl.create_default_context()
    client_socket = context.wrap_socket(client_socket, server_hostname='127.0.0.1')

    user_name = message(HEADER_SIZE=HEADERSIZE)
    user_name.set_sender(username)
    user_name.set_msg(username)
    if not connector.send(client_socket, HEADERSIZE, user_name):
        print("Error in the connection!")
        exit(2)

def main():
    init_socket()
    #Start UI
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, "FCChat - Client")
    MainWindow.show()
    exit(app.exec_())

if __name__=="__main__":
    __init__()
    main()