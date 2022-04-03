import sys
import viewController as vc
import dataModel as dm

from PyQt5.QtWidgets import *

class MyautoTradeApp():
    def __init__(self):
        print("자동매매프로그램")
        self.myDataModel = dm.DataModel()
        self.myViewController = vc.viewController(self.myDataModel)



if __name__ == "__main__":
    print("메인실행")
    app = QApplication(sys.argv)
    myApp = MyautoTradeApp()
    myApp.myViewController.show()
    app.exec_()

