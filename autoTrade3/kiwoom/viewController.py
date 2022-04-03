import kiwoom.dataModel as dm

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *

form_class = uic.loadUiType("main_window.ui")[0]

class viewController(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        # self.setUI()
        # self.myModel = m_model
        print("뷰컨드롤러")

        # self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        # self.login()

        # self.kiwoom.OnEventConnect.connect(self.event_connect)
        # self.kiwoom.OnReceiveTrData.connect(self.receive_trData)

        # UI event Triger
        # self.searchItemButton.clicked.connect(self.searchItem)
        # self.buyPushButton.clicked.connect(self.itemBuy)
        # self.sellPushButton.clicked.connect(self.itemSell)

    def setUI(self):
        print("뷰컨드롤러")
        self.setupUi(self)

        column_head = ["00:지정가", "03:시장가", "05:조건부지정가", "06:최유리지정가", "07:최우선지정가", "10:지정가IOC",
                       "13:시장가IOC", "16:최유리IOC", "20:지정가FOK", "26:최유리FOK", "61:장전시장외종가"]
        self.gubuncomboBox.addItems(column_head)

        column_head = ["1:신규매수", "2:신규매도", "3:매수취소", "4:매도취소", "5:매수정정", "6:매도정정"]
        self.tradeGubuncomboBox.addItems(column_head)

    # def event_connect(self, nErrCode):
    #     if nErrCode == 0:
    #         self.statusbar.showMessage("로그인 성공")
    #         self.get_login_info()
    #         self.getItemList()
    #         self.getMyAccount()
    #     elif nErrCode == 100:
    #         print("사용자 정보교환 실패")
    #     elif nErrCode == 101:
    #         print("서버접속 실패")
    #     elif nErrCode == 102:
    #         print("버전처리 실패")
    #
    # def login(self):
    #     self.kiwoom.dynamicCall("CommConnect()")
    #
    # def get_login_info(self):
    #     accCnt = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "ACCOUNT_CNT")
    #     accList = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "ACCLIST")
    #     accList = accList.split(";")
    #     accList.pop()
    #     userId = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "USER_ID")
    #     userName = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
    #     keyBsec = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "KEY_BSECGB")
    #     firew = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "FIREW_SECGB")
    #     serverGubun = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "GetServerGubun")
    #
    #
    #     self.myModel.myLoginInfo = dm.DataModel.LoginInfo(accCnt,accList,userId,userName,keyBsec,firew,serverGubun)
    #
    #     self.statusbar.showMessage(self.myModel.myLoginInfo.getServerGubun())
    #
    #     self.accComboBox.addItems(accList)
    #
    #     print("나의이름:"+self.myModel.myLoginInfo.userName)
    #
    # # 종목리스트 요청
    # def getItemList(self):
    #     marketList = ["0", "10"]
    #     for marget in marketList:
    #         codeList = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", marget).split(";")
    #         for code in codeList:
    #             name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)",code)
    #             item = dm.DataModel.ItemInfo(code, name)
    #             self.myModel.itemList.append(item)
    #
    #     print(self.myModel.itemList[100].itemName)
    #
    # def searchItem(self):
    #     itemName = self.searchItemTextEdit.toPlainText()
    #     for item in self.myModel.itemList:
    #         if item.itemName == itemName:
    #             self.itemCodeTextEdit.setPlainText(item.itemCode)
    #             self.getItemInfo(item.itemCode)
    #             break
    #
    # # 현재가격 가지고 오기
    # def getItemInfo(self, code):
    #     self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드",  code)
    #     self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "주식기본정보요청", "opt10001", 0, "5000")
    #
    # def getMyAccount(self):
    #     account = self.accComboBox.currentText()
    #     self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", account)
    #     self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "")
    #     self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
    #     self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
    #     self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "계좌잔고평가내역", "opw00018", 0, "5100")
    #
    #
    # def receive_trData(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, nDataLength, sErrorCode, sMessage, sSplmMsg):
    #     if sTrCode == "opt10001":
    #         if sRQName == "주식기본정보요청":
    #             currentPrice = abs(int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "현재가")))
    #             self.priceSpinBox.setValue(currentPrice)
    #     if sTrCode == "opw00018":
    #         if sRQName == "계좌잔고평가내역":
    #
    #             column_head = ["종목번호", "종목명", "보유수량", "매입가", "현재가", "평가손익", "수익률(%)"]
    #             colCount = len(column_head)
    #             rowCount = self.kiwoom.dynamicCall("GetRepeatCnt(QString,QString)", sTrCode, sRQName)
    #
    #             self.stockListTableWidget.setColumnCount(colCount)
    #             self.stockListTableWidget.setRowCount(rowCount)
    #             self.stockListTableWidget.setHorizontalHeaderLabels(column_head)
    #
    #             totalBuyingPrice = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액"))
    #             currentTotalPrice = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가금액"))
    #             balanceAssset = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "추정예탁자산"))
    #             totalEstimateProfit = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액"))
    #
    #
    #             self.totalBuyPriceLabel.setText(str(totalBuyingPrice))
    #             # self.totalBuyingPriceLabel.setText(str(totalBuyingPrice))
    #             self.balanceAsssetLabel.setText(str(balanceAssset))
    #             self.totalEstimateProfitLabel.setText(str(totalEstimateProfit))
    #
    #             for index in range(rowCount):
    #                 itemCode = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "종목번호").strip(" ").strip("A")
    #                 itemName = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "종목명")
    #                 amount = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "보유수량"))
    #                 buyPrice = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "매입가"))
    #                 currentPrice = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "현재가"))
    #                 estimateProfit = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "평가손익")
    #                 profitRate = float(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "수익률(%)"))
    #
    #                 stoctBalance = dm.DataModel.StockBalance(itemCode, itemName, amount, buyPrice, currentPrice, estimateProfit, profitRate)
    #                 self.myModel.myStockBalanceList.append(stoctBalance)
    #
    #                 self.stockListTableWidget.setItem(index, 0, QTableWidgetItem(str(itemCode)))
    #                 self.stockListTableWidget.setItem(index, 1, QTableWidgetItem(str(itemName)))
    #                 self.stockListTableWidget.setItem(index, 2, QTableWidgetItem(str(amount)))
    #                 self.stockListTableWidget.setItem(index, 3, QTableWidgetItem(str(buyPrice)))
    #                 self.stockListTableWidget.setItem(index, 4, QTableWidgetItem(str(currentPrice)))
    #                 self.stockListTableWidget.setItem(index, 5, QTableWidgetItem(str(estimateProfit)))
    #                 self.stockListTableWidget.setItem(index, 6, QTableWidgetItem(str(profitRate)))
    #
    #
    # #매수주문
    # def itemBuy(self):
    #     print("매수버튼클릭")
    #     acc = self.accComboBox.currentText()
    #     code = self.itemCodeTextEdit.toPlainText()
    #     amount = int(self.volumeSpinBox.value())
    #     price = int(self.priceSpinBox.value())
    #     hogaGb = self.tradeGubuncomboBox.currentText()[0:2]
    #
    #     self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["주식주문", 6000, acc, 1, code, amount, price, hogaGb, ""])
    #
    # def itemSell(self):
    #     print("매도버튼클릭")
    #     acc = self.accComboBox.currentText()
    #     code = self.itemCodeTextEdit.toPlainText()
    #     amount = int(self.volumeSpinBox.value())
    #     price = int(self.priceSpinBox.value())
    #     hogaGb = self.tradeGubuncomboBox.currentText()[0:2]
    #
    #     self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["주식주문", 6000, acc, 2, code, amount, price, hogaGb, ""])

