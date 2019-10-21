# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'clirnt.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import ssl, select, time, pickle, os, socket
import errno, json, connector
from message import message

HEADERSIZE = 10
IP = ""
PORT = 0
username = None
client_socket = None
sending = False
init_msg = None
debug = (False if os.sys.gettrace() == None else True)

def log(data):
    """Prints out debug information, if debugger is atached. (Else it would slow the program down signigicantly)
    """
    if debug:
        print(data)

def __init__():
    """initializes the program, with the init setups:
    ip - The IP address of the server we want to connect to
    port - The port number of the server we want to connect to
    name - The name of the client application
    """
    with open("client.ini", 'r') as f:
        data = json.load(f)
    global IP
    global PORT
    global username
    IP = data['ip']
    PORT = data['port']
    username = data['name']

incoming_messages = []

class retriver(QtCore.QThread):
    return_value = QtCore.pyqtSignal(str)
    """This class is the retriver part of the client. 
    It runs on a different thread than the GUI, and retrives messages without freezing it.
    """
    def run(self, first=False):
        while True:
            try:
                while True:
                    msg = connector.retrive(client_socket, HEADERSIZE, username)
                    if msg is False:
                        log("Connection closed")
                        self.return_value.emit("CONNECTION TO THE SERVER WAS CLOSED")
                        exit(0)
                    else:
                        incoming_messages.append(msg)
                        log(msg)
                        self.return_value.emit("")
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print("Reading error!")
                    print(str(e))
                    exit(1)
                continue
            except Exception as e:
                print("General error")
                print(str(e))
                exit(1)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, server_name):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(805, 555)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.My_Message = QtWidgets.QLineEdit(self.centralwidget)
        self.My_Message.setGeometry(QtCore.QRect(20, 490, 601, 20))
        self.My_Message.setObjectName("My_Message")
        self.Incoming_Message = QtWidgets.QListWidget(self.centralwidget)
        self.Incoming_Message.setGeometry(QtCore.QRect(20, 10, 681, 471))
        self.Incoming_Message.setObjectName("Incoming_Message")
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
        self.D_Mod.setMinimum(-20)
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
        self.Incoming_Message.itemClicked.connect(self.msg_select)
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
        self.load()

    def msg_select(self, item):
        if incoming_messages[item.type()]._has_file:
            pass
        else:
            flag = QtCore.QItemSelectionModel.SelectionFlag(0x0001)
            self.Incoming_Message.setCurrentItem(item, flag)

    def load(self):
        if init_msg != None:
            for msg in init_msg:
                log(f"Loaded message: {msg}")
                incoming_messages.append(msg)
                self.retrive_msg()

    def retrive_msg(self, msg=""):
        """This function updates the GUI from a new message.
        """
        if msg == "":
            icon = QtGui.QIcon().fromTheme("emblem-downloads")
            item = QtWidgets.QListWidgetItem(f"{incoming_messages[-1].get_date_time()} {incoming_messages[-1].get_message_formated('> ')}", type=(len(incoming_messages) - 1))
            item.setIcon(icon)
            self.Incoming_Message.addItem(item)
            log(f"'{item.text}' added to the list (item)")
            log("incoming_messages length: {}".format(len(incoming_messages)))
        else:
            log(f"'{msg}' added to the list (msg)")
            self.Incoming_Message.addItem(QtWidgets.QListWidgetItem(msg))
        self.Incoming_Message.scrollToBottom()

    def send_message(self):
        """This function get's called, when we press RETURN, or press the send button.
        It creates a message object, and calls the send function with it.
        """
        if self.My_Message.text() != "":
            self.send(self.My_Message.text())
            self.My_Message.setText("")

    def roll_dice(self):
        """This function gets called, when we roll. It creates a message object, and calls the send function with it.
        """
        if self.D_Num.value() != 0 and self.D_Type.value() != 0:
            op = '+' if self.D_Mod.value() >= 0 else ''
            self.send(f"roll {self.D_Num.value()}d{self.D_Type.value()}{op}{self.D_Mod.value()}")
            self.D_Num.setValue(0)
            self.D_Type.setValue(0)
            self.D_Mod.setValue(0)
    
    def send(self, data):
        """Stops the retriving, so we won't get OSError, and waits a little, so it has time to stop retriving, then sends the message.
        After a little wait, it restarts the retriving process...
        """
        msg = message(False, HEADERSIZE)
        msg.message = data
        msg.sender = username
        self.msg_ret.terminate()
        time.sleep(0.001)
        connector.send(client_socket, msg)
        time.sleep(0.001)
        self.msg_ret.start()

def init_socket():
    """initializes the connection with the remote server on the given port.
    !IMPORTANT!
    The server's certification.pem file must be in the folder certif, with the server's IP address.
    """
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(True)

    context = ssl.create_default_context(cafile='certif/Certification.pem') #FOR NOW? IT HAS TO BE NAMED CERTIFICATION!
    client_socket = context.wrap_socket(client_socket, server_hostname='furryresidency')
    #client_socket.setblocking(False)

    user_name = message(HEADERSIZE=HEADERSIZE)
    user_name.sender = username
    user_name.message = username
    if not connector.send(client_socket, user_name):
        print("Error in the connection!")
        exit(2)
    messages = connector.retrive(client_socket, HEADERSIZE, username)
    if not messages:
        print("Error in the connection!")
        exit(2)
    elif messages._has_file:
        messages.create_file(f"{username}.msg")
        tmp = []
        with open(f"{username}.msg", 'rb') as f:
            msgs = f.read(-1).split(b"\t\t||\n")
        for msg in msgs:
            if msg != b"":
                tmp.append(pickle.loads(msg))
        os.remove(f"{username}.msg")
        global init_msg
        init_msg = tmp

def main():
    init_socket()
    #Start UI
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, "FRChat - Client")
    MainWindow.show()
    exit(app.exec_())

if __name__=="__main__":
    __init__()
    main()