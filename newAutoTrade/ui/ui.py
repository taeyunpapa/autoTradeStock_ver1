from kiwoom.kiwoom import *

import sys
from PyQt5.QtWidgets import *

class Ui_class():
    def __init__(self):
        print("Ui클래스")

        # 초기화
        self.app = QApplication(sys.argv)

        self.kiwoom = Kiwoom()


        # 이벤트루프 (프로그램이 종료하지 않게 해줌)
        self.app.exec_()