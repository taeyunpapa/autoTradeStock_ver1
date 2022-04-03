import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from PyQt5 import uic
from PyQt5.QAxContainer import *

form_class = uic.loadUiType("main_window.ui")[0]


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setUI()


        def setUI(self):
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myApp = MyWindow()
    myApp.show()
    app.exec_()
