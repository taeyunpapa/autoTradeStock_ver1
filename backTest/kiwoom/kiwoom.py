import os
import sys
import datetime

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *


class Kiwoom(QAxWidget):  # QAxWidget
    def __init__(self):
        super().__init__()

        ###############################UI##################################

        # UI event Triger
        # self.ui.searchItemButton.clicked.connect(self.searchItem)
        # self.ui.totalInit.clicked.connect(self.totalInit)
        # self.buyPushButton.clicked.connect(self.itemBuy)
        # self.sellPushButton.clicked.connect(self.itemSell)
        ##################################################################

        print("Kiwoom클래스")

        self.realType = RealType()

        ######이벤트 루프 모음#######
        self.event_login_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()
        ##########################



        ############### 테스트#############
        # self.isFirst = "Y"
        self.testfisrt = "Y"
        self.searchCnt = 0
        self.j = 0
        self.testFirst = "Y"
        self.testFirst2 = "Y"
        self.testFirst3 = "Y"
        #######스크린번호 모음#############

        self.screen_my_info = "2000"
        self.screen_calculator_stock = "4000"
        self.screen_real_stock = "5000"  # 종목별로 할당할 스크린번호
        self.screen_meme_stock = "6000"  # 종목별로 할당할 주문용 스크린 번호
        self.screen_start_stop_real = "1000"  # 장이 시작인지 끝인지
        ################################

        #######변수모음##############
        self.account_num = None
        self.market_open_f = None

        ###########################

        #######계좌관련 변수##########
        self.use_money = 0
        self.use_money_persent = 0.5
        #############################

        ############ 분봉만들기 변수 ##############
        currentDate = datetime.datetime.now()
        self.currentDay = currentDate.strftime("%Y%m%d")
        base = "20210210" + "090000"
        self.baseTime = datetime.datetime.strptime(base, "%Y%m%d%H%M%S")

        dongsihoga = "20210210" + "152000"
        self.dongsihogaTime = datetime.datetime.strptime(dongsihoga, "%Y%m%d%H%M%S")


        # self.firstbunbong="Y"
        self.firstsn=0

        self.bunbongNmSiga = None
        self.bunbongNmJongga = None
        self.bunbongNmGoga = None
        self.bunbongNmJuga = None
        #######################################

        ##########변수모음##############
        self.market_stock_list = {}
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        self.portfolio_stock_dict = {}
        self.portfolio_stock_buy = {}
        self.jango_dict = {}  # 잔고
        self.online_jango_dict = {}  # 실시간잔고
        self.jongmok1_hoga = {}  # 종목1 호가별 거래대금 모음
        self.jongmok2_hoga = {}  # 종목1 호가별 거래대금 모음
        self.jongmok3_hoga = {}  # 종목1 호가별 거래대금 모음
        self.jongmok4_hoga = {}  # 종목1 호가별 거래대금 모음
        self.jongmok5_hoga = {}  # 종목1 호가별 거래대금 모음

        self.price_sum = {}

        ##############################

        ########종목분석용############
        self.calcul_data = []
        self.itemList = []
        ############################

        self.get_ocx_instance()
        self.event_slot()
        #self.real_event_slot()

        self.signal_login_commConnect()
        # self.get_account_info()
        # self.detail_account_info()  # 예수금 가져오기
        # self.not_concluded_account()  # 미체결 요청
        self.getItemList()  # 종목코드가져오기
        self.read_code()  # 저장된 종목 파일 불러오기
        # self.detail_account_mystock()  # 계좌평가 잔고내역 가져오기

        self.screen_number_setting()  # 스크린번호를 할당

        # 장이 시작인지 끝인지 체크
        # print("장시작체크")
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '',
                         self.realType.REALTYPE['장시작시간']['장운영구분'], "0")

    def get_ocx_instance(self):
        # 키움오픈api를 사용하게 하는
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        # QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")

    # 종목리스트 요청
    def getItemList(self):
        marketList = ["0", "10"]
        for marget in marketList:
            codeList = self.dynamicCall("GetCodeListByMarket(QString)", marget).split(";")
            for code in codeList:
                name = self.dynamicCall("GetMasterCodeName(QString)", code)

                if name not in self.market_stock_list.keys():
                    self.market_stock_list.update({name: {}})

                self.market_stock_list[name].update({"종목코드": code})

    def searchItem(self, itemName):
        print("종목조회 : %s" % itemName)
        meme_code = None
        # itemName = self.ui.searchItemTextEdit.toPlainText()
        for item in self.market_stock_list.keys():
            if item == itemName:
                print(self.market_stock_list[item]['종목코드'])
                tempStockCode = self.market_stock_list[item]['종목코드']
                if tempStockCode not in self.portfolio_stock_dict.keys():
                    self.portfolio_stock_dict.update({tempStockCode: {"종목명": itemName,
                    "주문용스크린번호": self.screen_meme_stock, "익절횟수": 0,"처음":"Y", "순번":0,"분봉갯수":0,"매수분봉":0,
                    "매수조건":"", "매도가":0 , "매수포인트":"","손절횟수":0, "결과갯수":0, "만족갯수":0, "맥스거래량":0,"맥스고가":0
                    ,"만족갯수1":0, "전시가":0,"전종가":0, "첫분봉":"Y","isFirst":"Y", "매수갯수":0, "매수수량":0}})
                    print("매매종목추가:%s" % self.portfolio_stock_dict[tempStockCode]['종목명'])
                    meme_code = tempStockCode
                    # 틱데이터 받아오기
                    self.day_kiwoom_db(code=tempStockCode)

                break

        # for code in self.portfolio_stock_dict.keys():
        #     screen_num = self.portfolio_stock_dict[code]['주문용스크린번호']
        #     fids = self.realType.REALTYPE['주식체결']['체결시간']
        #
        #     self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1")
        #     print("실시간등록코드 : %s, 스크린번호: %s, fid번호: %s" % (code, screen_num, fids))

    # 이벤트 슬롯
    def event_slot(self):
        # 로그인 이벤트 슬롯
        self.OnEventConnect.connect(self.login_slot)

        # tr이벤트 슬롯
        self.OnReceiveTrData.connect(self.trData_slot)

        self.OnReceiveMsg.connect(self.msg_slot)

    # 실시간 이벤트 슬롯
   # def real_event_slot(self):
       # self.OnReceiveRealData.connect(self.realdata_slot)
        #self.OnReceiveChejanData.connect(self.chejan_slot)  ## 주문관련 슬롯

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.event_login_loop = QEventLoop()
        self.event_login_loop.exec_()

    def login_slot(self, errCode):
        print(errors(errCode))

        # 로그인이 완료되면 이벤트 로그인 루프를 끊어줌
        self.event_login_loop.exit()

    # 계좌번호 가져오기
    # def get_account_info(self):
    #     account_list = self.dynamicCall("GetLoginInfo(String)", "ACCNO")
    #     self.account_num = account_list.split(';')[0]
    #     print("보유계좌번호 %s" % self.account_num)

    # 저장된 종목 파일 불러오기
    def read_code(self):
        if os.path.exists("files/condition_stock.txt"):
            f = open("files/condition_stock.txt", "r", encoding="utf8")

            lines = f.readlines()
            for line in lines:
                if line != "":
                    ls = line.split("\n")  # 파일 쓸때 \t로 구분지어 놨기때문에

                    stock_nm = ls[0]

                    self.searchItem(stock_nm)

            f.close()  # 파일 닫기
            # print(self.portfolio_stock_dict)

    ########################### TR START #########################################
    ##############################################################################
    # def detail_account_info(self):
    #     print("예수금을 요청하는 부분")
    #
    #     self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
    #     self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
    #     self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
    #     self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
    #
    #     self.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)
    #
    #     # 이벤트루프 : 작업이 끝날때까지 다음 아래 코드 실행 안됨
    #     self.detail_account_info_event_loop.exec_()

    # 계좌평가잔고내역
    # def detail_account_mystock(self, sPrevNext="0"):
    #     print("계좌평가잔고내역요청")
    #     self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
    #     self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
    #     self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
    #     self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
    #
    #     self.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역", "opw00018", "0", self.screen_my_info)
    #
    #     self.detail_account_info_event_loop.exec_()

    # 미체결 내역
    # def not_concluded_account(self, sPrevNext="0"):
    #     print("미체결 요청")
    #     self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
    #     self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
    #     self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
    #
    #     self.dynamicCall("CommRqData(String, String, int, String)", "실시간미체결요청", "opt10075", sPrevNext,
    #                      self.screen_my_info)
    #
    #     self.detail_account_info_event_loop.exec_()

    # 일봉데이터 받아오기
    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        print("일봉데이터:%s" % code)

        QTest.qWait(500)  # 3.6초 딜레이(과도한 조회로 오류방지)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "틱범위", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식틱차트조회", "opt10079", sPrevNext,
                         self.screen_calculator_stock)

        # self.calculator_event_loop.exec_()

    def screen_number_setting(self):
        screen_overwrite = []

        # 계좌평가잔고내역에 있는 종목들
        for code in self.jango_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        # 미체결에 있는 종목들
        for order_no in self.not_account_stock_dict.keys():
            code = self.not_account_stock_dict[order_no]["종목코드"]
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        # 포트폴리오에 담겨있는 종목들
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        # 스크린번호 할당
        cnt = 0
        for code in screen_overwrite:

            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            # 스크린번호 하나당 종목 50개씩 넣는다
            if (cnt % 50) == 0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)

            if (cnt % 50) == 0:
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code].update({"스크린번호": str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.screen_meme_stock)})

            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update(
                    {code: {"스크린번호": str(self.screen_real_stock), "주문용스크린번호": str(self.screen_meme_stock)}})

            cnt += 1

            # print(self.portfolio_stock_dict)

    #############################TR END#########################################################
    ############################################################################################

    ##############################################################################################
    ##########################################요청한 결과 세팅#######################################
    ##############################################################################################

    def trData_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):  # 다음페이지 있으면 sPrevNext=2로옴/없으면 0 또는 null
        '''
        # tr요청을 받는 구역
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을때 지은 이른
        :param sTrCode: tr코드
        :param sRecordName: 사용안함
        :param sPrevNext: 다음페이지가 있는지
        :return:
        '''

        if sRQName == "예수금상세현황요청":
            deposit = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금"))

            print("예수금 %s" % deposit)

            self.use_money = deposit * self.use_money_persent
            self.use_money = self.use_money / 4

            ok_deposit = int(
                self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액"))
            print("출금가능금액 %s" % ok_deposit)

            ####결과 다 받았으니깐 이벤트 끊어줌
            self.detail_account_info_event_loop.exit()

        if sRQName == "계좌평가잔고내역":

            total_buy_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0,
                                               "총매입금액")
            total_buy_money_result = int(total_buy_money)

            print("총매입금액 %s" % total_buy_money_result)

            total_profit_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0,
                                                 "총수익률(%)")
            total_profit_rate_result = float(total_profit_rate)

            print("총수익률 %s" % total_profit_rate_result)

            # 보유종목가져오기
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # 보유종목갯수 : 한번에 20개씩밖에 조회안됨
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                # strip : 공백지우기
                code = code.strip()[1:]  # A12345 --> 12345

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                              "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "현재가")
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName,
                                                       i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                     "매매가능수량")

                if code in self.jango_dict.keys():
                    pass
                else:
                    self.jango_dict.update({code: {}})

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.jango_dict[code].update({"종목명": code_nm})
                self.jango_dict[code].update({"보유수량": stock_quantity})
                self.jango_dict[code].update({"매입가": buy_price})
                self.jango_dict[code].update({"수익률(%)": learn_rate})
                self.jango_dict[code].update({"현재가": current_price})
                self.jango_dict[code].update({"매입금액": total_chegual_price})
                self.jango_dict[code].update({"매매가능수량": possible_quantity})

                if code not in self.online_jango_dict.keys():
                    self.online_jango_dict.update({code: {}})

                self.online_jango_dict[code].update({"현재가": current_price})
                self.online_jango_dict[code].update({"종목코드": code})
                self.online_jango_dict[code].update({"보유수량": stock_quantity})
                self.online_jango_dict[code].update({"주문가능수량": possible_quantity})
                self.online_jango_dict[code].update({"매입단가": buy_price})
                self.online_jango_dict[code].update({"총매입가": total_chegual_price})
                self.online_jango_dict[code].update({"주문용스크린번호": self.screen_meme_stock})
                self.online_jango_dict[code].update({"종목명": code_nm})

                cnt += 1

            print("가지고있는 종목갯수 %s" % cnt)
            print("가지고있는 종목 %s" % self.online_jango_dict)

            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_info_event_loop.exit()  # 더이상 다음페이지가 없으니 연결 끊어줌


        elif sRQName == "실시간미체결요청":
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            for i in range(rows):
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                "주문상태")  # 접수/확인/체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "주문구분")  # 매도/매수/정정/취소
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "체결량")

                order_no = int(order_no.strip())
                code = code.strip()
                code_nm = code_nm.strip()
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')  # -매도 --> 매도
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no] = {}

                nasd = self.not_account_stock_dict[order_no]
                nasd.update({"종목코드": code})
                nasd.update({"종목명": code_nm})
                nasd.update({"주문상태": order_status})
                nasd.update({"주문수량": order_quantity})
                nasd.update({"주문가격": order_price})
                nasd.update({"주문구분": order_gubun})
                nasd.update({"미체결수량": not_quantity})
                nasd.update({"체결량": ok_quantity})

                print("미체결종목: %s" % self.not_account_stock_dict)

            self.detail_account_info_event_loop.exit()

        elif sRQName == "주식틱차트조회":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            # print("일봉데이터 요청 %s" % code)
            # print(self.portfolio_stock_dict[code])


            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            
            print("틱갯수 %s" % cnt)
            print(self.searchCnt)
            # 한번조회하면 900틱 데이터를 받을 수 있다.

            ticSn = self.searchCnt*900

            sum = 0
            for i in range(cnt):
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trading_date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "체결시간")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                row_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                Time = datetime.datetime.strptime(trading_date.strip(), "%Y%m%d%H%M%S")

               # print(trading_date)

                baseDate1 = "20210210000000"
                gijun1 = datetime.datetime.strptime(baseDate1, "%Y%m%d%H%M%S")
                baseDate2 = "20210211000000"
                gijun2 = datetime.datetime.strptime(baseDate2, "%Y%m%d%H%M%S")
                #if i==0:
                   # print(Time)

                if Time>gijun2:
                   # print(Time)
                    continue
                if gijun1 > Time :
                    # self.isFirst = "N"
                    self.portfolio_stock_dict[code].update({"isFirst":"N"})
                    break

                if self.portfolio_stock_dict[code]['첫분봉'] =="Y":
                    self.firstsn=i
                    self.portfolio_stock_dict[code].update({"첫분봉":"N"})
                    print(self.firstsn)
                    print(trading_date)


                data.append(i+ticSn-self.firstsn)
                data.append(current_price.strip())
                data.append(trading_date.strip())
                data.append(value.strip())
                data.append(code.strip())

                self.calcul_data.append(data.copy())

            if self.portfolio_stock_dict[code]['isFirst'] == "Y":
                if sPrevNext =="2":
                    if self.portfolio_stock_dict[code]['첫분봉'] =="N":
                        self.searchCnt += 1
                    self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else:
                print(self.calcul_data)
                self.back_test(code)


            # self.calculator_event_loop.exit()


    ###########################################################################################
    ########################################실시간 slot#########################################
    ###########################################################################################
    def back_test(self, sCode=None):
        # 체결시간
        print("aaa")
        #print(sCode)
        ticCnt=len(self.calcul_data)-1
        #print(ticCnt)

        self.jongmok1_hoga.update({sCode: {}})
        self.jongmok1_hoga[sCode].update({"최고누적량": 0})


        ticData = range(ticCnt, 0, -1)

        for tic in ticData:
            # print(self.calcul_data[i][2])
           # print(tic)
            p = str(self.calcul_data[tic][1])  # 현재가
            price = "P" + p
            g = int(self.calcul_data[tic][3])  # 거래량

            b=int(p)

            meme = self.calcul_data[tic][2]
            memeTime = datetime.datetime.strptime(meme, "%Y%m%d%H%M%S")

            if self.testfisrt =="Y":
                self.j = b # 토탈시가
                self.j = int(self.j)
                self.testfisrt = "N"





            timeline = range(0, 125)
            for i in timeline:
                startTime = self.baseTime + datetime.timedelta(minutes=(3 * i))
                endTime = self.baseTime + datetime.timedelta(minutes=(3 * (i + 1)))
                startTime1 = startTime + datetime.timedelta(minutes=1)
                # print(startTime,endTime,memeTime)

                if self.testFirst =="Y":
                    timerate1 = self.baseTime + datetime.timedelta(minutes=(3 * i + 1))
                    timerate2 = self.baseTime + datetime.timedelta(minutes=(3 * i + 2))

                    print(timerate1)
                    print(timerate2)
                    print(memeTime)

                    if timerate1 > memeTime:
                        print("AAA")
                    elif timerate2 > memeTime:
                        print("BBB")
                    self.testFirst = "N"


                if memeTime >= startTime and endTime > memeTime:

                    self.bunbongNmSiga = str(i) + "분봉시가"
                    self.bunbongNmJongga = str(i) + "분봉종가"
                    self.bunbongNmGoga = str(i) + "분봉고가"
                    self.bunbongNmJuga = str(i) + "분봉저가"
                    self.bunbongQuant = str(i) + "분봉거래량"

                    if self.portfolio_stock_dict[sCode]['처음'] == "Y":

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmSiga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmJongga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmGoga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmJuga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongQuant: g})

                        self.portfolio_stock_dict[sCode].update({"처음": "N"})

                        self.portfolio_stock_dict[sCode].update({"순번": i})

                    elif self.portfolio_stock_dict[sCode]['순번'] == i:

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmJongga: b})

                        if b > self.portfolio_stock_dict[sCode][self.bunbongNmGoga]:
                            self.portfolio_stock_dict[sCode].update({self.bunbongNmGoga: b})

                        if self.portfolio_stock_dict[sCode][self.bunbongNmJuga] > b:
                            self.portfolio_stock_dict[sCode].update({self.bunbongNmJuga: b})

                        sumQ = int(self.portfolio_stock_dict[sCode][self.bunbongQuant]) + g
                        self.portfolio_stock_dict[sCode].update({self.bunbongQuant: sumQ})

                    else:
                        self.portfolio_stock_dict[sCode].update({"순번": i})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmSiga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmJongga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmGoga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmJuga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongQuant: g})

                        cnt = self.portfolio_stock_dict[sCode]["분봉갯수"]

                        self.portfolio_stock_dict[sCode].update({"분봉갯수": cnt + 1})
                    break

                ############### 매수############################
            if self.portfolio_stock_dict[sCode]['분봉갯수'] > 3 and sCode not in self.portfolio_stock_buy.keys():

                # print(self.portfolio_stock_dict[sCode])

                bunsiga = self.portfolio_stock_dict[sCode][self.bunbongNmSiga]
                bunsiga = int(bunsiga)

                bunjongga = self.portfolio_stock_dict[sCode][self.bunbongNmJongga]
                bunjongga = int(bunjongga)

                bongcnt = self.portfolio_stock_dict[sCode]['분봉갯수']
                resultcnt = self.portfolio_stock_dict[sCode]['결과갯수']


                rate = (bunjongga - bunsiga) / bunsiga * 100
                midle = (bunjongga + bunsiga) / 2

                startSn = self.portfolio_stock_dict[sCode]['순번']-(bongcnt-resultcnt)
                endSn = self.portfolio_stock_dict[sCode]['순번']
                # print(self.portfolio_stock_dict[sCode]['순번'])
                # print(self.portfolio_stock_dict[sCode]['분봉갯수'])

                maxGoga = self.portfolio_stock_dict[sCode]['맥스고가']
                maxQuant = self.portfolio_stock_dict[sCode]['맥스거래량']
                mesuManjockCnt1 = self.portfolio_stock_dict[sCode]['만족갯수1']

                jogun = range(startSn, endSn)

                janunManjok = "Y"
                janunManjok2 = "Y"
                preunitsiga = self.portfolio_stock_dict[sCode]['전시가']
                preunitjonga = self.portfolio_stock_dict[sCode]['전종가']

                mesuManjockCnt1 = 0
                mesuManjockCnt2 = 0
                if bongcnt > resultcnt:
                    for z in jogun:
                        # print(z)
                        unitbunbongNmSiga = str(z) + "분봉시가"
                        unitbunbongNmJongga = str(z) + "분봉종가"
                        unitbunbongNmGoga = str(z) + "분봉고가"
                        unitbunbongQuant = str(z) + "분봉거래량"

                        if unitbunbongNmSiga not in self.portfolio_stock_dict[sCode]:
                            continue

                        unitsiga = self.portfolio_stock_dict[sCode][unitbunbongNmSiga]
                        unitsiga = int(unitsiga)
                        unitjonga = self.portfolio_stock_dict[sCode][unitbunbongNmJongga]
                        unitjonga = int(unitjonga)
                        # unitgoga = self.portfolio_stock_dict[sCode][unitbunbongNmGoga]
                        # unitgoga = int(unitgoga)
                        unitQuant = self.portfolio_stock_dict[sCode][unitbunbongQuant]

                        # print(unitsiga)
                        # print(unitjonga)

                        unitgoga = 0
                        if unitsiga > unitjonga:
                            unitgoga = unitsiga
                        else:
                            unitgoga = unitjonga

                        if unitgoga >= self.portfolio_stock_dict[sCode]['맥스고가']:
                            if self.testFirst2=="Y":
                                #print("AAA")
                                # print(unitgoga)
                                # print(self.portfolio_stock_dict[sCode]['맥스고가'])
                                self.testFirst2="N"
                            maxGoga = unitgoga
                            if self.portfolio_stock_dict[sCode]['만족갯수1'] < 16:
                                self.portfolio_stock_dict[sCode].update({"맥스고가": maxGoga})

                                mesuManjockCnt1 = 0
                                self.portfolio_stock_dict[sCode].update({"만족갯수1": mesuManjockCnt1})
                            # print(self.portfolio_stock_dict[sCode]['맥스고가'])
                        else:
                            if self.testFirst3 == "Y":
                                # print("bbb")
                                # print(unitgoga)
                                # print(self.portfolio_stock_dict[sCode]['맥스고가'])
                                self.testFirst3 = "N"
                            if self.portfolio_stock_dict[sCode]['맥스고가'] > unitgoga:
                                # print("ccc")
                                # print(unitgoga)
                                # print(self.portfolio_stock_dict[sCode]['맥스고가'])
                                # print(mesuManjockCnt1)
                                # print(z)
                                mesuManjockCnt1 += 1
                                self.portfolio_stock_dict[sCode].update({"만족갯수1": mesuManjockCnt1})

                        if unitQuant > maxQuant:
                            maxQuant = unitQuant
                            self.portfolio_stock_dict[sCode].update({"맥스거래량": maxQuant})

                        if z == 0:
                            if unitsiga == self.j and unitjonga >= self.j:
                                if unitjonga >= unitsiga:
                                    result = "A"
                                else:
                                    result = "B"
                            elif self.j == unitsiga and self.j > unitjonga:
                                if unitjonga >= unitsiga:
                                    result = "D"
                                else:
                                    result = "C"

                            preunitsiga = unitsiga
                            preunitjonga = unitjonga

                        else:
                            if unitjonga == preunitjonga:
                                result = result + "E"
                            else:
                                if unitsiga > self.j and unitjonga > self.j:
                                    if preunitsiga > preunitjonga:

                                        if unitsiga > unitjonga:
                                            if unitsiga > preunitsiga and unitjonga > preunitjonga:
                                                result = result + "A"
                                            elif preunitsiga > unitsiga and preunitjonga > unitjonga:
                                                result = result + "B"
                                            elif preunitsiga == unitsiga and preunitjonga == unitjonga:
                                                result = result + "E"
                                            else:
                                                if unitjonga > preunitjonga:
                                                    result = result + "a"
                                                else:
                                                    result = result + "B"



                                        elif unitjonga >= unitsiga:

                                            if unitjonga == unitsiga and unitsiga == preunitjonga:
                                                result = result + "E"
                                            elif unitjonga > preunitsiga and unitsiga > preunitjonga:
                                                result = result + "A"
                                            elif preunitsiga > unitjonga and preunitjonga > unitsiga:
                                                result = result + "B"
                                            elif preunitsiga == unitjonga and preunitjonga == unitsiga:
                                                result = result + "E"
                                            else:
                                                if preunitsiga >= unitjonga:
                                                    if unitjonga > preunitjonga:
                                                        result = result + "a"
                                                    else:
                                                        result = result + "b"
                                                elif unitjonga > preunitsiga:
                                                    if unitjonga > preunitjonga:
                                                        result = result + "A"
                                                    else:
                                                        result = result + "b"



                                    elif preunitjonga >= preunitsiga:

                                        if unitsiga > unitjonga:

                                            if unitsiga > preunitjonga and unitjonga > preunitsiga:
                                                result = result + "A"
                                            elif preunitjonga > unitsiga and preunitsiga > unitjonga:
                                                result = result + "B"
                                            elif preunitjonga == unitsiga and preunitsiga == unitjonga:
                                                result = result + "E"
                                            else:
                                                result = result + "b"


                                        elif unitjonga >= unitsiga:
                                            if unitjonga == unitsiga and unitsiga == preunitjonga:
                                                result = result + "E"
                                            elif unitjonga > preunitjonga and unitsiga > preunitsiga:
                                                result = result + "A"
                                            elif preunitjonga > unitjonga and preunitsiga > unitsiga:
                                                result = result + "B"
                                            elif preunitjonga == unitjonga and preunitsiga == unitsiga:
                                                result = result + "E"
                                            else:
                                                result = result + "a"


                                elif self.j > unitsiga and self.j > unitjonga:

                                    if preunitsiga > preunitjonga:

                                        if unitsiga > unitjonga:
                                            if unitsiga > preunitsiga and unitjonga > preunitjonga:
                                                result = result + "D"
                                            elif preunitsiga > unitsiga and preunitjonga > unitjonga:
                                                result = result + "C"
                                            elif preunitsiga == unitsiga and preunitjonga == unitjonga:
                                                result = result + "E"
                                            else:
                                                if unitjonga > preunitjonga:
                                                    result = result + "d"
                                                else:
                                                    result = result + "C"


                                        elif unitjonga >= unitsiga:
                                            if unitjonga == unitsiga and unitsiga == preunitjonga:
                                                result = result + "E"
                                            elif unitjonga > preunitsiga and unitsiga > preunitjonga:
                                                result = result + "D"
                                            elif preunitsiga > unitjonga and preunitjonga > unitsiga:
                                                result = result + "C"
                                            elif preunitsiga == unitjonga and preunitjonga == unitsiga:
                                                result = result + "E"
                                            else:
                                                if preunitsiga >= unitjonga:
                                                    if unitjonga > preunitjonga:
                                                        result = result + "d"
                                                    else:
                                                        result = result + "c"
                                                elif unitjonga > preunitsiga:
                                                    if unitjonga > preunitjonga:
                                                        result = result + "D"
                                                    else:
                                                        result = result + "c"

                                    elif preunitjonga >= preunitsiga:

                                        if unitsiga > unitjonga:

                                            if unitsiga > preunitjonga and unitjonga > preunitsiga:
                                                result = result + "D"
                                            elif preunitjonga > unitsiga and preunitsiga > unitjonga:
                                                result = result + "C"
                                            elif preunitjonga == unitsiga and preunitsiga == unitjonga:
                                                result = result + "E"
                                            else:
                                                result = result + "c"



                                        elif unitjonga >= unitsiga:
                                            if unitjonga == unitsiga and unitsiga == preunitjonga:
                                                result = result + "E"
                                            elif unitjonga > preunitjonga and unitsiga > preunitsiga:
                                                result = result + "D"
                                            elif preunitjonga > unitjonga and preunitsiga > unitsiga:
                                                result = result + "C"
                                            elif preunitjonga == unitjonga and preunitsiga == unitsiga:
                                                result = result + "E"
                                            else:
                                                result = result + "d"

                                else:

                                    if preunitsiga > self.j and preunitjonga > self.j:

                                        if preunitsiga > preunitjonga:

                                            if unitsiga > unitjonga:
                                                if unitsiga > preunitsiga and unitjonga > preunitjonga:
                                                    result = result + "A"
                                                elif preunitsiga > unitsiga and preunitjonga > unitjonga:
                                                    result = result + "B"
                                                elif preunitsiga == unitsiga and preunitjonga == unitjonga:
                                                    result = result + "E"
                                                else:
                                                    if unitjonga > preunitjonga:
                                                        result = result + "a"
                                                    else:
                                                        result = result + "B"


                                            elif unitjonga >= unitsiga:
                                                if unitjonga == unitsiga and unitsiga == preunitjonga:
                                                    result = result + "E"
                                                elif unitjonga > preunitsiga and unitsiga > preunitjonga:
                                                    result = result + "A"
                                                elif preunitsiga > unitjonga and preunitjonga > unitsiga:
                                                    result = result + "B"
                                                elif preunitsiga == unitjonga and preunitjonga == unitsiga:
                                                    result = result + "E"
                                                else:
                                                    if preunitsiga >= unitjonga:
                                                        if unitjonga > preunitjonga:
                                                            result = result + "a"
                                                        else:
                                                            result = result + "b"
                                                    elif unitjonga > preunitsiga:
                                                        if unitjonga > preunitjonga:
                                                            result = result + "A"
                                                        else:
                                                            result = result + "b"

                                        elif preunitjonga >= preunitsiga:

                                            if unitsiga > unitjonga:

                                                if unitsiga > preunitjonga and unitjonga > preunitsiga:
                                                    result = result + "A"
                                                elif preunitjonga > unitsiga and preunitsiga > unitjonga:
                                                    result = result + "B"
                                                elif preunitjonga == unitsiga and preunitsiga == unitjonga:
                                                    result = result + "E"
                                                else:
                                                    result = result + "b"


                                            elif unitjonga >= unitsiga:
                                                if unitjonga == unitsiga and unitsiga == preunitjonga:
                                                    result = result + "E"
                                                elif unitjonga > preunitjonga and unitsiga > preunitsiga:
                                                    result = result + "A"
                                                elif preunitjonga > unitjonga and preunitsiga > unitsiga:
                                                    result = result + "B"
                                                elif preunitjonga == unitjonga and preunitsiga == unitsiga:
                                                    result = result + "E"
                                                else:
                                                    result = result + "a"

                                    elif self.j > preunitsiga and self.j > preunitjonga:

                                        if preunitsiga > preunitjonga:

                                            if unitsiga > unitjonga:
                                                if unitsiga > preunitsiga and unitjonga > preunitjonga:
                                                    result = result + "D"
                                                elif preunitsiga > unitsiga and preunitjonga > unitjonga:
                                                    result = result + "C"
                                                elif preunitsiga == unitsiga and preunitjonga == unitjonga:
                                                    result = result + "E"
                                                else:
                                                    if unitjonga > preunitjonga:
                                                        result = result + "d"
                                                    else:
                                                        result = result + "C"


                                            elif unitjonga >= unitsiga:
                                                if unitjonga == unitsiga and unitsiga == preunitjonga:
                                                    result = result + "E"
                                                elif unitjonga > preunitsiga and unitsiga > preunitjonga:
                                                    result = result + "D"
                                                elif preunitsiga > unitjonga and preunitjonga > unitsiga:
                                                    result = result + "C"
                                                elif preunitsiga == unitjonga and preunitjonga == unitsiga:
                                                    result = result + "E"
                                                else:
                                                    if preunitsiga >= unitjonga:
                                                        if unitjonga > preunitjonga:
                                                            result = result + "d"
                                                        else:
                                                            result = result + "c"
                                                    elif unitjonga > preunitsiga:
                                                        if unitjonga > preunitjonga:
                                                            result = result + "D"
                                                        else:
                                                            result = result + "c"

                                        elif preunitjonga >= preunitsiga:

                                            if unitsiga > unitjonga:

                                                if unitsiga > preunitjonga and unitjonga > preunitsiga:
                                                    result = result + "D"
                                                elif preunitjonga > unitsiga and preunitsiga > unitjonga:
                                                    result = result + "C"
                                                elif preunitjonga == unitsiga and preunitsiga == unitjonga:
                                                    result = result + "E"
                                                else:
                                                    result = result + "c"


                                            elif unitjonga >= unitsiga:
                                                if unitjonga == unitsiga and unitsiga == preunitjonga:
                                                    result = result + "E"
                                                elif unitjonga > preunitjonga and unitsiga > preunitsiga:
                                                    result = result + "D"
                                                elif preunitjonga > unitjonga and preunitsiga > unitsiga:
                                                    result = result + "C"
                                                elif preunitjonga == unitjonga and preunitsiga == unitsiga:
                                                    result = result + "E"
                                                else:
                                                    result = result + "d"
                                    else:
                                        result = result + "F"

                        preunitsiga = unitsiga
                        preunitjonga = unitjonga
                        self.portfolio_stock_dict[sCode].update({"전시가": unitsiga})
                        self.portfolio_stock_dict[sCode].update({"전종가": unitjonga})

                    self.portfolio_stock_dict[sCode].update({'결과': result})
                    abc = len(self.portfolio_stock_dict[sCode]['결과'])

                    self.portfolio_stock_dict[sCode].update({'결과갯수': abc})


                    if self.portfolio_stock_dict[sCode]['만족갯수1'] > 14:
                        maxGoga2 = self.portfolio_stock_dict[sCode]['맥스고가']
                        maxQ = int(self.portfolio_stock_dict[sCode]['맥스거래량'])
                        currentQ = int(self.portfolio_stock_dict[sCode][self.bunbongQuant])

                        currentQ = int(self.portfolio_stock_dict[sCode][self.bunbongQuant])

                        tempsn = range(endSn - 4, endSn)
                        for y in tempsn:
                            mesuganeungjonga = str(y) + "분봉종가"
                            mesuganeungQ = str(y) + "분봉거래량"
                            if self.portfolio_stock_dict[sCode][mesuganeungjonga] > b:
                                currentQ = currentQ + int(self.portfolio_stock_dict[sCode][mesuganeungQ])


                        if b > maxGoga2 and currentQ >maxQ * 0.7 :

                            quantity = int(5000000 / b)

                            print("케이스1 코드:%s 시간:%s 가격:%s, 수량:%s, 시가:%s" % (sCode,meme, b, quantity, self.j))
                            print("맥스거래량:%s, 현거래량:%s" %(maxQ,currentQ))
                            # order_success = self.dynamicCall(
                            #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                            #     ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                            #      sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])


                            self.portfolio_stock_dict[sCode].update({"매수가능여부":"N"})
                            self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                            self.portfolio_stock_dict[sCode].update({"매수조건": "case2"})
                            self.portfolio_stock_dict[sCode].update({"매수기준가": maxGoga2})
                            self.portfolio_stock_buy.update({sCode:{}})

                            self.online_jango_dict.update({sCode:{}})
                            self.online_jango_dict[sCode].update({"매입단가":b})
                            self.online_jango_dict[sCode].update({"주문가능수량": quantity})
                            self.online_jango_dict[sCode].update({"매도가격1": 0})
                            self.online_jango_dict[sCode].update({"매도가격2": 0})
                            self.online_jango_dict[sCode].update({"매도가격3": 0})
                            self.online_jango_dict[sCode].update({"매도가격4": 0})
                            self.online_jango_dict[sCode].update({"매도가격5": 0})
                            self.online_jango_dict[sCode].update({"매도가격6": 0})
                            self.online_jango_dict[sCode].update({"매도가격7": 0})



                ############################# 매도 #########################################

            if sCode in self.online_jango_dict.keys():

                medoSn = self.portfolio_stock_dict[sCode]['순번']
                mesubunbong = self.portfolio_stock_dict[sCode]['매수분봉']

                asd = self.online_jango_dict[sCode]
                meib = int(asd['매입단가'])
                meme_rate = (b - meib) / meib * 100  # 등락률

                self.online_jango_dict[sCode].update({"수익률": meme_rate})

                mesuGijunga = self.portfolio_stock_dict[sCode]['매수기준가']
                tempstr = str(mesubunbong) + "분봉저가"
                sonjulGijunga = self.portfolio_stock_dict[sCode][tempstr]

                ikjulCnt = self.portfolio_stock_dict[sCode]['익절횟수']

                medojogun = range(mesubunbong, medoSn)

                madojanunManjok = "N"
                madojanunManjok2 = "N"
                ikjuljojunmanjok = "N"

                for g in medojogun:
                    medounitbunbongNmGoga = str(g) + "분봉고가"
                    medounitbunbongNmSiga = str(g) + "분봉시가"
                    medounitbunbongNmJongga = str(g) + "분봉종가"

                    if medounitbunbongNmSiga in self.portfolio_stock_dict[sCode]:

                        medounitgoga = self.portfolio_stock_dict[sCode][medounitbunbongNmGoga]
                        medounitsiga = self.portfolio_stock_dict[sCode][medounitbunbongNmSiga]
                        medoUnitJonga = self.portfolio_stock_dict[sCode][medounitbunbongNmJongga]

                        jonga_meme_rate = ((medoUnitJonga - meib) / meib) * 100

                        # if 1.0 > jonga_meme_rate:
                        #     ikjuljojunmanjok = "Y"

                        if mesuGijunga > medoUnitJonga or sonjulGijunga > medoUnitJonga:
                            madojanunManjok = "Y"

                        if g == mesubunbong:
                            if mesuGijunga >= medoUnitJonga:
                                if medounitgoga - medoUnitJonga > medoUnitJonga - medounitsiga:
                                    madojanunManjok2 = "Y"

                bunsiga = self.portfolio_stock_dict[sCode][self.bunbongNmSiga]
                bunjongga = self.portfolio_stock_dict[sCode][self.bunbongNmJongga]
                sonjulCnt = self.portfolio_stock_dict[sCode]['손절횟수']

                sojulRate = ((mesuGijunga - b) / mesuGijunga) * 100

                if self.online_jango_dict[sCode]['수익률'] > 0:

                    if asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] > 7.0:

                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        print("즉시익절9 매도:%s, 수익률:%s,  시간:%s" % (sCode, meme_rate, meme))

                        # order_success = self.dynamicCall(
                        #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                        #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                        #        sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                        # if order_success == 0:
                        #     self.portfolio_stock_dict[sCode].update({"매도가": b})
                        #     print("매도주문 전달 성공")
                        # else:
                        #     print("매도주문 전달 실패")
                        del self.online_jango_dict[sCode]

                    elif asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] > 6.0:
                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        self.online_jango_dict[sCode].update({"매도가격7": b})

                        print("6.0 프로이상 홀딩:%s, 수익률:%s, 시간:%s" % (sCode, meme_rate, meme))

                    elif asd['주문가능수량'] > 0 and 5.0 > self.online_jango_dict[sCode]['수익률'] and \
                            self.online_jango_dict[sCode]['매도가격7'] > 0:

                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        print("즉시익절8 매도:%s, 수익률:%s,  시간:%s" % (sCode, meme_rate, meme))

                        # order_success = self.dynamicCall(
                        #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                        #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                        #        sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                        #
                        # if order_success == 0:
                        #     self.portfolio_stock_dict[sCode].update({"매도가": b})
                        #     print("매도주문 전달 성공")
                        # else:
                        #     print("매도주문 전달 실패")
                        del self.online_jango_dict[sCode]

                    elif asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] > 5.0:
                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        self.online_jango_dict[sCode].update({"매도가격6": b})

                        print("5.0 프로이상 홀딩:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))

                    elif asd['주문가능수량'] > 0 and 4.0 > self.online_jango_dict[sCode]['수익률'] and \
                            self.online_jango_dict[sCode]['매도가격6'] > 0:

                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        print("즉시익절7 매도:%s, 수익률:%s,  시간:%s" % (sCode, meme_rate, meme))

                        # order_success = self.dynamicCall(
                        #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                        #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                        #        sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                        #
                        # if order_success == 0:
                        #     self.portfolio_stock_dict[sCode].update({"매도가": b})
                        #     print("매도주문 전달 성공")
                        # else:
                        #     print("매도주문 전달 실패")

                        del self.online_jango_dict[sCode]


                    elif asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] > 4.0:
                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        self.online_jango_dict[sCode].update({"매도가격5": b})

                        print("4.0 프로이상 홀딩:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))



                    elif asd['주문가능수량'] > 0 and 3.0 > self.online_jango_dict[sCode]['수익률']:

                        if self.online_jango_dict[sCode]['매도가격5'] > 0:
                            if self.portfolio_stock_dict[sCode]['익절5'] == "N":
                                profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                                ikjulmedoCnt = int(asd['주문가능수량']) / 2

                                print("즉시익절6 매도:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))

                                # order_success = self.dynamicCall(
                                #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                #        sCode, ikjulmedoCnt, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                                #
                                # if order_success == 0:
                                #     self.portfolio_stock_dict[sCode].update({"매도가": b})
                                #     self.portfolio_stock_dict[sCode].update({'익절5': "Y"})
                                #     self.online_jango_dict[sCode].update({"매도가격4": b})
                                #     print("매도주문 전달 성공")
                                # else:
                                #     print("매도주문 전달 실패")
                                self.online_jango_dict[sCode].update({"주문가능수량": asd['주문가능수량'] - ikjulmedoCnt})


                    elif asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] > 3.0:
                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        self.online_jango_dict[sCode].update({"매도가격4": b})

                        print("3.0 프로이상 홀딩:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))


                    elif asd['주문가능수량'] > 0 and 2.0 > self.online_jango_dict[sCode]['수익률']:

                        if self.online_jango_dict[sCode]['매도가격4'] > 0:

                            print("즉시익절4 매도:%s, 수익률:%s,  시간:%s" % (sCode, meme_rate, meme))

                            # order_success = self.dynamicCall(
                            #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                            #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                            #        sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                            #
                            # if order_success == 0:
                            #     print("매도주문 전달 성공")
                            #     self.portfolio_stock_dict[sCode].update({"매도가": b})
                            #     self.online_jango_dict[sCode].update({"매도가격3": b})
                            # else:
                            #     print("매도주문 전달 실패")
                            del self.online_jango_dict[sCode]
                    elif asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] > 2.0:

                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        self.online_jango_dict[sCode].update({"매도가격3": b})

                        print("2.0 프로이상 홀딩:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))

                    elif asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['매도가격3'] > 0 and \
                            1.0 > self.online_jango_dict[sCode]['수익률']:

                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        print("즉시익절3 매도:%s, 수익률:%s,  시간:%s" % (sCode, meme_rate, meme))

                        # ikjulmedoCnt = int(asd['주문가능수량']) / 2
                        #
                        # order_success = self.dynamicCall(
                        #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                        #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                        #        sCode, ikjulmedoCnt, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                        #
                        # if order_success == 0:
                        #     print("매도주문 전달 성공")
                        #     self.portfolio_stock_dict[sCode].update({"매도가": b})
                        #     self.portfolio_stock_dict[sCode].update({'익절횟수': ikjulCnt + 1})
                        #     self.portfolio_stock_dict[sCode].update({'익절3': "Y"})
                        # else:
                        #     print("매도주문 전달 실패")
                        self.portfolio_stock_dict[sCode].update({'익절횟수': ikjulCnt + 1})
                        self.portfolio_stock_dict[sCode].update({'익절3': "Y"})
                        self.online_jango_dict[sCode].update({"주문가능수량": asd['주문가능수량'] - ikjulmedoCnt})

                    elif asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] > 1.0:

                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        self.online_jango_dict[sCode].update({"매도가격2": b})

                        print("1.0 프로이상 홀딩:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))


                    elif asd['주문가능수량'] > 0 and 0.5 > self.online_jango_dict[sCode]['수익률']:

                        if self.online_jango_dict[sCode]['매도가격2'] > 0:

                            if self.portfolio_stock_dict[sCode]['익절2'] == "N":

                                profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                                print("즉시익절2 매도:%s, 수익률:%s, 시간:%s" % (sCode, meme_rate, meme))

                                ikjulmedoCnt = int(asd['주문가능수량']) / 2

                                # order_success = self.dynamicCall(
                                #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                #        sCode, ikjulmedoCnt, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                                # if order_success == 0:
                                #     print("매도주문 전달 성공")
                                #     self.portfolio_stock_dict[sCode].update({"매도가": b})
                                #     self.portfolio_stock_dict[sCode].update({'익절횟수': ikjulCnt + 1})
                                #     self.portfolio_stock_dict[sCode].update({'익절2': "Y"})
                                # else:
                                #     print("매도주문 전달 실패")
                                self.portfolio_stock_dict[sCode].update({'익절횟수': ikjulCnt + 1})
                                self.portfolio_stock_dict[sCode].update({'익절2': "Y"})
                                self.online_jango_dict[sCode].update({"주문가능수량": asd['주문가능수량'] - ikjulmedoCnt})

                    elif asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] > 0.5:
                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        self.online_jango_dict[sCode].update({"매도가격1": b})

                        print("0.5프로이상 홀딩:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))


                    elif asd['주문가능수량'] > 0 and 0.2 > self.online_jango_dict[sCode]['수익률'] and \
                            self.online_jango_dict[sCode]['매도가격1'] > 0:
                        if ikjulCnt == 0:

                            print("즉시익절1 매도:%s, 수익률:%s 시간:%s" % (sCode, meme_rate, meme))

                            ikjulmedoCnt = int(asd['주문가능수량']) / 3

                            # order_success = self.dynamicCall(
                            #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                            #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                            #        sCode, ikjulmedoCnt, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                            # if order_success == 0:
                            #     print("매도주문 전달 성공")
                            #     self.portfolio_stock_dict[sCode].update({"매도가": b})
                            #     self.portfolio_stock_dict[sCode].update({'익절횟수': ikjulCnt + 1})
                            #     self.portfolio_stock_dict[sCode].update({'익절1': "Y"})
                            #
                            # else:
                            #     print("매도주문 전달 실패")
                            self.portfolio_stock_dict[sCode].update({'익절1': "Y"})
                            self.portfolio_stock_dict[sCode].update({'익절횟수': ikjulCnt + 1})
                            self.online_jango_dict[sCode].update({"주문가능수량":asd['주문가능수량']-ikjulmedoCnt})

                        elif self.online_jango_dict[sCode]['매도가격2'] > 0:
                            print("즉시익절1 매도:%s, 수익률:%s 시간:%s" % (sCode, meme_rate, meme))



                ################################## 손절 ######################################
                else:
                    if madojanunManjok == "Y" or madojanunManjok2 == "Y":
                        if mesuGijunga > sonjulGijunga:
                            if mesuGijunga > b and bunsiga > bunjongga and sonjulCnt == 0:

                                sonjulQuan1 = int(asd['주문가능수량']) / 3
                                sonjulAmount = (meib - b) * sonjulQuan1
                                print("손절1 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                                print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))

                                # order_success = self.dynamicCall(
                                #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                #        sCode, sonjulQuan1, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                                #
                                # if order_success == 0:
                                #
                                #     print("매도주문 전달 성공")
                                #     self.portfolio_stock_dict[sCode].update({"손절횟수": 1})
                                # else:
                                #     print("매도주문 전달 실패")
                                self.portfolio_stock_dict[sCode].update({"손절횟수": 1})

                            elif sonjulGijunga > b and bunsiga > bunjongga:

                                sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                                print("손절2 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                                print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                                # order_success = self.dynamicCall(
                                #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                #        sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                                #
                                # if order_success == 0:
                                #
                                #     print("매도주문 전달 성공")
                                # else:
                                #     print("매도주문 전달 실패")

                        else:
                            if sonjulGijunga > b and bunsiga > bunjongga and sonjulCnt == 0:
                                sonjulQuan1 = int(asd['주문가능수량']) / 3
                                sonjulAmount = (meib - b) * sonjulQuan1
                                print("손절3 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                                print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                                # order_success = self.dynamicCall(
                                #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                #        sCode, sonjulQuan1, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                                #
                                # if order_success == 0:
                                #     self.portfolio_stock_dict[sCode].update({"손절횟수": 1})
                                #     print("매도주문 전달 성공")
                                # else:
                                #     print("매도주문 전달 실패")
                                self.portfolio_stock_dict[sCode].update({"손절횟수": 1})

                            elif mesuGijunga > b and bunsiga > bunjongga:

                                sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                                print("손절4 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                                print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                                # order_success = self.dynamicCall(
                                #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                #        sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                                #
                                # if order_success == 0:
                                #
                                #     print("매도주문 전달 성공")
                                # else:
                                #     print("매도주문 전달 실패")

                    else:

                        if mesuGijunga > sonjulGijunga:
                            if mesuGijunga > b and bunsiga > bunjongga and sonjulCnt == 0 and sojulRate > 1.5:

                                sonjulQuan1 = int(asd['주문가능수량']) / 2
                                sonjulAmount = (meib - b) * sonjulQuan1
                                print("손절5 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                                print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                                # order_success = self.dynamicCall(
                                #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                #        sCode, sonjulQuan1, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                                #
                                # if order_success == 0:
                                #     self.portfolio_stock_dict[sCode].update({"손절횟수": 1})
                                #     print("매도주문 전달 성공")
                                # else:
                                #     print("매도주문 전달 실패")
                                self.portfolio_stock_dict[sCode].update({"손절횟수": 1})

                            elif sonjulGijunga > b and bunsiga > bunjongga and sojulRate > 1.5:

                                sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                                print("손절6 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                                print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                                # order_success = self.dynamicCall(
                                #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                #        sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                                #
                                # if order_success == 0:
                                #
                                #     print("매도주문 전달 성공")
                                # else:
                                #     print("매도주문 전달 실패")

                        else:
                            if sonjulGijunga > b and bunsiga > bunjongga and sonjulCnt == 0:
                                sonjulQuan1 = int(asd['주문가능수량']) / 2
                                sonjulAmount = (meib - b) * sonjulQuan1
                                print("손절7 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                                print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                                # order_success = self.dynamicCall(
                                #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                #        sCode, sonjulQuan1, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                                #
                                # if order_success == 0:
                                #     self.portfolio_stock_dict[sCode].update({"손절횟수": 1})
                                #     print("매도주문 전달 성공")
                                # else:
                                #     print("매도주문 전달 실패")
                                self.portfolio_stock_dict[sCode].update({"손절횟수": 1})

                            elif mesuGijunga > b and bunsiga > bunjongga:

                                sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                                print("손절8 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                                print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                                # order_success = self.dynamicCall(
                                #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                #     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                #        sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                                #
                                # if order_success == 0:
                                #
                                #     print("매도주문 전달 성공")
                                # else:
                                #     print("매도주문 전달 실패")


        # print(self.portfolio_stock_dict)
        # print("back Test End")
    #################################################################################################
    ############################### 주문 slot #######################################################

    def chejan_slot(self, sGubun, nItemCnt, sFidList):

        if int(sGubun) == 0:
            print("주문체결")
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['계좌번호'])
            rowsCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['종목코드'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['종목명'])
            stock_name = stock_name.strip()

            original_order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['원주문번호'])
            order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['주문번호'])
            order_status = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['주문상태'])
            order_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['주문수량'])
            if order_quan == '':
                order_quan = 0
            else:
                order_quan = int(order_quan)

            order_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['주문가격'])
            if order_price == '':
                order_price = 0
            else:
                not_chegual_quan = int(order_price)

            not_chegual_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['미체결수량'])

            if not_chegual_quan == '':
                not_chegual_quan = 0
            else:
                not_chegual_quan = int(not_chegual_quan)

            order_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['주문구분'])
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')

            # meme_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['매도수구분'])
            # meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]

            chegual_time_str = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['주문/체결시간'])

            chegual_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['체결가'])

            if chegual_price == '':
                chegual_price = 0
            else:
                chegual_price = int(chegual_price)

            chegual_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['체결량'])

            if chegual_quantity == '':
                chegual_quantity = 0
            else:
                chegual_quantity = int(chegual_quantity)

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['현재가'])
            if current_price == '':
                current_price = 0
            current_price = abs(int(current_price))

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['(최우선)매도호가'])
            if first_sell_price == '':
                first_sell_price = 0
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['(최우선)매수호가'])
            if first_buy_price == '':
                first_buy_price = 0
            first_buy_price = abs(int(first_buy_price))

            ##### 새로운 주문이면 주문번호 할당
            if sCode not in self.account_stock_dict.keys():
                self.account_stock_dict.update({sCode: {}})

            self.account_stock_dict[sCode].update({"종목코드": sCode})
            self.account_stock_dict[sCode].update({"주문번호": order_number})
            self.account_stock_dict[sCode].update({"종목명": stock_name})
            self.account_stock_dict[sCode].update({"주문상태": order_status})
            self.account_stock_dict[sCode].update({"주문수량": order_quan})
            self.account_stock_dict[sCode].update({"주문가격": order_price})
            self.account_stock_dict[sCode].update({"미체결수량": not_chegual_quan})
            self.account_stock_dict[sCode].update({"원주문번호": original_order_number})
            self.account_stock_dict[sCode].update({"주문구분": order_gubun})
            # self.not_account_stock_dict[order_number].update({"매도수구분": meme_gubun})
            self.account_stock_dict[sCode].update({"주문/체결시간": chegual_time_str})
            self.account_stock_dict[sCode].update({"체결가": chegual_price})
            self.account_stock_dict[sCode].update({"체결량": chegual_quantity})
            self.account_stock_dict[sCode].update({"현재가": current_price})
            self.account_stock_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            self.account_stock_dict[sCode].update({"(최우선)매수 호가": first_buy_price})

            # print(rowsCode)
            # print(sCode)
            # print(self.account_stock_dict)


        # 잔고
        elif int(sGubun) == 1:
            print("잔고")
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목코드'])[1:]

            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['현재가'])
            if current_price == '':
                current_price = 0

            current_price = abs(int(current_price))

            stock_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['보유수량'])
            if stock_quan == '':
                stock_quan = 0
            stock_quan = int(stock_quan)

            like_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)

            buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매입단가'])
            if buy_price == '':
                buy_price = 0
            buy_price = abs(int(buy_price))

            total_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['총매입가'])
            if total_buy_price == '':
                total_buy_price = 0
            total_buy_price = int(total_buy_price)

            meme_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매도매수구분'])
            meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            if sCode not in self.online_jango_dict.keys():
                self.online_jango_dict.update({sCode: {}})

            self.online_jango_dict[sCode].update({"현재가": current_price})
            self.online_jango_dict[sCode].update({"종목코드": sCode})
            self.online_jango_dict[sCode].update({"종목명": stock_name})
            self.online_jango_dict[sCode].update({"보유수량": stock_quan})
            self.online_jango_dict[sCode].update({"주문가능수량": like_quan})
            self.online_jango_dict[sCode].update({"매입단가": buy_price})
            self.online_jango_dict[sCode].update({"총매입가": total_buy_price})
            self.online_jango_dict[sCode].update({"매도매수구분": meme_gubun})
            self.online_jango_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            self.online_jango_dict[sCode].update({"(최우선)매수호가": first_buy_price})
            self.online_jango_dict[sCode].update({"주문용스크린번호": self.screen_meme_stock})
            
            # if sCode in self.portfolio_stock_dict.keys():
            #     mesuSn = self.portfolio_stock_dict[sCode]['매수분봉']
            #
            #     self.online_jango_dict[sCode].update({"매수분봉":mesuSn})

            if stock_quan == 0:
                del self.online_jango_dict[sCode]
              #  self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[sCode]['스크린번호'], sCode)

                if sCode in self.portfolio_stock_buy.keys():
                    del self.portfolio_stock_buy[sCode]

               # if sCode in self.portfolio_stock_dict.keys():
                  #  del self.portfolio_stock_dict[sCode]

        # else:

        # for sCode in self.online_jango_dict.keys():
        # self.day_kiwoom_db(code=sCode)

        # fids = self.realType.REALTYPE['주식체결']['체결시간']

        # self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_meme_stock, sCode, fids, "1")
        ##print(self.online_jango_dict)

    # 송수신 메세지 get
    def msg_slot(self, sScrNo, sRgName, sTrCode, msg):
        print("스크린: %s, 요청이름: %s, tr코드:%s----%s " % (sScrNo, sRgName, sTrCode, msg))

    # 파일 삭제
    def file_delete(self):
        if os.path.isfile("files/condition_stock.txt"):
            os.remove("files/condition_stock.txt")

    class ItemInfo:
        def __init__(self, itemCode, itemName):
            self.itemCode = itemCode
            self.itemName = itemName
















