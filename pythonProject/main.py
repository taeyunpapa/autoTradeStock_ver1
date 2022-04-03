import sys

import self as self
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from PyQt5 import uic

from PyQt5.QAxContainer import *

form_class = uic.loadUiType("main_window.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setUI()
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICTrl.1")
        self.login()

    def setUI(self):
        self.setupUi(self)

    def login(self):
        self.kiwoom.dynamicCall("CommConnect()")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myApp = MyWindow()
    myApp.show()
    app.exec_()