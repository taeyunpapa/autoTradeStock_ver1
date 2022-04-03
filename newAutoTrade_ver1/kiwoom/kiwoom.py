import os
import sys
import datetime

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *
from time import sleep


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

        #######스크린번호 모음#############

        self.screen_my_info = "2000"
        self.screen_calculator_stock = "4000"
        self.screen_real_stock = "5000"  # 종목별로 할당할 스크린번호
        self.screen_meme_stock = "6000"  # 종목별로 할당할 주문용 스크린 번호
        self.screen_meme_stock1 = "6001"  # 종목별로 할당할 주문용 스크린 번호
        self.screen_meme_stock2 = "6002"  # 종목별로 할당할 주문용 스크린 번호
        self.screen_meme_stock3 = "6003"  # 종목별로 할당할 주문용 스크린 번호
        self.screen_meme_stock4 = "6004"  # 종목별로 할당할 주문용 스크린 번호
        self.screen_meme_stock5 = "6005"  # 종목별로 할당할 주문용 스크린 번호
        self.screen_meme_stock6 = "6006"  # 종목별로 할당할 주문용 스크린 번호
        self.screen_meme_stock7 = "6007"  # 종목별로 할당할 주문용 스크린 번호
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
        base = self.currentDay + "090000"
        base2 = self.currentDay + "150000"
        base3 = self.currentDay + "100000"
        base4 = self.currentDay + "093000"
        self.baseTime = datetime.datetime.strptime(base, "%Y%m%d%H%M%S")
        self.startTime1 = None
        self.mesuEndTime = datetime.datetime.strptime(base2, "%Y%m%d%H%M%S")
        self.maxTime = datetime.datetime.strptime(base3, "%Y%m%d%H%M%S")
        self.mesuStartTime = datetime.datetime.strptime(base4, "%Y%m%d%H%M%S")

        self.bunbongNmSiga = None
        self.bunbongNmJongga = None
        self.bunbongNmGoga = None
        self.bunbongNmJuga = None
        self.bunbongQuant = None

        #######################################

        ##########변수모음##############
        self.screenNum = 0
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

        self.meme_stock_list = {}

        ##############################

        ########종목분석용############
        self.calcul_data = []
        self.itemList = []
        ############################

        self.get_ocx_instance()
        self.event_slot()
        self.real_event_slot()

        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info()  # 예수금 가져오기
        self.not_concluded_account()  # 미체결 요청
        self.getItemList()  # 종목코드가져오기

        self.detail_account_mystock()  # 계좌평가 잔고내역 가져오기

        self.screen_number_setting()  # 스크린번호를 할당

        self.stock_research()

       # self.read_code()  # 저장된 종목 파일 불러오기


        self.isFirst = "Y"
        



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
                self.market_stock_list[name].update({"시장구분": marget})

    def searchItem(self, itemName, price):
        # print("종목조회 : %s" % itemName)
        meme_code = None
        # itemName = self.ui.searchItemTextEdit.toPlainText()
        for item in self.market_stock_list.keys():
            if item == itemName:
                # print(self.market_stock_list[item]['종목코드'])
                # print(self.market_stock_list[item]['시장구분'])
                marketgubun1 = self.market_stock_list[item]['시장구분']
                tempStockCode = self.market_stock_list[item]['종목코드']
                if tempStockCode not in self.portfolio_stock_dict.keys():

                    if self.screenNum<100:
                        screenMemeNum= self.screen_meme_stock
                    elif self.screenNum>=100 and self.screenNum<200:
                        screenMemeNum = self.screen_meme_stock1
                    elif self.screenNum>=200 and self.screenNum<300:
                        screenMemeNum = self.screen_meme_stock2
                    elif self.screenNum>=300 and self.screenNum<400:
                        screenMemeNum = self.screen_meme_stock3
                    elif self.screenNum>=400 and self.screenNum<500:
                        screenMemeNum = self.screen_meme_stock4
                    elif self.screenNum>=500 and self.screenNum<600:
                        screenMemeNum = self.screen_meme_stock5
                    else:
                        screenMemeNum = self.screen_meme_stock6

                    self.portfolio_stock_dict.update({tempStockCode: {"종목명": itemName,"기준가격":price,"시장구분":marketgubun1,"결과갯수":0,"결과":"","재결과":"",
                        "주문용스크린번호": screenMemeNum, "익절횟수": 0,"처음":"Y","처음1":"Y", "순번":0,"분봉갯수":0,"매수분봉":0,
                        "전시가":0,"전종가":0,"맥스고가":0,"매수조건":"", "매수가능여부":"Y","매도가":0,"손절횟수":0,"만족갯수1":0,"만족갯수2":0,
                        "익절1":"N", "익절2":"N", "익절3":"N", "익절4":"N", "익절5":"N", "익절6":"N", "익절7":"N", "맥스거래량":0
                        ,"매수거래량":0, "추가매수여부":"N", "시간비율":"", "익절8":"N", "익절9":"N", "익절10":"N", "익절11":"N"
                        , "익절12":"N", "익절13":"N", "익절14":"N", "익절15":"N", "익절16":"N", "익절17":"N", "익절18":"N","손절":"N"
                        ,"맥스갭":0, "맥스시간":"N", "손절1":"N", "손절2":"N", "익절0":"N", "매도호가우위":"N", "매수갯수":0, "매수수량":0
                        ,"매도갯수":0, "매도수량":0, "매도호가총잔량":0, "매수호가총잔량":0, "만족갯수저가":0,"손절3":"N","맥스저가":0
                        ,"15분봉시가1":0,"15분봉종가1":0,"15분봉시가2":0,"15분봉종가2":0, "평균매수가":0, "최고수익률":0,"호가썸":0}})
                    # print("매매종목추가:%s" % self.portfolio_stock_dict[tempStockCode]['종목명'])
                    meme_code = tempStockCode
                    # 일봉데이터 받아오기
                    # self.day_kiwoom_db(code=tempStockCode)
                    # self.stock_basic_info(code=tempStockCode)
                    self.screenNum += 1
                break

        # print(self.portfolio_stock_dict)
    def register(self, code):

        screen_num = self.portfolio_stock_dict[code]['주문용스크린번호']
        fids = self.realType.REALTYPE['주식체결']['체결시간']

        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1")
        print("실시간등록코드 : %s, 스크린번호: %s, fid번호: %s" % (code, screen_num, fids))

        fids2 = self.realType.REALTYPE['주식호가잔량']['매도호가총잔량']
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids2, "1")

    # 이벤트 슬롯
    def event_slot(self):
        # 로그인 이벤트 슬롯
        self.OnEventConnect.connect(self.login_slot)

        # tr이벤트 슬롯
        self.OnReceiveTrData.connect(self.trData_slot)

        self.OnReceiveMsg.connect(self.msg_slot)

    # 실시간 이벤트 슬롯
    def real_event_slot(self):
        self.OnReceiveRealData.connect(self.realdata_slot)
        self.OnReceiveChejanData.connect(self.chejan_slot)  ## 주문관련 슬롯

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.event_login_loop = QEventLoop()
        self.event_login_loop.exec_()

    def login_slot(self, errCode):
        print(errors(errCode))

        # 로그인이 완료되면 이벤트 로그인 루프를 끊어줌
        self.event_login_loop.exit()

    # 계좌번호 가져오기
    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)", "ACCNO")
        self.account_num = account_list.split(';')[1]
        print("보유계좌번호 %s" % self.account_num)

    # 저장된 종목 파일 불러오기
    def read_code(self):
        if os.path.exists("files/condition_stock.txt"):
            f = open("files/condition_stock.txt", "r", encoding="utf8")

            lines = f.readlines()
            for line in lines:
                if line != "":
                    ls = line.split("\n")  # 파일 쓸때 \t로 구분지어 놨기때문에

                    # stock_nm = ls[0]
                    stock_if = ls[0]
                    stock_nm = stock_if.split('/')[0]
                    price = stock_if.split('/')[1]
                    # marketgubun = stock_if.split('/')[2]

                    self.searchItem(stock_nm,price)



            f.close()  # 파일 닫기

        self.register()
            # print(self.portfolio_stock_dict)

    ########################### TR START #########################################
    ##############################################################################
    def stock_research(self):
        print("거래량상위종목조회")
        a = 3000
        for i in range(a):
            QTest.qWait(5000)
            # 시장구분 = 000:전체, 001:코스피, 101:코스닥
            # 정렬구분 = 1:거래량, 2: 거래회전율, 3: 거래대금
            # 관리종목포함 = 0:관리종목 포함, 1:관리종목 미포함, 3:우선주제외, 11:정리매매종목제외, 4:관리종목, 우선주제외
            # 장운영구분 = 0:전체조회, 1: 장중, 2: 장전시간외, 3: 장후시간외
            self.dynamicCall("SetInputValue(QString, QString)", "시장구분", "101")
            self.dynamicCall("SetInputValue(QString, QString)", "정렬구분", "3")
            self.dynamicCall("SetInputValue(QString, QString)", "관리종목포함", "11")
            self.dynamicCall("SetInputValue(QString, QString)", "신용구분", "0")
            self.dynamicCall("SetInputValue(QString, QString)", "거래량구분", "0")
            self.dynamicCall("SetInputValue(QString, QString)", "가격구분", "0")
            self.dynamicCall("SetInputValue(QString, QString)", "거래대금구분", "0")
            self.dynamicCall("SetInputValue(QString, QString)", "장운영구분", "1")
            self.dynamicCall("CommRqData(String, String, int, String)", "당일거래량상위요청", "opt10030", "0",
                             self.screen_my_info)

    def stock_basic_info(self,code):
        QTest.qWait(1000)
        print("주식기본정보요청")
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("CommRqData(String, String, int, String)", "주식기본정보요청", "opt10001", "0", self.screen_my_info)

    def detail_account_info(self):
        print("예수금을 요청하는 부분")

        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")

        self.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)

        # 이벤트루프 : 작업이 끝날때까지 다음 아래 코드 실행 안됨
        self.detail_account_info_event_loop.exec_()

    # 계좌평가잔고내역
    def detail_account_mystock(self, sPrevNext="0"):
        print("계좌평가잔고내역요청")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")

        self.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역", "opw00018", "0", self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    # 미체결 내역
    def not_concluded_account(self, sPrevNext="0"):
        print("미체결 요청")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")

        self.dynamicCall("CommRqData(String, String, int, String)", "실시간미체결요청", "opt10075", sPrevNext,
                         self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    # 일봉데이터 받아오기
    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        print("일봉데이터:%s" % code)

        QTest.qWait(500)  # 3.6초 딜레이(과도한 조회로 오류방지)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext,
                         self.screen_calculator_stock)

        self.calculator_event_loop.exec_()

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
        if sRQName == "당일거래량상위요청":
            cnt1 = 50
            for i in range(cnt1):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "종목코드").strip()
                sunwe = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                        "현재순위").strip()
                codeNm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                        "종목명").strip()
                rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                          "등락률").strip()

                if code not in self.portfolio_stock_dict.keys():

                    self.portfolio_stock_dict.update({code: {"종목명": codeNm,  "결과갯수": 0, "결과": "",
                         "재결과": "","주문용스크린번호": "6000", "익절횟수": 0, "처음": "Y","처음1": "Y", "순번": 0,
                        "분봉갯수": 0, "매수분봉": 0,"전시가": 0, "전종가": 0, "맥스고가": 0, "매수조건": "","매수가능여부": "Y",
                        "매도가": 0, "손절횟수": 0, "만족갯수1": 0,"만족갯수2": 0,"익절1": "N", "익절2": "N", "익절3": "N", "익절4": "N",
                        "익절5": "N", "익절6": "N", "익절7": "N", "맥스거래량": 0, "매수거래량": 0, "추가매수여부": "N",
                        "시간비율": "", "익절8": "N", "익절9": "N", "익절10": "N", "익절11": "N", "익절12": "N",
                        "익절13": "N", "익절14": "N", "익절15": "N", "익절16": "N", "익절17": "N", "익절18": "N",
                        "손절": "N", "맥스갭": 0, "맥스시간": "N", "손절1": "N", "손절2": "N", "익절0": "N",
                        "매도호가우위": "N", "매수갯수": 0, "매수수량": 0, "매도갯수": 0, "매도수량": 0, "매도호가총잔량": 0,
                        "매수호가총잔량": 0, "만족갯수저가": 0, "손절3": "N", "맥스저가": 0, "15분봉시가1": 0, "15분봉종가1": 0,
                        "15분봉시가2": 0, "15분봉종가2": 0, "평균매수가": 0, "최고수익률": 0, "호가썸": 0, "매수강도":1,
                        "매수강도비율":0, "매수강도조건확인":"N","매도1잔량합":1, "매도2잔량합":1, "손절만족":"N","매수1여부":"N","매수2여부":"N","매수3여부":"N"
                        ,"매수기준가1":0,"매수기준가2":0, "매수기준가3":0,"총맥스고가":0}})
                    self.screenNum += 1
                    self.register(code)
                    
            # print("거래량상위종목추가")
            # print(self.portfolio_stock_dict)



        if sRQName == "주식기본정보요청":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드").strip()
            codeNm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목명").strip()
            sigaChong = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "시가총액").strip())

            if self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "유통비율").strip() == '':
                flowRate = float(100)
            else:
                flowRate = float(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "유통비율").strip())

            sigaChong = int(sigaChong * flowRate/100)

            print("종목명:%s 시가총액:%s 유통비율:%s" % (codeNm, sigaChong, flowRate))

            self.portfolio_stock_dict[code].update({"시가총액":sigaChong})

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

                if code not in self.meme_stock_list.keys():
                    self.meme_stock_list.update({code: {}})

                cnt += 1

            print("가지고있는 종목갯수 %s" % cnt)
            print("가지고있는 종목 %s" % self.online_jango_dict)
            print(self.portfolio_stock_dict)

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

        elif sRQName == "주식일봉차트조회":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            print("일봉데이터 요청 %s" % code)

            # cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            cnt = 7
            print("데이터일수 %s" % cnt)

            # 한번조회하면 600일치 일봉데이터를 받을 수 있다.
            self.calcul_data.clear()
            sum = 0
            for i in range(cnt):
                print(i)
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "거래대금")
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                row_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                data.append("")  # GetCommDataEx 함수와 동일형태로 만들어주기 위해
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(row_price.strip())
                data.append("")

                self.calcul_data.append(data.copy())

            # 4일 평균가
            zeroRate = (int(self.calcul_data[0][1]) - int(self.calcul_data[0][5])) / int(self.calcul_data[0][5]) *100
            oneRate = (int(self.calcul_data[1][1]) - int(self.calcul_data[1][5])) / int(self.calcul_data[1][5]) *100

            twoRate = (int(self.calcul_data[2][1]) - int(self.calcul_data[2][5])) / int(self.calcul_data[2][5]) *100
            twoCenterValue = (int(self.calcul_data[2][1]) + int(self.calcul_data[2][5])) /2

            threeRate = (int(self.calcul_data[3][1]) - int(self.calcul_data[3][5])) / int(self.calcul_data[3][5]) *100
            threeCenterValue = (int(self.calcul_data[3][1]) + int(self.calcul_data[3][5])) / 2

            fourRate = (int(self.calcul_data[4][1]) - int(self.calcul_data[4][5])) / int(self.calcul_data[4][5]) *100
            fourCenterValue = (int(self.calcul_data[4][1]) + int(self.calcul_data[4][5])) / 2

            fiveRate = (int(self.calcul_data[5][1]) - int(self.calcul_data[5][5])) / int(self.calcul_data[5][5]) *100
            fiveCenterValue = (int(self.calcul_data[5][1]) + int(self.calcul_data[5][5])) / 2

            sixRate = (int(self.calcul_data[6][1]) - int(self.calcul_data[6][5])) / int(self.calcul_data[6][5]) *100
            sixCenterValue = (int(self.calcul_data[6][1]) + int(self.calcul_data[6][5])) / 2

            print(twoRate)
            print(twoCenterValue)

            if code not in self.meme_stock_list.keys():

                if twoRate>10:
                    if int(self.calcul_data[2][1]) * 1.05 > int(self.calcul_data[1][1]) and int(self.calcul_data[1][1]) > twoCenterValue:
                        self.meme_stock_list.update({code:{}})
                        self.meme_stock_list[code].update({"손절기준가":self.calcul_data[2][5]})
                        self.meme_stock_list[code].update({"중간값": twoCenterValue})

                elif threeRate>10:
                    if int(self.calcul_data[3][1]) * 1.05 > int(self.calcul_data[2][1]) and int(self.calcul_data[3][1]) * 1.05 > int(self.calcul_data[1][1])\
                        and int(self.calcul_data[2][1])>threeCenterValue and int(self.calcul_data[1][1])>threeCenterValue:
                        self.meme_stock_list.update({code: {}})
                        self.meme_stock_list[code].update({"손절기준가": self.calcul_data[3][5]})
                        self.meme_stock_list[code].update({"중간값": threeCenterValue})

                elif fourRate>10:
                    if int(self.calcul_data[4][1]) * 1.05 > int(self.calcul_data[3][1]) and int(self.calcul_data[4][1]) * 1.05 >\
                        int(self.calcul_data[2][1]) and int(self.calcul_data[4][1]) * 1.05 > int(self.calcul_data[1][1]) and \
                        int(self.calcul_data[3][1])>fourCenterValue and int(self.calcul_data[2][1])>fourCenterValue and \
                        int(self.calcul_data[1][1]) > fourCenterValue:
                        self.meme_stock_list.update({code: {}})
                        self.meme_stock_list[code].update({"손절기준가": self.calcul_data[4][5]})
                        self.meme_stock_list[code].update({"중간값": fourCenterValue})

                elif fiveRate > 10:
                    if int(self.calcul_data[5][1]) * 1.05 > int(self.calcul_data[4][1]) and int(self.calcul_data[5][1]) * 1.05 > \
                        int(self.calcul_data[3][1]) and int(self.calcul_data[5][1]) * 1.05 > int(self.calcul_data[2][1]) and \
                        int(self.calcul_data[5][1]) * 1.05 > int(self.calcul_data[1][1]) and int(self.calcul_data[4][1]) > fiveCenterValue\
                        and int(self.calcul_data[3][1]) > fiveCenterValue and int(self.calcul_data[2][1]) > fiveCenterValue and \
                        int(self.calcul_data[1][1]) > fiveCenterValue:
                        self.meme_stock_list.update({code: {}})
                        self.meme_stock_list[code].update({"손절기준가": self.calcul_data[5][5]})
                        self.meme_stock_list[code].update({"중간값": fiveCenterValue})

                elif sixRate > 10:
                    if int(self.calcul_data[6][1]) * 1.05 > int(self.calcul_data[5][1]) and int(self.calcul_data[6][1]) * 1.05 > \
                        int(self.calcul_data[4][1]) and int(self.calcul_data[6][1]) * 1.05 > int(self.calcul_data[3][1]) and \
                        int(self.calcul_data[6][1]) * 1.05 > int(self.calcul_data[2][1]) and int(self.calcul_data[6][1]) * 1.05 > \
                        int(self.calcul_data[1][1]) and int(self.calcul_data[5][1]) > sixCenterValue and int(self.calcul_data[4][1]) > \
                        sixCenterValue and int(self.calcul_data[3][1]) > sixCenterValue and int(self.calcul_data[2][1]) > \
                        sixCenterValue and int(self.calcul_data[1][1]) > sixCenterValue:
                        self.meme_stock_list.update({code: {}})
                        self.meme_stock_list[code].update({"손절기준가": self.calcul_data[6][5]})
                        self.meme_stock_list[code].update({"중간값": sixCenterValue})

            # self.price_sum[code].update({'합계': sum})
            print(self.meme_stock_list)

            self.calculator_event_loop.exit()

    ###########################################################################################
    ########################################실시간 slot#########################################
    ###########################################################################################

    def realdata_slot(self, sCode, sRealType, sRealData):

        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']
            value = self.dynamicCall("GetCommRealData(QString, int)", sCode, fid)

            if value == "0":
                print("장 시작 전")
                self.market_open_f = "N"
            elif value == "3":
                print("장 시작")
                self.market_open_f = "Y"
                self.stock_research()
            elif value == "2":
                print("장 종료, 동시호가로 넘어감")
                self.market_open_f = "Z"

                for sCode in self.online_jango_dict.keys():
                    order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                        , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                           sCode,  self.online_jango_dict[sCode]['주문가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])


            elif value == "4":
                print("3시 30분 장 종료")
                self.market_open_f = "N"
                for code in self.portfolio_stock_dict.keys():
                    self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['주문용스크린번호'],
                                     code)

                # del self.jongmok1_hoga

                # self.file_delete()
                # self.calculator_fnc()
                self.jango_dict.clear()

                sys.exit()

        elif sRealType == "주식호가잔량":

            if sCode in self.portfolio_stock_dict.keys():

                medohogatotalcnt = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['매도호가총잔량'])
                mesuhogatotalcnt = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                                    self.realType.REALTYPE[sRealType]['매수호가총잔량'])

                madoprice1 = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['매도호가1'])
                madoQ1 = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                              self.realType.REALTYPE[sRealType]['매도호가수량1'])

                madoprice2 = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                              self.realType.REALTYPE[sRealType]['매도호가2'])
                madoQ2 = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                          self.realType.REALTYPE[sRealType]['매도호가수량2'])
                madoprice3 = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                              self.realType.REALTYPE[sRealType]['매도호가3'])
                madoQ3 = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                          self.realType.REALTYPE[sRealType]['매도호가수량3'])
                madoprice4 = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                              self.realType.REALTYPE[sRealType]['매도호가4'])
                madoQ4 = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                          self.realType.REALTYPE[sRealType]['매도호가수량4'])
                madoprice5 = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                              self.realType.REALTYPE[sRealType]['매도호가5'])
                madoQ5 = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                          self.realType.REALTYPE[sRealType]['매도호가수량5'])

                # print("코드:%s, 매도1호가:%s, 매수1호가수량:%s" %(sCode, madoprice1, madoQ1))


                self.portfolio_stock_dict[sCode].update({"매도호가총잔량": medohogatotalcnt})
                self.portfolio_stock_dict[sCode].update({"매수호가총잔량": mesuhogatotalcnt})

                gajungmedoSum1 = int(madoQ1) + int(madoQ2)
                gajungmedoSum2 = int(madoQ3) + int(madoQ4) + int(madoQ5)

                self.portfolio_stock_dict[sCode].update({"매도1잔량합": gajungmedoSum1})
                self.portfolio_stock_dict[sCode].update({"매도2잔량합": gajungmedoSum2})


        elif sRealType == "주식체결":
            # print("주식체결:%s" % sCode)
            a = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                 self.realType.REALTYPE[sRealType]['체결시간'])  # HHMMSS

            b = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                 self.realType.REALTYPE[sRealType]['현재가'])  # +(-)2500
            b = abs(int(b))

            c = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['전일대비'])
            c = abs(int(c))

            d = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['등락율'])
            d = abs(float(d))

            e = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매도호가'])
            e = abs(int(e))

            f = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매수호가'])
            f = abs(int(f))

            rowg = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['거래량'])
            g = abs(int(rowg))
            rowg=int(rowg)
            h = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['누적거래량'])
            h = abs(int(h))

            y = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['고가'])
            y = abs(int(y))

            j = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['시가'])
            j = abs(int(j))

            k = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['저가'])
            k = abs(int(k))

            if sCode not in self.portfolio_stock_dict.keys():
                 return None
            else:
                #self.portfolio_stock_dict.update({sCode: {}})

                self.portfolio_stock_dict[sCode].update({"체결시간": a})
                self.portfolio_stock_dict[sCode].update({"현재가": b})
                self.portfolio_stock_dict[sCode].update({"전일대비": c})
                self.portfolio_stock_dict[sCode].update({"등락율": d})
                self.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
                self.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
                self.portfolio_stock_dict[sCode].update({"거래량": g})
                self.portfolio_stock_dict[sCode].update({"누적거래량": h})
                self.portfolio_stock_dict[sCode].update({"고가": y})
                self.portfolio_stock_dict[sCode].update({"시가": j})
                self.portfolio_stock_dict[sCode].update({"저가": k})
            #print(self.portfolio_stock_dict)


            mesucnt = self.portfolio_stock_dict[sCode]['매수갯수']
            # mesuQ = self.portfolio_stock_dict[sCode]['매수수량']

            mesucnt = int(mesucnt) + 1

            mok = int(mesucnt // 50)
            nameargi = int(mesucnt % 50)

            if mesucnt <51:
                mesusurang = str(mesucnt) + "매수수량"
                mesusuQ = str(mesucnt) + "매수크기"
                self.portfolio_stock_dict[sCode].update({"매수갯수": mesucnt})
                self.portfolio_stock_dict[sCode].update({mesusurang: (b * rowg)})
                self.portfolio_stock_dict[sCode].update({mesusuQ: abs(rowg)})

            else:
                tempMe = (mok - 1) * 50 + nameargi
                mesusurang1 = str(tempMe) + "매수수량"
                mesusurang = str(mesucnt) + "매수수량"
                mesusuQ = str(mesucnt) + "매수크기"
                mesusuQ1 = str(tempMe) + "매수크기"

                del self.portfolio_stock_dict[sCode][mesusurang1]
                del self.portfolio_stock_dict[sCode][mesusuQ1]

                self.portfolio_stock_dict[sCode].update({"매수갯수": mesucnt})
                self.portfolio_stock_dict[sCode].update({mesusurang: (b * rowg)})
                self.portfolio_stock_dict[sCode].update({mesusuQ: rowg})

            sumCnt = 0
            if mesucnt > 49:
                sumCnt = mesucnt - 49
            else:
                sumCnt = 1

            hogaRange = range(sumCnt, mesucnt + 1)
            hogaSum = 0
            hogaQ = 0
            for m in hogaRange:
                temphogastr = str(m) + "매수수량"
                temphogastr1 = str(m) + "매수크기"


                hogaSum += int(self.portfolio_stock_dict[sCode][temphogastr])
                hogaQ += int(self.portfolio_stock_dict[sCode][temphogastr1])

            self.portfolio_stock_dict[sCode].update({"호가썸":hogaSum})
            self.portfolio_stock_dict[sCode].update({"호가량": hogaQ})

            # mesugangdo = int(self.portfolio_stock_dict[sCode]['호가량'])/int(self.portfolio_stock_dict[sCode]['매도5잔량가중평균'])*100

            # mesugangdoRate = float(mesugangdo)/float(self.portfolio_stock_dict[sCode]["매수강도"])

            if int(self.portfolio_stock_dict[sCode]['호가량'])>int(self.portfolio_stock_dict[sCode]['매도1잔량합'])*0.8\
                and int(self.portfolio_stock_dict[sCode]['호가량'])>int(self.portfolio_stock_dict[sCode]['매도2잔량합'])*0.5:
                self.portfolio_stock_dict[sCode].update({"매수강도조건확인":"Y"})
                # print("종목:%s,호가량:%s,매수1잔량:%s,매수2잔량:%s, 시간:%s" % (sCode, hogaQ, self.portfolio_stock_dict[sCode]['매도1잔량합'], self.portfolio_stock_dict[sCode]['매도2잔량합'], a))
            else:
                self.portfolio_stock_dict[sCode].update({"매수강도조건확인": "N"})



            # self.portfolio_stock_dict[sCode].update({"매수강도":mesugangdo})
            # self.portfolio_stock_dict[sCode].update({"매수강도비율": mesugangdoRate})



            # 매수가 매도가 1호가 위로 설정
            mesuB = 0
            medoB = 0
            hoga = 0
            # if self.portfolio_stock_dict[sCode]['시장구분'] == 0:
            #     if b >= 500000:
            #         hoga = 1000
            #     elif 500000 > b >= 100000:
            #         hoga = 500
            #     elif 100000 > b >= 50000:  # 호가단위 백원
            #         hoga = 100
            #     elif 50000 > b >= 10000:
            #         hoga = 50
            #     elif 10000 > b >= 5000:
            #         hoga = 10
            #     elif 5000 > b >= 1000:
            #         hoga = 5
            #     elif 1000 > b:
            #         hoga = 1
            # elif self.portfolio_stock_dict[sCode]['시장구분'] == 10:
            #     if b >= 50000:  # 호가단위 백원
            #         hoga = 100
            #     elif 50000 > b >= 10000:
            #         hoga = 50
            #     elif 10000 > b >= 5000:
            #         hoga = 10
            #     elif 5000 > b >= 1000:
            #         hoga = 5
            #     elif 1000 > b:
            #         hoga = 1

            mesuB = b + hoga
            medoB = b - hoga
            
            # if self.portfolio_stock_dict[sCode]['처음1'] == "Y":
            #     self.portfolio_stock_dict[sCode].update({"맥스고가": j})
            #     tempJuga = int(j) * 0.97
            #     tempJuga = int(tempJuga)
            #     self.portfolio_stock_dict[sCode].update({"맥스저가": tempJuga})
            #     self.portfolio_stock_dict[sCode].update({"처음1":"N"})

            #체결시간
            meme = self.currentDay + a
            memeTime = datetime.datetime.strptime(meme, "%Y%m%d%H%M%S")

            timeline = range(0, 130)

            startTimeF = "N"
            endTimeF = "N"
            maxTimeF = "N"

            for i in timeline:
                startTime = self.baseTime + datetime.timedelta(minutes=(3 * i))
                endTime = self.baseTime + datetime.timedelta(minutes=(3 * (i + 1)))


                if memeTime >= startTime and endTime > memeTime:

                    timerate1 = self.baseTime + datetime.timedelta(minutes=(3 * i + 1))
                    timerate2 = self.baseTime + datetime.timedelta(minutes=(3 * i + 2))

                    if timerate1 > memeTime:
                        self.portfolio_stock_dict[sCode].update({"시간비율": "F"})
                    elif timerate2 > memeTime:
                        self.portfolio_stock_dict[sCode].update({"시간비율": "T"})
                    else:
                        self.portfolio_stock_dict[sCode].update({"시간비율": "A"})


                    if startTime >= self.mesuEndTime:
                        endTimeF = "Y"

                    if startTime >= self.maxTime :
                        maxTimeF = "Y"

                    if self.mesuStartTime >= startTime:
                        startTimeF = "Y"

                    self.startTime1 = startTime + datetime.timedelta(minutes=1)



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

                        self.portfolio_stock_dict[sCode].update({"처음":"N"})

                        self.portfolio_stock_dict[sCode].update({"순번": i})

                        self.portfolio_stock_dict[sCode].update({'15분봉시가1':b})

                    elif self.portfolio_stock_dict[sCode]['순번'] == i:

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmJongga: b})

                        if b > self.portfolio_stock_dict[sCode][self.bunbongNmGoga]:
                            self.portfolio_stock_dict[sCode].update({self.bunbongNmGoga: b})

                        if self.portfolio_stock_dict[sCode][self.bunbongNmJuga] > b:
                            self.portfolio_stock_dict[sCode].update({self.bunbongNmJuga: b})

                        sumQ = int(self.portfolio_stock_dict[sCode][self.bunbongQuant]) + g
                        self.portfolio_stock_dict[sCode].update({self.bunbongQuant:sumQ})

                    else:
                        #if i == 5:
                           # self.portfolio_stock_dict[sCode].update(
                               # {'15분봉종가1':self.portfolio_stock_dict[sCode]["4분봉종가"]})
                           # self.portfolio_stock_dict[sCode].update({'15분봉시가2': b})
                        #elif i == 10:
                         #   self.portfolio_stock_dict[sCode].update(
                        #        {'15분봉종가2': self.portfolio_stock_dict[sCode]["9분봉종가"]})

                        self.portfolio_stock_dict[sCode].update({"순번":i})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmSiga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmJongga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmGoga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmJuga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongQuant: g})

                        cnt = self.portfolio_stock_dict[sCode]["분봉갯수"]

                        self.portfolio_stock_dict[sCode].update({"분봉갯수":cnt+1})
                    break


            ############################# 매수 #########################################
            
            if self.portfolio_stock_dict[sCode]['분봉갯수'] >0 and endTimeF=="N" :
                    # and startTimeF == "Y":



                #print(self.portfolio_stock_dict[sCode])

                bunsiga = self.portfolio_stock_dict[sCode][self.bunbongNmSiga]
                bunjongga = self.portfolio_stock_dict[sCode][self.bunbongNmJongga]

                rate = (bunjongga - bunsiga)/ bunsiga *100
                midle = (bunjongga + bunsiga)/2
                resultcnt = self.portfolio_stock_dict[sCode]['결과갯수']
                bongcnt = self.portfolio_stock_dict[sCode]['분봉갯수']
                startSn = self.portfolio_stock_dict[sCode]['순번']-(bongcnt-resultcnt)
                endSn = self.portfolio_stock_dict[sCode]['순번']
                result = self.portfolio_stock_dict[sCode]['결과']
                janunManjok ="Y"
                janunManjok2 = "Y"
                totalMaxGoga = self.portfolio_stock_dict[sCode]['총맥스고가']


                maxGoga = self.portfolio_stock_dict[sCode]['맥스고가']
                maxJuga = self.portfolio_stock_dict[sCode]['맥스저가']
                maxQuant = self.portfolio_stock_dict[sCode]['맥스거래량']

                mesuManjockCnt1 = self.portfolio_stock_dict[sCode]['만족갯수1']
                mesuManjockCnt2 = self.portfolio_stock_dict[sCode]['만족갯수2']
                preunitsiga = self.portfolio_stock_dict[sCode]['전시가']
                preunitjonga = self.portfolio_stock_dict[sCode]['전종가']
                
                gap = self.portfolio_stock_dict[sCode]['맥스갭']

                unitRowPrice = self.portfolio_stock_dict[sCode]['만족갯수저가']
                
               # basePrice = self.portfolio_stock_dict[sCode]['가격']


                jogun = range(startSn, endSn)

                if bongcnt > resultcnt:
                    for z in jogun:

                        unitbunbongNmSiga = str(z) + "분봉시가"
                        unitbunbongNmJongga = str(z) + "분봉종가"
                        unitbunbongNmGoga = str(z) + "분봉고가"
                        unitbunbongNmJuga = str(z) + "분봉저가"
                        unitbunbongQuant = str(z) + "분봉거래량"

                        # if unitbunbongNmSiga not in self.portfolio_stock_dict[sCode]:
                        #     continue
                        if unitbunbongNmSiga not in self.portfolio_stock_dict[sCode]:
                            continue

                        unitsiga = self.portfolio_stock_dict[sCode][unitbunbongNmSiga]
                        unitjonga = self.portfolio_stock_dict[sCode][unitbunbongNmJongga]
                        unitgoga = self.portfolio_stock_dict[sCode][unitbunbongNmGoga]
                        unitjuga = self.portfolio_stock_dict[sCode][unitbunbongNmJuga]
                        
                        unitQuant = self.portfolio_stock_dict[sCode][unitbunbongQuant]

                        # if mesuManjockCnt1 > 15:
                        #     if unitsiga >maxGoga and unitjonga>maxGoga :
                        #         self.portfolio_stock_dict[sCode].update({"매수가능여부":"N"})


                        # unitgoga = 0

                        if unitjonga > totalMaxGoga:
                            self.portfolio_stock_dict[sCode].update({'총맥스고가': unitjonga})


                        unitjuga = 0
                        bongHighGgori = 0
                        bongGrowRate = (unitjonga - unitsiga)/unitsiga *100
                        bongGrowRate1 = (unitgoga - unitjonga) / unitgoga * 100
                        if unitjonga - unitsiga > 0 and unitgoga - unitjonga > 0:

                            bongHighGgori = (unitgoga - unitjonga) / (unitjonga - unitsiga) *100



                        if unitjonga > unitsiga:
                            if unitRowPrice == 0:
                                unitRowPrice = unitsiga
                            else:
                                if unitRowPrice > unitsiga:
                                    unitRowPrice = unitsiga
                        else:
                            if unitRowPrice == 0:
                                unitRowPrice = unitjonga
                            else:
                                if unitRowPrice > unitjonga:
                                    unitRowPrice = unitjonga


                        if maxJuga == 0:
                            maxJuga = unitjuga
                        else:
                            if maxJuga > unitjuga:
                                maxJuga = unitjuga

                        if self.portfolio_stock_dict[sCode]['등락율'] > 25:
                            # print("25프로 이상종목 제외:%s"%sCode)
                            self.portfolio_stock_dict[sCode].update({"맥스고가": 0})
                            self.portfolio_stock_dict[sCode].update({"맥스저가": 0})
                            mesuManjockCnt1 = 0
                            self.portfolio_stock_dict[sCode].update({"만족갯수1": mesuManjockCnt1})
                            mesuManjockCnt2 = 0
                            self.portfolio_stock_dict[sCode].update({"만족갯수2": mesuManjockCnt2})
                            self.portfolio_stock_dict[sCode].update({"만족갯수저가": 0})
                            self.portfolio_stock_dict[sCode].update({"매수기준가1": 0})
                            self.portfolio_stock_dict[sCode].update({"매수기준가2": 0})
                            self.portfolio_stock_dict[sCode].update({"매수기준가3": 0})

                        else:
                            if float(bongGrowRate) >= 3.5 and unitsiga > j and 50>bongHighGgori\
                             and unitjonga>=self.portfolio_stock_dict[sCode]['총맥스고가']:

                                print("3.5프로 양봉 종목 :%s, 시간:%s" % (sCode, a))

                                self.portfolio_stock_dict[sCode].update({"맥스고가": unitjonga})
                                # self.portfolio_stock_dict[sCode].update({"맥스저가": unitsiga})
                                self.portfolio_stock_dict[sCode].update({"양봉률":bongGrowRate})
                                mesuManjockCnt1 = 0
                                self.portfolio_stock_dict[sCode].update({"만족갯수1": mesuManjockCnt1})
                                mesuManjockCnt2 = 0
                                self.portfolio_stock_dict[sCode].update({"만족갯수2": mesuManjockCnt2})
                                self.portfolio_stock_dict[sCode].update({"만족갯수저가": 0})
                                self.portfolio_stock_dict[sCode].update({"매수기준가1": 0})
                                self.portfolio_stock_dict[sCode].update({"매수기준가2": 0})
                                self.portfolio_stock_dict[sCode].update({"매수기준가3": 0})
                            else:
                                if int(self.portfolio_stock_dict[sCode]['맥스고가']) == 0:
                                    continue
                                else:
                                    if bongGrowRate1 >= 2.0:
                                        print("큰음봉 제외:%s, 음봉율:%s" %(sCode,bongGrowRate1))
                                        self.portfolio_stock_dict[sCode].update({"맥스고가": 0})
                                        self.portfolio_stock_dict[sCode].update({"맥스저가": 0})
                                        mesuManjockCnt1 = 0
                                        self.portfolio_stock_dict[sCode].update({"만족갯수1": mesuManjockCnt1})
                                        mesuManjockCnt2 = 0
                                        self.portfolio_stock_dict[sCode].update({"만족갯수2": mesuManjockCnt2})
                                        self.portfolio_stock_dict[sCode].update({"만족갯수저가": 0})
                                        self.portfolio_stock_dict[sCode].update({"매수기준가1": 0})
                                        self.portfolio_stock_dict[sCode].update({"매수기준가2": 0})
                                        self.portfolio_stock_dict[sCode].update({"매수기준가3": 0})

                                        # 미체결 취소
                                        if sCode in self.not_account_stock_dict.keys():
                                            notChegualCnt = int(self.not_account_stock_dict[sCode]['미체결수량'])
                                            jumunNum = self.not_account_stock_dict[sCode]['주문번호']

                                            if notChegualCnt == '':
                                                notChegualCnt = 0
                                            else:
                                                notChegualCnt = int(notChegualCnt)

                                            if notChegualCnt > 0:
                                                # 매수시도 분봉 지나면 매수주문 취소

                                                print("미체결취소:%s, %s, %s" % (sCode, notChegualCnt, memeTime))
                                                order_success = self.dynamicCall(
                                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                    ["매수취소", self.portfolio_stock_dict[sCode]['주문용스크린번호'],
                                                     self.account_num, 3,
                                                     sCode, notChegualCnt, b,
                                                     self.realType.SENDTYPE['거래구분']['지정가'], jumunNum])

                                                if order_success == 0:
                                                    print("주문취소:%s" % sCode)
                                                    del self.not_account_stock_dict[sCode]

                                    else:
                                        if int(self.portfolio_stock_dict[sCode]['맥스고가'])*1.01 >= unitjonga and \
                                            unitjonga>=int(self.portfolio_stock_dict[sCode]['맥스고가'])*0.99 :
                                                mesuManjockCnt1 += 1
                                                self.portfolio_stock_dict[sCode].update({"만족갯수1": mesuManjockCnt1})
                                                self.portfolio_stock_dict[sCode].update({"맥스저가": maxJuga})
                                                if self.portfolio_stock_dict[sCode]['만족갯수저가']==0:
                                                    self.portfolio_stock_dict[sCode].update({"만족갯수저가":unitRowPrice})

                                                elif self.portfolio_stock_dict[sCode]['만족갯수저가']>unitRowPrice:
                                                    self.portfolio_stock_dict[sCode].update({"만족갯수저가":unitRowPrice})

                                        else:
                                            self.portfolio_stock_dict[sCode].update({"맥스고가":0})
                                            self.portfolio_stock_dict[sCode].update({"맥스저가": 0})
                                            mesuManjockCnt1 = 0
                                            self.portfolio_stock_dict[sCode].update({"만족갯수1": mesuManjockCnt1})
                                            mesuManjockCnt2 = 0
                                            self.portfolio_stock_dict[sCode].update({"만족갯수2": mesuManjockCnt2})
                                            self.portfolio_stock_dict[sCode].update({"만족갯수저가": 0})
                                            self.portfolio_stock_dict[sCode].update({"매수기준가1": 0})
                                            self.portfolio_stock_dict[sCode].update({"매수기준가2": 0})
                                            self.portfolio_stock_dict[sCode].update({"매수기준가3": 0})

                                            # 미체결 취소
                                            if sCode in self.not_account_stock_dict.keys():
                                                notChegualCnt = int(self.not_account_stock_dict[sCode]['미체결수량'])
                                                jumunNum = self.not_account_stock_dict[sCode]['주문번호']

                                                if notChegualCnt == '':
                                                    notChegualCnt = 0
                                                else:
                                                    notChegualCnt = int(notChegualCnt)

                                                if notChegualCnt > 0:
                                                    # 매수시도 분봉 지나면 매수주문 취소

                                                    print("미체결취소:%s, %s, %s" % (sCode, notChegualCnt, memeTime))
                                                    order_success = self.dynamicCall(
                                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                        ["매수취소", self.portfolio_stock_dict[sCode]['주문용스크린번호'],
                                                         self.account_num, 3,
                                                         sCode, notChegualCnt, b,
                                                         self.realType.SENDTYPE['거래구분']['지정가'], jumunNum])

                                                    if order_success == 0:
                                                        print("주문취소:%s" % sCode)
                                                        del self.not_account_stock_dict[sCode]


                        # if unitsiga > unitjonga:
                        #     unitgoga = unitsiga
                        #     unitjuga = unitjonga
                        # else:
                        #     unitgoga = unitjonga
                        #     unitjuga = unitsiga
                        #
                        # if unitgoga >= maxGoga:
                        #     maxGoga = unitgoga
                        #
                        #     self.portfolio_stock_dict[sCode].update({"맥스고가": maxGoga})
                        #
                        #     if self.portfolio_stock_dict[sCode]['만족갯수1'] < 50:
                        #         mesuManjockCnt1 = 0
                        #         self.portfolio_stock_dict[sCode].update({"맥스고가": maxGoga})
                        #         self.portfolio_stock_dict[sCode].update({"맥스시간": maxTimeF})
                        #         self.portfolio_stock_dict[sCode].update({"만족갯수1": mesuManjockCnt1})
                        #         self.portfolio_stock_dict[sCode].update({"맥스갭": 0})
                        # else:
                        #     mesuManjockCnt1 += 1
                        #     self.portfolio_stock_dict[sCode].update({"만족갯수1": mesuManjockCnt1})
                        #
                        #     if unitQuant > maxQuant:
                        #         maxQuant = unitQuant
                        #         # if self.portfolio_stock_dict[sCode]['만족갯수1'] < 20:
                        #         self.portfolio_stock_dict[sCode].update({"맥스거래량": maxQuant})
                        #
                        #     if maxJuga > unitjuga:
                        #         maxJuga = unitjuga
                        #         self.portfolio_stock_dict[sCode].update({"맥스저가": maxJuga})

                        # else:
                        #
                        #     if unitsiga != unitjonga:
                        #
                        #         mesuManjockCnt1 += 1
                        #         self.portfolio_stock_dict[sCode].update({"만족갯수1": mesuManjockCnt1})
                        #         self.portfolio_stock_dict[sCode].update({"만족갯수저가": unitjuga})



                            # else:
                            #     if self.portfolio_stock_dict[sCode]['만족갯수1'] < 15:
                            #         mesuManjockCnt1 = 0
                            #         self.portfolio_stock_dict[sCode].update({"만족갯수1": mesuManjockCnt1})

                        # 맥스갭
                        #unitgap = ((maxGoga - maxJuga) / maxGoga) * 100
                        #if unitgap > gap:
                            #self.portfolio_stock_dict[sCode].update({"맥스갭": unitgap})

                        # 맥스거래량


                        if z == 0:
                            result = "A"
                        else:
                            result = result + "A"

                    self.portfolio_stock_dict[sCode].update({'결과': result})
                    abc = len(self.portfolio_stock_dict[sCode]['결과'])

                    self.portfolio_stock_dict[sCode].update({'결과갯수': abc})

                # print(self.portfolio_stock_dict[sCode])
                if self.portfolio_stock_dict[sCode]['매수가능여부']=="Y":

                    maxGoga2 = self.portfolio_stock_dict[sCode]['맥스고가']
                    maxQ = int(self.portfolio_stock_dict[sCode]['맥스거래량'])
                    medochong = int(self.portfolio_stock_dict[sCode]['매도호가총잔량'])
                    mesuchong = int(self.portfolio_stock_dict[sCode]['매수호가총잔량'])
                    currentQ = int(self.portfolio_stock_dict[sCode][self.bunbongQuant])


                    timerate = 1

                    # if self.portfolio_stock_dict[sCode]['시간비율']  == "F":
                    #     timerate = 0.8
                    # elif self.portfolio_stock_dict[sCode]['시간비율']  == "T":
                    #     timerate = 1.5
                    # elif self.portfolio_stock_dict[sCode]['시간비율']  == "A":
                    #     timerate = 2.0

                    # tempsn = range(endSn-3,endSn)
                    # for y in tempsn:
                    #     mesuganeungjonga = str(y) + "분봉종가"
                    #     mesuganeungQ = str(y) + "분봉거래량"
                    #     if mesuganeungjonga not in self.portfolio_stock_dict[sCode]:
                    #         continue
                    #     if self.portfolio_stock_dict[sCode][mesuganeungjonga]>maxGoga2:
                    #         currentQ = currentQ + int(self.portfolio_stock_dict[sCode][mesuganeungQ])
                    # maxGoga3 = 0
                    # if 100000 > maxGoga2 >= 50000:  # 호가단위 백원
                    #     maxGoga3 = maxGoga2 + 200
                    # elif 50000 > maxGoga2 >= 10000:
                    #     maxGoga3 = maxGoga2 + 100
                    # elif 10000 > maxGoga2 >= 5000:
                    #     maxGoga3 = maxGoga2 + 20
                    # elif 5000 > maxGoga2 >= 1000:
                    #     maxGoga3 = maxGoga2 + 10
                    # elif 1000 > maxGoga2:
                    #     maxGoga3 = maxGoga2 + 2
                    #
                    # maxGoga4 = 0
                    # if 100000 > maxGoga2 >= 50000:  # 호가단위 백원
                    #     maxGoga4 = maxGoga2 - 500
                    # elif 50000 > maxGoga2 >= 10000:
                    #     maxGoga4 = maxGoga2 - 250
                    # elif 10000 > maxGoga2 >= 5000:
                    #     maxGoga4 = maxGoga2 - 50
                    # elif 5000 > maxGoga2 >= 1000:
                    #     maxGoga4 = maxGoga2 - 25
                    # elif 1000 > maxGoga2:
                    #     maxGoga4 = maxGoga2 - 5




                    # if b >50000 :
                    #     if g >50:
                    #         if rowg >0 :
                    #             self.portfolio_stock_dict[sCode].update({"매수갯수":mesucnt+1})
                    #             self.portfolio_stock_dict[sCode].update({"매수수량": mesuQ + (b*g)})
                    #         else:
                    #             self.portfolio_stock_dict[sCode].update({"매수갯수": 0})
                    #             self.portfolio_stock_dict[sCode].update({"매수수량": 0})
                    # elif b>30000:
                    #     if g >100:
                    #         if rowg >0 :
                    #             self.portfolio_stock_dict[sCode].update({"매수갯수":mesucnt+1})
                    #             self.portfolio_stock_dict[sCode].update({"매수수량": mesuQ + (b*g)})
                    #         else:
                    #             self.portfolio_stock_dict[sCode].update({"매수갯수": 0})
                    #             self.portfolio_stock_dict[sCode].update({"매수수량": 0})
                    #
                    # elif b>=10000:
                    #     if g >300:
                    #         if rowg >0 :
                    #             self.portfolio_stock_dict[sCode].update({"매수갯수":mesucnt+1})
                    #             self.portfolio_stock_dict[sCode].update({"매수수량": mesuQ + (b*g)})
                    #         else:
                    #             self.portfolio_stock_dict[sCode].update({"매수갯수": 0})
                    #             self.portfolio_stock_dict[sCode].update({"매수수량": 0})
                    #
                    # elif 10000>b:
                    #     if g >500:
                    #         if rowg >0 :
                    #             self.portfolio_stock_dict[sCode].update({"매수갯수":mesucnt+1})
                    #             self.portfolio_stock_dict[sCode].update({"매수수량": mesuQ + (b*g)})
                    #         else:
                    #             self.portfolio_stock_dict[sCode].update({"매수갯수": 0})
                    #             self.portfolio_stock_dict[sCode].update({"매수수량": 0})

                    #print("호가썸:%s, 매도총:%s, 매수총:%s, 맥스거래량:%s, 현거래량:%s" %(hogaSum,medochong,mesuchong,maxQ,currentQ))
                    if b>=j:

                        #chongRate = int(self.portfolio_stock_dict[sCode]['시가총액'])*0.003*100000000

                        price1 = self.portfolio_stock_dict[sCode]['매수기준가1']
                        price2 = self.portfolio_stock_dict[sCode]['매수기준가2']
                        price3 = self.portfolio_stock_dict[sCode]['매수기준가3']

                        maesuCon = ""
                        maedoPrice = 0

                        if self.portfolio_stock_dict[sCode]['만족갯수1'] >=2:

                            af = self.portfolio_stock_dict[sCode]['매수1여부']
                            bf = self.portfolio_stock_dict[sCode]['매수2여부']
                            cf = self.portfolio_stock_dict[sCode]['매수3여부']

                            # if self.portfolio_stock_dict[sCode]['만족갯수1'] ==2:

                            # if price1 == 0:
                            price1 = self.portfolio_stock_dict[sCode]['만족갯수저가']
                            price3 = int(self.portfolio_stock_dict[sCode]['맥스저가'])
                            price2 = (int(price1) + int(price3)) / 2

                            self.portfolio_stock_dict[sCode].update({"매수기준가1":price1})
                            self.portfolio_stock_dict[sCode].update({"매수기준가2":price2})
                            self.portfolio_stock_dict[sCode].update({"매수기준가3":price3})



                            maesuCon = "case2"
                            maedoPrice = int(self.portfolio_stock_dict[sCode]['맥스저가'])

                            # mesuaverage = int(hogaSum) / int(hogaQ)
                            # self.portfolio_stock_dict[sCode].update({"평균매수가":mesuaverage})
                            quantity1 = int(300000 / b)

                            if b>=self.portfolio_stock_dict[sCode]['매수기준가1'] :

                                if self.portfolio_stock_dict[sCode]['매수1여부']=="N":

                                    print("매수1 - 주문")
                                    print("종목:%s, price1:%s, 매도기준가:%s, 시간:%s, 현재가:%s" % (sCode, price1, maedoPrice, a, b))
                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                        ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                         sCode, quantity1, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                                    if order_success == 0:
                                        self.portfolio_stock_dict[sCode].update({"매수1여부": "Y"})
                                        self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                                        self.portfolio_stock_dict[sCode].update({"매수조건": maesuCon})
                                        self.portfolio_stock_dict[sCode].update({"매수기준가": b})
                                        self.portfolio_stock_dict[sCode].update({"매도기준가": maedoPrice})

                                    # order_success = self.dynamicCall(
                                    #     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                    #     ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                    #      sCode, quantity1, maxGoga2, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    else:
                                        print("매수주문 전달 실패")


            ############################# 매도 #########################################

            if sCode in self.online_jango_dict.keys():

                medoSn = self.portfolio_stock_dict[sCode]['순번']
                mesubunbong = self.portfolio_stock_dict[sCode]['매수분봉']

                ###### 추가매수 #####
                # if self.portfolio_stock_dict[sCode]['추가매수여부']=="N":
                #     if int(medoSn)-1 == int(mesubunbong):
                #
                #         chugamesusibunbong = str(mesubunbong) + "분봉시가"
                #         chugamesujongbunbong = str(mesubunbong) + "분봉종가"
                #         chugamesuQuantitybunbong = str(mesubunbong) + "분봉거래량"
                #
                #         maxQ = int(self.portfolio_stock_dict[sCode]['맥스거래량'])
                #         currentQ = int(self.portfolio_stock_dict[sCode][chugamesuQuantitybunbong])
                #
                #         chugamesusiga = self.portfolio_stock_dict[sCode][chugamesusibunbong]
                #         chugamesujognga = self.portfolio_stock_dict[sCode][chugamesujongbunbong]
                #
                #         chugamesuRate = (chugamesujognga - chugamesusiga)/ chugamesusiga *100
                #
                #         chugahoga = 0
                #
                #         if currentQ >= maxQ:
                #             if chugamesuRate >= 4.0:
                #                 chugahoga = int(chugamesusiga + (chugamesujognga - chugamesusiga) * 0.5)
                #
                #                 quantity = int(300000 / b)
                #
                #                 print("케이스2 코드:%s 시간:%s 가격:%s, 수량:%s, 시가:%s" % (sCode, meme, b, quantity, j))
                #                 #print("재결과:%s" % finalResult2)
                #                 order_success = self.dynamicCall(
                #                     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                #                     ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                #                      sCode, quantity, chugahoga, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                #
                #                 if order_success == 0:
                #                     #self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                #                     #self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                #                     #self.portfolio_stock_dict[sCode].update({"매수조건": "case2"})
                #                     #self.portfolio_stock_dict[sCode].update({"매수기준가": maxGoga2})
                #                     self.portfolio_stock_dict[sCode].update({"추가매수여부": "Y"})
                #
                #                 else:
                #                     print("매수주문 전달 실패")
                #
                #             elif chugamesuRate >= 2.0:
                #                 chugahoga = int(chugamesusiga + (chugamesujognga - chugamesusiga) * 0.7)
                #
                #                 quantity = int(300000 / b)
                #
                #                 print("케이스3 코드:%s 시간:%s 가격:%s, 수량:%s, 시가:%s" % (sCode, meme, b, quantity, j))
                #                 #print("재결과:%s" % finalResult2)
                #                 order_success = self.dynamicCall(
                #                     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                #                     ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                #                      sCode, quantity, chugahoga, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                #
                #                 if order_success == 0:
                #                     #self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                #                     #self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                #                     #self.portfolio_stock_dict[sCode].update({"매수조건": "case2"})
                #                     #self.portfolio_stock_dict[sCode].update({"매수기준가": maxGoga2})
                #                     self.portfolio_stock_dict[sCode].update({"추가매수여부": "Y"})
                #
                #                 else:
                #                     print("매수주문 전달 실패")



                asd = self.online_jango_dict[sCode]
                meib = int(asd['매입단가'])
                meme_rate = (b - meib) / meib * 100  # 등락률

                maxRate = self.portfolio_stock_dict[sCode]['최고수익률']

                if float(meme_rate) > float(maxRate) :
                    self.portfolio_stock_dict[sCode].update({"최고수익률":meme_rate})

                self.online_jango_dict[sCode].update({"수익률":meme_rate})
                #print(meme_rate)

                mesuGijunga = self.online_jango_dict[sCode]['매입단가']
                tempstr = str(mesubunbong) + "분봉저가"
                sonjulGijunga = self.portfolio_stock_dict[sCode][tempstr]
                
                ikjulCnt = self.portfolio_stock_dict[sCode]['익절횟수']

                medocnt = self.portfolio_stock_dict[sCode]['매도갯수']

                medochong1 = int(self.portfolio_stock_dict[sCode]['매도호가총잔량'])
                mesuchong1 = int(self.portfolio_stock_dict[sCode]['매수호가총잔량'])

                maedogijunPrice = self.portfolio_stock_dict[sCode]['매도기준가']



                medocnt = int(medocnt) + 1

                mok1 = int(medocnt // 50)
                nameargi1 = int(medocnt % 50)

                if mok1 == 0 or nameargi1 == 0:
                    medosurang = str(medocnt) + "매도수량"
                    self.portfolio_stock_dict[sCode].update({"매도갯수": medocnt})
                    self.portfolio_stock_dict[sCode].update({medosurang: (b * rowg)})

                else:
                    tempMe1 = (mok1 - 1) * 50 + nameargi1
                    medosurang1 = str(tempMe1) + "매도수량"
                    medosurang = str(medocnt) + "매도수량"

                    del self.portfolio_stock_dict[sCode][medosurang1]

                    self.portfolio_stock_dict[sCode].update({"매도갯수": medocnt})
                    self.portfolio_stock_dict[sCode].update({medosurang: (b * rowg)})

                sumCnt1 = 0
                if medocnt > 49:
                    sumCnt1 = medocnt - 49
                else:
                    sumCnt1 = 1

                hogaRange1 = range(sumCnt1, medocnt + 1)
                hogaSum1 = 0
                for n in hogaRange1:
                    temphogastr = str(n) + "매도수량"

                    hogaSum1 += int(self.portfolio_stock_dict[sCode][temphogastr])


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

                        jonga_meme_rate = ((medoUnitJonga-meib) / meib) * 100

                        # if 1.0 > jonga_meme_rate:
                        #     ikjuljojunmanjok = "Y"

                        # if mesuGijunga > medoUnitJonga or sonjulGijunga > medoUnitJonga:
                        #     madojanunManjok = "Y"
                        #
                        # if g == mesubunbong:
                        #     if mesuGijunga >= medoUnitJonga:
                        #         if medounitgoga-medoUnitJonga>medoUnitJonga-medounitsiga:
                        #             madojanunManjok2="Y"

                        if maedogijunPrice>medoUnitJonga:
                            self.portfolio_stock_dict[sCode].update({"손절만족":"Y"})



                bunsiga = self.portfolio_stock_dict[sCode][self.bunbongNmSiga]
                bunjongga = self.portfolio_stock_dict[sCode][self.bunbongNmJongga]
                sonjulCnt = self.portfolio_stock_dict[sCode]['손절횟수']

                sojulRate = ((meib - b) / meib) * 100

                # chongRate1 = int(self.portfolio_stock_dict[sCode]['시가총액']) * 0.001 * 100000000
                #chongRate2 = int(self.portfolio_stock_dict[sCode]['시가총액']) * 0.0001 * 100000000
                medoRate2 = rowg * b

                if self.online_jango_dict[sCode]['수익률'] > 0:
                    # print(meme_rate)
                    # print(asd['주문가능수량'])
                    if self.portfolio_stock_dict[sCode]['최고수익률']-3 > self.online_jango_dict[sCode]['수익률']:

                        print("최소수익률대비 3프로 하락")

                        ikjulmedoCnt = int(asd['주문가능수량'])

                        order_success = self.dynamicCall(
                            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                            , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                               sCode, ikjulmedoCnt, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                        if order_success == 0:
                            self.portfolio_stock_dict[sCode].update({"매도가": b})
                            self.portfolio_stock_dict[sCode].update({'익절0': "X"})
                            self.portfolio_stock_dict[sCode].update({"매수가능여부":"N"})
                            print("매도주문 전달 성공")
                        else:
                            print("매도주문 전달 실패")

                    else:
                        gijunP1 = 0
                        gijunP2 = 0
                        gijunP3 = 0
                        gijunP4 = 0
                        if self.portfolio_stock_dict[sCode]['매수3여부'] == "Y":
                            gijunP1 = 0.4
                            gijunP2 = 0.7
                            gijunP3 = 1.0
                            gijunP4 = 2.0
                        else:
                            gijunP1 = 0.7
                            gijunP2 = 1.5
                            gijunP3 = 2.5
                            gijunP4 = 5.0

                        if asd['주문가능수량'] > 0 and 0.5 > self.online_jango_dict[sCode]['수익률']:

                            if self.portfolio_stock_dict[sCode]['익절0'] == "Y":

                                profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                                print("즉시익절_0.5프로 매도:%s, 수익률:%s,매입단가:%s,현재가:%s,시간:%s" % (sCode, meme_rate,meib,b,meme))

                                ikjulmedoCnt = int(asd['주문가능수량'])/1

                                order_success = self.dynamicCall(
                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                    , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                       sCode, ikjulmedoCnt, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                                if order_success == 0:
                                    self.portfolio_stock_dict[sCode].update({"매도가": b})
                                    self.portfolio_stock_dict[sCode].update({'익절0': "X"})
                                    self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                    print("매도주문 전달 성공")
                                else:
                                    print("매도주문 전달 실패")

                            if self.portfolio_stock_dict[sCode]['익절1'] == "Y":

                                profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                                print("즉시익절02프로 매도:%s, 수익률:%s,매입단가:%s,현재가:%s,시간:%s" % (sCode, meme_rate,meib,b,meme))

                                ikjulmedoCnt = int(asd['주문가능수량'])

                                order_success = self.dynamicCall(
                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                    , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                       sCode, ikjulmedoCnt, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                                if order_success == 0:
                                    self.portfolio_stock_dict[sCode].update({"매도가": b})
                                    self.portfolio_stock_dict[sCode].update({'익절0': "X"})
                                    self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                    print("매도주문 전달 성공")
                                else:
                                    print("매도주문 전달 실패")

                        if asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] >= 0.5:
                            if self.portfolio_stock_dict[sCode]['손절']=="Y":
                                ikjulmedoCnt = int(asd['주문가능수량']) / 2

                                order_success = self.dynamicCall(
                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                    , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                       sCode, ikjulmedoCnt, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                                if order_success == 0:
                                    self.portfolio_stock_dict[sCode].update({"매도가": b})
                                    self.portfolio_stock_dict[sCode].update({'손절': "N"})
                                    self.portfolio_stock_dict[sCode].update({'익절0': "Y"})
                                    self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                    print("매도주문 전달 성공")
                                else:
                                    print("매도주문 전달 실패")


                        if asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] >= gijunP1:

                            if self.portfolio_stock_dict[sCode]['익절0'] == "N":

                                profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                                print("즉시익절_0.7프로 매도:%s, 수익률:%s,매입단가:%s,현재가:%s,시간:%s" % (sCode, meme_rate,meib,b,meme))

                                ikjulmedoCnt = int(asd['주문가능수량']) / 4
                                if ikjulmedoCnt>0 and 1>ikjulmedoCnt:
                                    ikjulmedoCnt = 1

                                order_success = self.dynamicCall(
                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                    , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                       sCode, ikjulmedoCnt, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                                if order_success == 0:
                                    self.portfolio_stock_dict[sCode].update({"매도가": b})
                                    self.portfolio_stock_dict[sCode].update({'익절0': "Y"})
                                    self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                    print("매도주문 전달 성공")
                                else:
                                    print("매도주문 전달 실패")

                        if asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] >= gijunP2:

                            if self.portfolio_stock_dict[sCode]['익절1'] == "N":

                                profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                                print("즉시익절_1.5프로 매도:%s, 수익률:%s,매입단가:%s,현재가:%s,시간:%s" % (sCode, meme_rate,meib,b,meme))

                                ikjulmedoCnt = int(asd['주문가능수량']) / 3
                                if ikjulmedoCnt>0 and 1>ikjulmedoCnt:
                                    ikjulmedoCnt = 1

                                order_success = self.dynamicCall(
                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                    , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                       sCode, ikjulmedoCnt, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                                if order_success == 0:
                                    self.portfolio_stock_dict[sCode].update({"매도가": b})
                                    self.portfolio_stock_dict[sCode].update({'익절1': "Y"})
                                    self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                    print("매도주문 전달 성공")
                                else:
                                    print("매도주문 전달 실패")

                        if asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] >= gijunP3:

                            if self.portfolio_stock_dict[sCode]['익절2'] == "N":

                                profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                                print("즉시익절_2.5프로 매도:%s, 수익률:%s,매입단가:%s,현재가:%s,시간:%s" % (sCode, meme_rate,meib,b,meme))

                                ikjulmedoCnt = int(asd['주문가능수량']) / 2
                                if ikjulmedoCnt>0 and 1>ikjulmedoCnt:
                                    ikjulmedoCnt = 1

                                order_success = self.dynamicCall(
                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                    , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                       sCode, ikjulmedoCnt, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                                if order_success == 0:
                                    self.portfolio_stock_dict[sCode].update({"매도가": b})
                                    self.portfolio_stock_dict[sCode].update({'익절2': "Y"})
                                    self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                    print("매도주문 전달 성공")
                                else:
                                    print("매도주문 전달 실패")

                        if asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] >= gijunP4:

                            if self.portfolio_stock_dict[sCode]['익절3'] == "N":

                                profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                                print("즉시익절4프로 매도:%s, 수익률:%s,  시간:%s" % (sCode, meme_rate, meme))

                                ikjulmedoCnt = int(asd['주문가능수량'])/2

                                order_success = self.dynamicCall(
                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                    , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                       sCode, ikjulmedoCnt, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                                if order_success == 0:
                                    self.portfolio_stock_dict[sCode].update({"매도가": b})
                                    self.portfolio_stock_dict[sCode].update({'익절3': "Y"})
                                    self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                    print("매도주문 전달 성공")
                                else:
                                    print("매도주문 전달 실패")

                        if asd['주문가능수량'] > 0 and self.online_jango_dict[sCode]['수익률'] >= 10.0:

                            if self.portfolio_stock_dict[sCode]['익절4'] == "N":

                                profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                                print("즉시익절4프로 매도:%s, 수익률:%s,  시간:%s" % (sCode, meme_rate, meme))

                                ikjulmedoCnt = int(asd['주문가능수량'])

                                order_success = self.dynamicCall(
                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                    , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                       sCode, ikjulmedoCnt, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                                if order_success == 0:
                                    self.portfolio_stock_dict[sCode].update({"매도가": b})
                                    self.portfolio_stock_dict[sCode].update({'익절4': "Y"})
                                    self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                    print("매도주문 전달 성공")
                                else:
                                    print("매도주문 전달 실패")


                #############################################################################

                ################################## 손절 ######################################
                else:

                    mesu = str(mesubunbong) + "분봉거래량"
                    curr = str(medoSn) + "분봉거래량"

                    mesuQnt = int(self.portfolio_stock_dict[sCode][mesu])
                    currQnt = int(self.portfolio_stock_dict[sCode][curr])

                    timerate1 = 1.0

                    if self.portfolio_stock_dict[sCode]['시간비율']  == "F":
                        timerate1 = 0.6
                    elif self.portfolio_stock_dict[sCode]['시간비율']  == "T":
                        timerate1 = 0.8
                    elif self.portfolio_stock_dict[sCode]['시간비율']  == "A":
                        timerate1 = 1.0


                    # 1프로익절 한건이면 -1프에서 전체 손절(본절 처리)
                    if self.portfolio_stock_dict[sCode]['익절0'] == "X":

                        sonjulQuan0 = int(asd['주문가능수량'])

                        print("본절처리")

                        order_success = self.dynamicCall(
                            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                            , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                               sCode, sonjulQuan0, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                        if order_success == 0:
                            self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                            print("매도주문 전달 성공")

                        else:
                            print("매도주문 전달 실패")

                    else:

                        if self.portfolio_stock_dict[sCode]['매도기준가'] > self.portfolio_stock_dict[sCode]['현재가']:

                            if self.portfolio_stock_dict[sCode]['손절만족'] == "Y":

                                sonjulQuan0 = int(asd['주문가능수량'])

                                order_success = self.dynamicCall(
                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                    , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                       sCode, sonjulQuan0, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                                if order_success == 0:
                                    self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                    print("매도주문 전달 성공")

                                else:
                                    print("매도주문 전달 실패")

                        sojulRate1 = -0.5
                        sojulRate2 = -10.0
                        sojulRate3 = -12.0

                        # if currQnt > mesuQnt*timerate1*0.8:
                        #     sojulRate1 = -0.5
                        #     sojulRate2 = -1.0
                        #     sojulRate3 = -1.5
                        # elif currQnt > mesuQnt*timerate1*0.5:
                        #     sojulRate1 = -0.7
                        #     sojulRate2 = -1.0
                        #     sojulRate3 = -1.5
                        # else:
                        #     sojulRate1 = -0.7
                        #     sojulRate2 = -1.0
                        #     sojulRate3 = -1.5

                        # if self.online_jango_dict[sCode]['수익률'] < -5.0:
                        #     self.portfolio_stock_dict[sCode].update({"손절":"Y"})
                        #
                        #
                        # if self.online_jango_dict[sCode]['수익률'] < sojulRate1:
                        #     if self.portfolio_stock_dict[sCode]['손절1'] == "N":
                        #         sonjulQuan0 = int(asd['주문가능수량']) / 2
                        #         sonjulAmount = (meib - b) * sonjulQuan0
                        #         print("손절1 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                        #         print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                        #
                        #         order_success = self.dynamicCall(
                        #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                        #             , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                        #                sCode, int(sonjulQuan0), 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        #
                        #         if order_success == 0:
                        #
                        #             print("매도주문 전달 성공")
                        #             self.portfolio_stock_dict[sCode].update({"손절1":"Y"})
                        #         else:
                        #             print("매도주문 전달 실패")
                        #
                        # if self.online_jango_dict[sCode]['수익률'] < sojulRate2:
                        #     if self.portfolio_stock_dict[sCode]['손절2'] == "N":
                        #         sonjulQuan0 = int(asd['주문가능수량']) / 2
                        #         sonjulAmount = (meib - b) * sonjulQuan0
                        #         print("손절1 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                        #         print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                        #
                        #         order_success = self.dynamicCall(
                        #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                        #             , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                        #                sCode, sonjulQuan0, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        #
                        #         if order_success == 0:
                        #
                        #             print("매도주문 전달 성공")
                        #             self.portfolio_stock_dict[sCode].update({"손절2":"Y"})
                        #         else:
                        #             print("매도주문 전달 실패")
                        #
                        # if self.online_jango_dict[sCode]['수익률'] < sojulRate3:
                        #
                        #     sonjulQuan0 = int(asd['주문가능수량'])
                        #     sonjulAmount = (meib - b) * sonjulQuan0
                        #     print("손절1 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                        #     print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                        #
                        #     order_success = self.dynamicCall(
                        #         "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                        #         , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                        #            sCode, sonjulQuan0, 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                        #
                        #     if order_success == 0:
                        #
                        #         print("매도주문 전달 성공")
                        #         self.portfolio_stock_dict[sCode].update({"손절1":"Y"})
                        #     else:
                        #         print("매도주문 전달 실패")



                    # chongRate1 = int(self.portfolio_stock_dict[sCode]['시가총액']) * 0.001 * 100000000
                    # if int(abs(hogaSum1))>chongRate1 and mesuchong1*2>medochong1:


                    # if madojanunManjok == "Y" or madojanunManjok2 == "Y":
                    #     if self.online_jango_dict[sCode]['수익률'] < -1.5:
                    #         if mesuGijunga > sonjulGijunga:
                    #             if mesuGijunga > b and bunsiga > bunjongga and sonjulCnt == 0:
                    #
                    #                 sonjulQuan1 = int(asd['주문가능수량']) / 2
                    #                 sonjulAmount = (meib - b) * sonjulQuan1
                    #                 print("손절1 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                    #                 print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                    #
                    #                 order_success = self.dynamicCall(
                    #                     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                    #                     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                    #                        sCode, sonjulQuan1, medoB, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    #
                    #                 if order_success == 0:
                    #
                    #                     print("매도주문 전달 성공")
                    #                     self.portfolio_stock_dict[sCode].update({"손절횟수": 1})
                    #                 else:
                    #                     print("매도주문 전달 실패")
                    #
                    #             elif sonjulGijunga > b and bunsiga > bunjongga and 2>sonjulCnt :
                    #
                    #                 if sojulRate>2.0:
                    #                     sonjulQuan2 = int(asd['주문가능수량'])
                    #                 else:
                    #                     sonjulQuan2 = int(asd['주문가능수량'])
                    #
                    #                 sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                    #                 print("손절2 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                    #                 print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                    #                 order_success = self.dynamicCall(
                    #                     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                    #                     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                    #                        sCode, sonjulQuan2, medoB, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    #
                    #                 if order_success == 0:
                    #
                    #                     print("매도주문 전달 성공")
                    #                     soncnt = int(self.portfolio_stock_dict[sCode]['손절횟수'])+1
                    #                     self.portfolio_stock_dict[sCode].update({"손절횟수": soncnt})
                    #                 else:
                    #                     print("매도주문 전달 실패")
                    #
                    #             elif sojulRate>2.0:
                    #
                    #                 sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                    #                 print("손절3 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                    #                 print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                    #                 order_success = self.dynamicCall(
                    #                     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                    #                     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                    #                        sCode, asd['주문가능수량'], medoB, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    #
                    #                 if order_success == 0:
                    #
                    #                     print("매도주문 전달 성공")
                    #                     soncnt = int(self.portfolio_stock_dict[sCode]['손절횟수']) + 1
                    #                     self.portfolio_stock_dict[sCode].update({"손절횟수": soncnt})
                    #                 else:
                    #                     print("매도주문 전달 실패")
                    #
                    #
                    #         else:
                    #             if sonjulGijunga > b and bunsiga > bunjongga and sonjulCnt == 0:
                    #                 sonjulQuan1 = int(asd['주문가능수량']) / 3
                    #                 sonjulAmount = (meib - b) * sonjulQuan1
                    #                 print("손절3 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                    #                 print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                    #                 order_success = self.dynamicCall(
                    #                     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                    #                     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                    #                        sCode, sonjulQuan1, medoB, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    #
                    #                 if order_success == 0:
                    #                     self.portfolio_stock_dict[sCode].update({"손절횟수": 1})
                    #                     print("매도주문 전달 성공")
                    #                 else:
                    #                     print("매도주문 전달 실패")
                    #
                    #             elif mesuGijunga > b and bunsiga > bunjongga and 2>sonjulCnt:
                    #
                    #                 if sojulRate>2.0:
                    #                     sonjulQuan2 = int(asd['주문가능수량'])
                    #                 else:
                    #                     sonjulQuan2 = int(asd['주문가능수량']) / 2
                    #
                    #                 sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                    #                 print("손절4 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                    #                 print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                    #                 order_success = self.dynamicCall(
                    #                     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                    #                     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                    #                        sCode, sonjulQuan2, medoB, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    #
                    #                 if order_success == 0:
                    #
                    #                     print("매도주문 전달 성공")
                    #                     soncnt = int(self.portfolio_stock_dict[sCode]['손절횟수']) + 1
                    #                     self.portfolio_stock_dict[sCode].update({"손절횟수": soncnt})
                    #                 else:
                    #                     print("매도주문 전달 실패")
                    #
                    #             elif sojulRate>2.0:
                    #
                    #                 sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                    #                 print("손절4 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                    #                 print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                    #                 order_success = self.dynamicCall(
                    #                     "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                    #                     , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                    #                        sCode, asd['주문가능수량'], medoB, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    #
                    #                 if order_success == 0:
                    #
                    #                     print("매도주문 전달 성공")
                    #                 else:
                    #                     print("매도주문 전달 실패")


                    # else:
                    #
                    #     if mesuGijunga > sonjulGijunga:
                    #         if mesuGijunga > b and bunsiga > bunjongga and sonjulCnt == 0 and sojulRate > 2.5:
                    #
                    #             sonjulQuan1 = int(asd['주문가능수량']) / 2
                    #             sonjulAmount = (meib - b) * sonjulQuan1
                    #             print("손절5 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                    #             print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                    #             order_success = self.dynamicCall(
                    #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                    #                 , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                    #                    sCode, sonjulQuan1, medoB, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    #
                    #             if order_success == 0:
                    #                 self.portfolio_stock_dict[sCode].update({"손절횟수": 1})
                    #                 print("매도주문 전달 성공")
                    #             else:
                    #                 print("매도주문 전달 실패")
                    #
                    #         elif sonjulGijunga > b and bunsiga > bunjongga and sojulRate > 2.5:
                    #
                    #             sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                    #             print("손절6 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                    #             print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                    #             order_success = self.dynamicCall(
                    #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                    #                 , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                    #                    sCode, asd['주문가능수량'], medoB, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    #
                    #             if order_success == 0:
                    #
                    #                 print("매도주문 전달 성공")
                    #             else:
                    #                 print("매도주문 전달 실패")
                    #
                    #     else:
                    #         if sonjulGijunga > b and bunsiga > bunjongga and sonjulCnt == 0:
                    #             sonjulQuan1 = int(asd['주문가능수량']) / 2
                    #             sonjulAmount = (meib - b) * sonjulQuan1
                    #             print("손절7 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                    #             print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                    #             order_success = self.dynamicCall(
                    #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                    #                 , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                    #                    sCode, sonjulQuan1, medoB, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    #
                    #             if order_success == 0:
                    #                 self.portfolio_stock_dict[sCode].update({"손절횟수": 1})
                    #                 print("매도주문 전달 성공")
                    #             else:
                    #                 print("매도주문 전달 실패")
                    #
                    #         elif mesuGijunga > b and bunsiga > bunjongga:
                    #
                    #             sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                    #             print("손절8 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                    #             print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                    #             order_success = self.dynamicCall(
                    #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                    #                 , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                    #                    sCode, asd['주문가능수량'], medoB, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    #
                    #             if order_success == 0:
                    #
                    #                 print("매도주문 전달 성공")
                    #             else:
                    #                 print("매도주문 전달 실패")


    #################################################################################################
    ############################### 주문 slot #######################################################

    def chejan_slot(self, sGubun, nItemCnt, sFidList):

        if int(sGubun) == 0:
            print("주문체결")
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['계좌번호'])
            rowsCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드'])[1:]
            # print(sCode)
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()

            original_order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['원주문번호'])
            order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문번호'])
            order_status = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문상태'])
            order_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문수량'])
            if order_quan == '':
                order_quan = 0
            else:
                order_quan = int(order_quan)

            order_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문가격'])
            if order_price == '':
                order_price = 0
            else:
                order_price = int(order_price)

            not_chegual_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['미체결수량'])

            if not_chegual_quan == '':
                not_chegual_quan = 0
            else:
                not_chegual_quan = int(not_chegual_quan)

            order_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문구분'])
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')

            # meme_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['매도수구분'])
            # meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]

            chegual_time_str = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간'])

            chegual_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가'])

            if chegual_price == '':
                chegual_price = 0
            else:
                chegual_price = int(chegual_price)

            chegual_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량'])

            if chegual_quantity == '':
                chegual_quantity = 0
            else:
                chegual_quantity = int(chegual_quantity)

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['현재가'])
            if current_price == '':
                current_price = 0
            current_price = abs(int(current_price))

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매도호가'])
            if first_sell_price == '':
                first_sell_price = 0
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매수호가'])
            if first_buy_price == '':
                first_buy_price = 0
            first_buy_price = abs(int(first_buy_price))

            if order_gubun == "매수":
                if not_chegual_quan >0:
                    if sCode not in self.not_account_stock_dict.keys():
                        self.not_account_stock_dict.update({sCode:{}})

                    self.not_account_stock_dict[sCode].update({"주문번호": order_number})
                    self.not_account_stock_dict[sCode].update({"미체결수량":not_chegual_quan})

                    print("미체결종목:%s 수량:%s" %(sCode, not_chegual_quan))

                if chegual_quantity >0:
                    if sCode in self.not_account_stock_dict.keys():
                        notQ = self.not_account_stock_dict[sCode]['미체결수량']
                        if chegual_quantity == int(notQ):
                            del self.not_account_stock_dict[sCode]
                        else:
                            namergeQ = not_chegual_quan - int(notQ)
                            namergeQ = int(namergeQ)
                            self.not_account_stock_dict[sCode].update({"미체결수량":namergeQ})


            ##### 새로운 주문이면 주문번호 할당
            # if sCode not in self.online_jango_dict.keys():
            #     self.online_jango_dict.update({sCode: {}})
            #
            # self.online_jango_dict[sCode].update({"주문번호": order_number})
            # self.account_stock_dict[sCode].update({"종목명": stock_name})
            # self.account_stock_dict[sCode].update({"주문상태": order_status})
            # self.account_stock_dict[sCode].update({"주문수량": order_quan})
            # self.account_stock_dict[sCode].update({"주문가격": order_price})
            # self.online_jango_dict[sCode].update({"미체결수량": not_chegual_quan})
            # self.online_jango_dict[sCode].update({"원주문번호": original_order_number})
            # self.online_jango_dict[sCode].update({"주문구분": order_gubun})
            # self.not_account_stock_dict[order_number].update({"매도수구분": meme_gubun})
            # self.account_stock_dict[sCode].update({"주문/체결시간": chegual_time_str})
            # self.online_jango_dict[sCode].update({"매입단가": chegual_price})
            # self.online_jango_dict[sCode].update({"주문가능수량": chegual_quantity})
            # self.account_stock_dict[sCode].update({"현재가": current_price})
            # self.account_stock_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            # self.account_stock_dict[sCode].update({"(최우선)매수 호가": first_buy_price})

            # print(rowsCode)
            # print(sCode)
            # print(self.online_jango_dict[sCode])

            # if order_gubun =="매도":
            #     self.portfolio_stock_dict[sCode].update({"매도가": chegual_price})




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
            if like_quan == '':
                like_quan = 0
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
            self.online_jango_dict[sCode].update({"매도가격0": 0})
            self.online_jango_dict[sCode].update({"매도가격1": 0})
            self.online_jango_dict[sCode].update({"매도가격2": 0})
            self.online_jango_dict[sCode].update({"매도가격3": 0})
            self.online_jango_dict[sCode].update({"매도가격4": 0})
            self.online_jango_dict[sCode].update({"매도가격5": 0})
            self.online_jango_dict[sCode].update({"매도가격6": 0})
            self.online_jango_dict[sCode].update({"매도가격7": 0})
            self.online_jango_dict[sCode].update({"매도가격8": 0})
            self.online_jango_dict[sCode].update({"매도가격9": 0})
            self.online_jango_dict[sCode].update({"매도가격10": 0})
            self.online_jango_dict[sCode].update({"매도가격11": 0})
            self.online_jango_dict[sCode].update({"매도가격12": 0})
            self.online_jango_dict[sCode].update({"매도가격13": 0})
            self.online_jango_dict[sCode].update({"매도가격14": 0})
            self.online_jango_dict[sCode].update({"매도가격15": 0})
            self.online_jango_dict[sCode].update({"매도가격16": 0})
            self.online_jango_dict[sCode].update({"매도가격17": 0})
            self.online_jango_dict[sCode].update({"매도가격18": 0})
            self.online_jango_dict[sCode].update({"매도가격19": 0})

            
            # if sCode in self.portfolio_stock_dict.keys():
            #     mesuSn = self.portfolio_stock_dict[sCode]['매수분봉']
            #
            #     self.online_jango_dict[sCode].update({"매수분봉":mesuSn})
            # print(stock_quan)
            # print(self.online_jango_dict[sCode])
            if stock_quan == 0:
                if sCode in self.online_jango_dict.keys():
                   del self.online_jango_dict[sCode]

                if sCode in self.portfolio_stock_dict.keys():
                    #print("포트폴리오삭제 %s" % self.portfolio_stock_dict[sCode]['종목명'])
                    del self.portfolio_stock_dict[sCode]
                    self.dynamicCall("SetRealRemove(QString, QString)", "ALL" ,sCode)
                   # self.portfolio_stock_dict[sCode].update({"매수가능여부":"Y"})
                   # self.portfolio_stock_dict[sCode].update({"익절횟수": 0})
                   # self.portfolio_stock_dict[sCode].update({"손절횟수": 0})





                # if sCode in self.portfolio_stock_dict.keys():
                #    del self.portfolio_stock_dict[sCode]

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
















