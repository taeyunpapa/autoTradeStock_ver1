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
        base = self.currentDay + "090000"
        self.baseTime = datetime.datetime.strptime(base, "%Y%m%d%H%M%S")
        self.startTime1 = None

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
        self.real_event_slot()

        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info()  # 예수금 가져오기
        self.not_concluded_account()  # 미체결 요청
        self.getItemList()  # 종목코드가져오기
        self.read_code()  # 저장된 종목 파일 불러오기
        self.detail_account_mystock()  # 계좌평가 잔고내역 가져오기

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
                    self.portfolio_stock_dict.update({tempStockCode: {"종목명": itemName,"결과갯수":0,"결과":"E","재결과":"",
                        "주문용스크린번호": self.screen_meme_stock, "익절횟수": 0,"처음":"Y", "순번":0,"분봉갯수":0,"매수분봉":0,
                        "전시가":0,"전종가":0,"맥스고가":0,"매수조건":"", "매수가능여부":"Y","매도가":0,"손절횟수":0
                        , "매수포인트":"", "e케이스":"Y"}})
                    print("매매종목추가:%s" % self.portfolio_stock_dict[tempStockCode]['종목명'])
                    meme_code = tempStockCode
                    # 일봉데이터 받아오기
                    self.day_kiwoom_db(code=tempStockCode)

                break

        for code in self.portfolio_stock_dict.keys():
            screen_num = self.portfolio_stock_dict[code]['주문용스크린번호']
            fids = self.realType.REALTYPE['주식체결']['체결시간']

            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1")
            print("실시간등록코드 : %s, 스크린번호: %s, fid번호: %s" % (code, screen_num, fids))

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
        self.account_num = account_list.split(';')[0]
        print("보유계좌번호 %s" % self.account_num)

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

        QTest.qWait(300)  # 3.6초 딜레이(과도한 조회로 오류방지)

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

        elif sRQName == "주식일봉차트조회":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            print("일봉데이터 요청 %s" % code)

            # cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            cnt = 5
            print("데이터일수 %s" % cnt)

            # 한번조회하면 600일치 일봉데이터를 받을 수 있다.
            self.calcul_data.clear()
            sum = 0
            for i in range(cnt):
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
            one_before = int(self.calcul_data[1][1])
            two_before = int(self.calcul_data[2][1])
            three_before = int(self.calcul_data[3][1])
            four_before = int(self.calcul_data[4][1])

            sum = one_before + two_before + three_before + four_before

            print("4일합계:%s" % sum)

            if code not in self.price_sum.keys():
                self.price_sum.update({code: {}})

            self.price_sum[code].update({'합계': sum})
            print(self.price_sum)

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

            elif value == "2":
                print("장 종료, 동시호가로 넘어감")
                self.market_open_f = "N"
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
            d = float(c)

            e = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매도호가'])
            e = abs(int(e))

            f = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매수호가'])
            f = abs(int(f))

            g = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['거래량'])
            g = abs(int(g))

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

            #체결시간
            meme = self.currentDay + a
            memeTime = datetime.datetime.strptime(meme, "%Y%m%d%H%M%S")

            timeline = range(0, 130)
            
            for i in timeline:
                startTime = self.baseTime + datetime.timedelta(minutes=(3 * i))
                endTime = self.baseTime + datetime.timedelta(minutes=(3 * (i + 1)))


                if memeTime >= startTime and endTime > memeTime:
                    self.startTime1 = startTime + datetime.timedelta(minutes=1)

                    self.bunbongNmSiga = str(i) + "분봉시가"
                    self.bunbongNmJongga = str(i) + "분봉종가"
                    self.bunbongNmGoga = str(i) + "분봉고가"
                    self.bunbongNmJuga = str(i) + "분봉저가"


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
                            if i>int(self.portfolio_stock_dict[sCode]['매수분봉']):
                                print("미체결취소:%s" % sCode)
                                order_success = self.dynamicCall(
                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                    ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 3,
                                     sCode, notChegualCnt, b, self.realType.SENDTYPE['거래구분']['지정가'], jumunNum])

                                if order_success == 0:
                                    print("주문취소:%s" % sCode)
                    

                    if self.portfolio_stock_dict[sCode]['처음'] == "Y":

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmSiga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmJongga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmGoga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmJuga: b})

                        self.portfolio_stock_dict[sCode].update({"처음":"N"})

                        self.portfolio_stock_dict[sCode].update({"순번": i})

                    elif self.portfolio_stock_dict[sCode]['순번'] == i:

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmJongga: b})

                        if b > self.portfolio_stock_dict[sCode][self.bunbongNmGoga]:
                            self.portfolio_stock_dict[sCode].update({self.bunbongNmGoga: b})

                        if self.portfolio_stock_dict[sCode][self.bunbongNmJuga] > b:
                            self.portfolio_stock_dict[sCode].update({self.bunbongNmJuga: b})

                    else:
                        self.portfolio_stock_dict[sCode].update({"순번":i})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmSiga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmJongga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmGoga: b})

                        self.portfolio_stock_dict[sCode].update({self.bunbongNmJuga: b})

                        cnt = self.portfolio_stock_dict[sCode]["분봉갯수"]

                        self.portfolio_stock_dict[sCode].update({"분봉갯수":cnt+1})
                    break


            ############################# 매수 #########################################
            
            if self.portfolio_stock_dict[sCode]['분봉갯수'] >3 and self.portfolio_stock_dict[sCode]['매수가능여부']=="Y":

                # print(self.portfolio_stock_dict[sCode])

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
                maxGoga = self.portfolio_stock_dict[sCode]['맥스고가']


                preunitsiga = self.portfolio_stock_dict[sCode]['전시가']
                preunitjonga = self.portfolio_stock_dict[sCode]['전종가']

                if bongcnt > resultcnt:
                    jogun = range(startSn, endSn)
                    for z in jogun:
                        unitbunbongNmSiga = str(z) + "분봉시가"
                        unitbunbongNmJongga = str(z) + "분봉종가"
                        unitbunbongNmGoga = str(z) + "분봉고가"

                        if unitbunbongNmSiga not in self.portfolio_stock_dict[sCode]:
                            continue

                        unitsiga = self.portfolio_stock_dict[sCode][unitbunbongNmSiga]
                        unitjonga = self.portfolio_stock_dict[sCode][unitbunbongNmJongga]
                        # unitgoga = self.portfolio_stock_dict[sCode][unitbunbongNmGoga]
                        unitgoga = 0
                        if unitsiga > unitjonga:
                            unitgoga = unitsiga
                        else:
                            unitgoga = unitjonga

                        if unitgoga > maxGoga:
                            maxGoga = unitgoga
                            self.portfolio_stock_dict[sCode].update({"맥스고가":maxGoga})

                        if z == 0:
                            if unitsiga == j and unitjonga >= j:
                                if unitjonga >= unitsiga:
                                    result = "A"
                                else:
                                    result = "B"
                            elif j == unitsiga and j > unitjonga:
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
                                if unitsiga > j and unitjonga > j:
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


                                                # rowgoGap = unitsiga - preunitsiga
                                                # rowjuGap = unitjonga - preunitjonga
                                                #
                                                # goGap = abs(rowgoGap)
                                                # juGap = abs(rowjuGap)
                                                #
                                                # if rowgoGap > 0:
                                                #
                                                #     if goGap > juGap:
                                                #         result = result + "A"
                                                #     elif juGap > goGap:
                                                #         result = result + "B"
                                                #     else:
                                                #         result = result + "E"
                                                # elif rowgoGap < 0:
                                                #
                                                #     if juGap > goGap:
                                                #         result = result + "A"
                                                #     elif goGap > juGap:
                                                #         result = result + "B"
                                                #     else:
                                                #         result = result + "E"
                                                # else:
                                                #     if rowjuGap > 0:
                                                #         result = result + "A"
                                                #     elif rowjuGap < 0:
                                                #         result = result + "B"
                                                #     else:
                                                #         result = result + "E"

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

                                                # rowgoGap = unitjonga - preunitsiga
                                                # rowjuGap = unitsiga - preunitjonga
                                                #
                                                # goGap = abs(rowgoGap)
                                                # juGap = abs(rowjuGap)
                                                #
                                                # if rowgoGap > 0:
                                                #
                                                #     if goGap > juGap:
                                                #         result = result + "A"
                                                #     elif juGap > goGap:
                                                #         result = result + "B"
                                                #     else:
                                                #         result = result + "E"
                                                #
                                                # elif rowgoGap < 0:
                                                #
                                                #     if juGap > goGap:
                                                #         result = result + "A"
                                                #     elif goGap > juGap:
                                                #         result = result + "B"
                                                #     else:
                                                #         result = result + "E"
                                                # else:
                                                #     if rowjuGap > 0:
                                                #         result = result + "A"
                                                #     elif rowjuGap < 0:
                                                #         result = result + "B"
                                                #     else:
                                                #         result = result + "E"

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
                                                # if unitjonga > preunitjonga:
                                                #     result = result + "a"
                                                # else:
                                                #     result = result + "b"

                                                # rowgoGap = unitsiga - preunitjonga
                                                # rowjuGap = unitjonga - preunitsiga
                                                #
                                                # goGap = abs(rowgoGap)
                                                # juGap = abs(rowjuGap)
                                                #
                                                # if rowgoGap > 0:
                                                #
                                                #     if goGap > juGap:
                                                #         result = result + "A"
                                                #     elif juGap > goGap:
                                                #         result = result + "B"
                                                #     else:
                                                #         result = result + "E"
                                                # elif rowgoGap < 0:
                                                #
                                                #     if juGap > goGap:
                                                #         result = result + "A"
                                                #     elif goGap > juGap:
                                                #         result = result + "B"
                                                #     else:
                                                #         result = result + "E"
                                                # else:
                                                #     if rowjuGap > 0:
                                                #         result = result + "A"
                                                #     elif rowjuGap < 0:
                                                #         result = result + "B"
                                                #     else:
                                                #         result = result + "E"

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
                                                # if unitjonga > preunitjonga:
                                                #     result = result + "a"
                                                # else:
                                                #     result = result + "b"

                                                # rowgoGap = unitjonga - preunitjonga
                                                # rowjuGap = unitsiga - preunitsiga
                                                #
                                                # goGap = abs(rowgoGap)
                                                # juGap = abs(rowjuGap)
                                                #
                                                # if rowgoGap > 0:
                                                #
                                                #     if goGap > juGap:
                                                #         result = result + "A"
                                                #     elif juGap > goGap:
                                                #         result = result + "B"
                                                #     else:
                                                #         result = result + "E"
                                                # elif rowgoGap < 0:
                                                #
                                                #     if juGap > goGap:
                                                #         result = result + "A"
                                                #     elif goGap > juGap:
                                                #         result = result + "B"
                                                #     else:
                                                #         result = result + "E"
                                                # else:
                                                #     if rowjuGap > 0:
                                                #         result = result + "A"
                                                #     elif rowjuGap < 0:
                                                #         result = result + "B"
                                                #     else:
                                                #         result = result + "E"

                                elif j > unitsiga and j > unitjonga:

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

                                                # rowgoGap = unitsiga - preunitsiga
                                                # rowjuGap = unitjonga - preunitjonga
                                                #
                                                # goGap = abs(rowgoGap)
                                                # juGap = abs(rowjuGap)
                                                #
                                                # if rowgoGap > 0:
                                                #
                                                #     if goGap > juGap:
                                                #         result = result + "D"
                                                #     elif juGap > goGap:
                                                #         result = result + "C"
                                                #     else:
                                                #         result = result + "E"
                                                # elif rowgoGap < 0:
                                                #
                                                #     if juGap > goGap:
                                                #         result = result + "D"
                                                #     elif goGap > juGap:
                                                #         result = result + "C"
                                                #     else:
                                                #         result = result + "E"
                                                # else:
                                                #     if rowjuGap > 0:
                                                #         result = result + "D"
                                                #     elif rowjuGap < 0:
                                                #         result = result + "C"
                                                #     else:
                                                #         result = result + "E"

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

                                                # rowgoGap = unitjonga - preunitsiga
                                                # rowjuGap = unitsiga - preunitjonga
                                                #
                                                # goGap = abs(rowgoGap)
                                                # juGap = abs(rowjuGap)
                                                #
                                                # if rowgoGap > 0:
                                                #
                                                #     if goGap > juGap:
                                                #         result = result + "D"
                                                #     elif juGap > goGap:
                                                #         result = result + "C"
                                                #     else:
                                                #         result = result + "E"
                                                # elif rowgoGap < 0:
                                                #
                                                #     if juGap > goGap:
                                                #         result = result + "D"
                                                #     elif goGap > juGap:
                                                #         result = result + "C"
                                                #     else:
                                                #         result = result + "E"
                                                # else:
                                                #     if rowjuGap > 0:
                                                #         result = result + "D"
                                                #     elif rowjuGap < 0:
                                                #         result = result + "C"
                                                #     else:
                                                #         result = result + "E"


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

                                                # if unitjonga > preunitjonga:
                                                #     result = result + "d"
                                                # else:
                                                #     result = result + "c"

                                                # rowgoGap = unitsiga - preunitjonga
                                                # rowjuGap = unitjonga - preunitsiga
                                                #
                                                # goGap = abs(rowgoGap)
                                                # juGap = abs(rowjuGap)
                                                #
                                                # if rowgoGap > 0:
                                                #
                                                #     if goGap > juGap:
                                                #         result = result + "D"
                                                #     elif juGap > goGap:
                                                #         result = result + "C"
                                                #     else:
                                                #         result = result + "E"
                                                # elif rowgoGap < 0:
                                                #
                                                #     if juGap > goGap:
                                                #         result = result + "D"
                                                #     elif goGap > juGap:
                                                #         result = result + "C"
                                                #     else:
                                                #         result = result + "E"
                                                # else:
                                                #     if rowjuGap > 0:
                                                #         result = result + "D"
                                                #     elif rowjuGap < 0:
                                                #         result = result + "C"
                                                #     else:
                                                #         result = result + "E"

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
                                                # if unitjonga > preunitjonga:
                                                #     result = result + "d"
                                                # else:
                                                #     result = result + "c"

                                                # rowgoGap = unitjonga - preunitjonga
                                                # rowjuGap = unitsiga - preunitsiga
                                                #
                                                # goGap = abs(rowgoGap)
                                                # juGap = abs(rowjuGap)
                                                #
                                                # if rowgoGap > 0:
                                                #
                                                #     if goGap > juGap:
                                                #         result = result + "D"
                                                #     elif juGap > goGap:
                                                #         result = result + "C"
                                                #     else:
                                                #         result = result + "E"
                                                # elif rowgoGap < 0:
                                                #
                                                #     if juGap > goGap:
                                                #         result = result + "D"
                                                #     elif goGap > juGap:
                                                #         result = result + "C"
                                                #     else:
                                                #         result = result + "E"
                                                # else:
                                                #     if rowjuGap > 0:
                                                #         result = result + "D"
                                                #     elif rowjuGap < 0:
                                                #         result = result + "C"
                                                #     else:
                                                #         result = result + "E"
                                else:

                                    if preunitsiga > j and preunitjonga > j:

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

                                    elif j > preunitsiga and j > preunitjonga:

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
                        self.portfolio_stock_dict[sCode].update({"전시가":unitsiga})
                        self.portfolio_stock_dict[sCode].update({"전종가": unitjonga})

                    self.portfolio_stock_dict[sCode].update({'결과':result})
                    abc=len(self.portfolio_stock_dict[sCode]['결과'])

                    self.portfolio_stock_dict[sCode].update({'결과갯수':abc})

                    Arow = "AbA"
                    reArow = "AA"
                    Brow = "BaB"
                    reBrow = "BB"
                    Brow22 = "Bab"
                    reBrow22 = "B"
                    Crow = "CdC"
                    reCrow = "CC"
                    Crow22 = "Cdc"
                    reCrow22 = "C"

                    Drow = "DcD"
                    reDrow = "DD"

                    Brow0 = "bBB"
                    reBrow0 = "BBB"
                    Brow01 = "BbB"
                    reBrow01 = "BBB"
                    Brow02 = "BBb"
                    reBrow02 = "BBB"

                    Crow0 = "cCC"
                    reCrow0 = "CCC"
                    Crow01 = "CcC"
                    reCrow01 = "CCC"
                    Crow02 = "CCc"
                    reCrow02 = "CCC"

                    Arow1 = "AEA"
                    reArow1 = "AA"
                    Brow1 = "BEB"
                    reBrow1 = "BB"
                    Crow1 = "CEC"
                    reCrow1 = "CC"
                    Drow1 = "DED"
                    reDrow1 = "DD"

                    Arow2 = "AAEbAA"
                    reArow2 = "AAAA"
                    Arow3 = "AAbEAA"
                    reArow3 = "AAAA"
                    Brow2 = "BBaEBB"
                    reBrow2 = "BBBB"
                    Brow3 = "BBEaBB"
                    reBrow3 = "BBBB"
                    Crow2 = "CCdECC"
                    reCrow2 = "CCCC"
                    Crow3 = "CCEdCC"
                    reCrow3 = "CCCC"
                    Drow2 = "DDcEDD"
                    reDrow2 = "DDDD"
                    Drow3 = "DDEcDD"
                    reDrow3 = "DDDD"

                    Arow21 = "AEaA"
                    reArow21 = "AAA"
                    Arow31 = "AaEA"
                    reArow31 = "AAA"
                    Brow21 = "BbEB"
                    reBrow21 = "BBB"
                    Brow31 = "BEbB"
                    reBrow31 = "BBB"
                    Crow21 = "CcEC"
                    reCrow21 = "CCC"
                    Crow31 = "CEcC"
                    reCrow31 = "CCC"
                    Drow21 = "DdED"
                    reDrow21 = "DDD"
                    Drow31 = "DEdD"
                    reDrow31 = "DDD"

                    Erow1 = "EEAEE"
                    reErow1 = "EEEEE"
                    Erow2 = "EEBEE"
                    reErow2 = "EEEEE"
                    Erow3 = "EECEE"
                    reErow3 = "EEEEE"
                    Erow4 = "EEDEE"
                    reErow4 = "EEEEE"

                    Erow11 = "BEEE"
                    reErow11 = "EEEE"
                    Erow21 = "CEEE"
                    reErow21 = "EEEE"
                    Erow31 = "DEEE"
                    reErow31 = "EEEE"

                    Frow1 = "FAA"
                    reFrow1 = "AAA"
                    Frow2 = "BBF"
                    reFrow2 = "BBB"
                    Frow3 = "FCC"
                    reFrow3 = "CCC"
                    Frow4 = "DDF"
                    reFrow4 = "DDD"
                    Frow5 = "FEE"
                    reFrow5 = "EEE"
                    Frow6 = "EEF"
                    reFrow6 = "EEE"

                    Erow41 = "BEB"
                    reErow41 = "BB"
                    Erow51 = "CEC"
                    reErow51 = "CC"
                    Erow61 = "DED"
                    reErow61 = "DD"

                    Brow41 = "BBBC"
                    reBrow41 = "BBBB"
                    Crow41 = "BCCC"
                    reCrow41 = "BBBB"
                    Brow51 = "BBCC"
                    reBrow51 = "BBBB"

                    #print("시간:%s , result:%s" % (meme,result))
                    for m in range(0, 5):
                        result = result.replace(Arow, reArow).replace(Brow, reBrow).replace(Crow, reCrow) \
                        .replace(Drow, reDrow).replace(Erow1, reErow1).replace(Erow2, reErow2) \
                        .replace(Erow3, reErow3).replace(Erow4, reErow4).replace(Arow1, reArow1) \
                        .replace(Brow1, reBrow1).replace(Crow1, reCrow1).replace(Drow1, reDrow1) \
                        .replace(Arow2, reArow2).replace(Arow3, reArow3).replace(Brow2, reBrow2) \
                        .replace(Brow3, reBrow3).replace(Crow2, reCrow2).replace(Crow3, reCrow3) \
                        .replace(Drow2, reDrow2).replace(Drow3, reDrow3).replace(Frow1, reFrow1) \
                        .replace(Frow2, reFrow2).replace(Frow3, reFrow3).replace(Frow4, reFrow4) \
                        .replace(Frow5, reFrow5).replace(Frow6, reFrow6).replace(Brow0, reBrow0) \
                        .replace(Crow0, reCrow0).replace(Brow01, reBrow01).replace(Brow02, reBrow02) \
                        .replace(Crow01, reCrow01).replace(Crow02, reCrow02).replace(Arow21, reArow21) \
                        .replace(Arow31, reArow31).replace(Brow21, reBrow21).replace(Brow31, reBrow31) \
                        .replace(Crow21, reCrow21).replace(Crow31, reCrow31).replace(Drow21, reDrow21) \
                        .replace(Drow31, reDrow31).replace(Erow11, reErow11).replace(Erow21, reErow21) \
                        .replace(Erow31, reErow31).replace(Erow41, reErow41).replace(Erow51, reErow51) \
                        .replace(Erow61, reErow61).replace(Brow41, reBrow41).replace(Crow41, reCrow41) \
                        .replace(Brow51, reBrow51).replace(Brow22, reBrow22).replace(Crow22, reCrow22)
                    # print("re_result:%s" % result)

                    result = "[" + result + "]"
                    finalResult = ""
                    preChar = None
                    jogun_cnt = 0
                    for n in result:

                        if n == preChar:
                            jogun_cnt += 1

                        else:

                            if jogun_cnt > 3:
                                if preChar == "A":
                                    finalResult = finalResult + "A_"
                                elif preChar == "B":
                                    finalResult = finalResult + "B_"
                                elif preChar == "C":
                                    finalResult = finalResult + "C_"
                                elif preChar == "D":
                                    finalResult = finalResult + "D_"
                                elif preChar == "E":
                                    finalResult = finalResult + "E_"

                            jogun_cnt = 1


                        preChar = n

                    # print("finalResult:%s" % finalResult)


                    self.portfolio_stock_dict[sCode].update({"재결과":finalResult})

                    # if finalResultLen>0:
                    #     print("시간:%s , result:%s" % (meme, result))
                    #     print("finalResult:%s" % finalResult)

                case1 = "A_"
                case2 = "B_"
                case3 = "C_"
                case4 = "D_"
                case5 = "E_"

                finalResult2 = self.portfolio_stock_dict[sCode]['재결과']

                finalResultLen = len(finalResult2)

                maxGoga2=self.portfolio_stock_dict[sCode]['맥스고가']

                if self.portfolio_stock_dict[sCode]['매수포인트'] != finalResult2:
                    # print("종목명:%s, 기존매수포인트 동일 제외" % self.portfolio_stock_dict[sCode]['종목명'])

                    if finalResultLen > 3:
                        subfinalResult = finalResult2[finalResultLen - 2: finalResultLen]


                        if subfinalResult == case2 :

                            if b > maxGoga2 and b > self.portfolio_stock_dict[sCode]['매도가']:
                                quantity = int(5000000 / b)
                                print("시간:%s , result:%s" % (meme, result))
                                print("finalResult1:%s" % finalResult2)
                                print("케이스1 코드:%s 시간:%s 가격:%s, 수량:%s, 시가:%s" % (sCode,meme, b, quantity, j))

                                order_success = self.dynamicCall(
                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                    ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                     sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                if order_success == 0:
                                    self.portfolio_stock_dict[sCode].update({"매수가능여부":"N"})
                                    self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                                    self.portfolio_stock_dict[sCode].update({"매수조건": "case1"})
                                    self.portfolio_stock_dict[sCode].update({"매수기준가": maxGoga2})
                                    self.portfolio_stock_dict[sCode].update({"매수포인트":finalResult2})

                                else:
                                    print("매수주문 전달 실패")

                        elif subfinalResult == case3 :
                            preMesuJogun = self.portfolio_stock_dict[sCode]['매수조건']

                            if b > j and b > self.portfolio_stock_dict[sCode]['매도가']:
                                if preMesuJogun == "case2":
                                    if b > maxGoga2:
                                        print("finalResult2:%s" % finalResult2)
                                        quantity = int(5000000 / b)
                                        print("케이스2 코드:%s 시간:%s 가격:%s, 수량:%s, 시가:%s" % (sCode, meme, b, quantity, j))

                                        order_success = self.dynamicCall(
                                            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                            ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                             sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                        if order_success == 0:
                                            self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                            self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                                            self.portfolio_stock_dict[sCode].update({"매수조건": "case2"})
                                            self.portfolio_stock_dict[sCode].update({"매수기준가": maxGoga2})
                                            self.portfolio_stock_dict[sCode].update({"매수포인트": finalResult2})
                                        else:
                                            print("매수주문 전달 실패")
                                else:
                                    print("finalResult2:%s" % finalResult2)
                                    quantity = int(5000000 / b)
                                    print("케이스3 코드:%s 시간:%s 가격:%s, 수량:%s, 시가:%s" % (sCode, meme, b, quantity, j))

                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                        ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                         sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    if order_success == 0:
                                        self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                        self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                                        self.portfolio_stock_dict[sCode].update({"매수조건": "case2"})
                                        self.portfolio_stock_dict[sCode].update({"매수기준가": j})
                                        self.portfolio_stock_dict[sCode].update({"매수포인트": finalResult2})
                                    else:
                                        print("매수주문 전달 실패")

                        elif subfinalResult == case5:
                            if self.portfolio_stock_dict[sCode]['e케이스'] == "Y":
                                if j >= b:
                                    caseERate = abs((j - b) / j * 100)
                                    if caseERate > 1:
                                        self.portfolio_stock_dict[sCode].update({"e케이스매수기준": "down"})
                                    else:
                                        self.portfolio_stock_dict[sCode].update({"e케이스매수기준": "up"})
                                else:
                                    self.portfolio_stock_dict[sCode].update({"e케이스매수기준": "up"})
                                self.portfolio_stock_dict[sCode].update({"e케이스":"N"})

                            if self.portfolio_stock_dict[sCode]['e케이스매수기준'] == "down":
                                if b > j:
                                    print("finalResult2:%s" % finalResult2)
                                    quantity = int(5000000 / b)
                                    print("케이스e-1 코드:%s 시간:%s 가격:%s, 수량:%s, 시가:%s" % (sCode, meme, b, quantity, j))

                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                        ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                         sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    if order_success == 0:
                                        self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                        self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                                        self.portfolio_stock_dict[sCode].update({"매수조건": "case2"})
                                        self.portfolio_stock_dict[sCode].update({"매수기준가": j})
                                        self.portfolio_stock_dict[sCode].update({"매수포인트": finalResult2})
                                    else:
                                        print("매수주문 전달 실패")
                            elif self.portfolio_stock_dict[sCode]['e케이스매수기준'] == "up":
                                if b > maxGoga2:
                                    print("finalResult2:%s" % finalResult2)
                                    quantity = int(5000000 / b)
                                    print("케이스e-2 코드:%s 시간:%s 가격:%s, 수량:%s, 시가:%s" % (sCode, meme, b, quantity, j))

                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                        ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                         sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    if order_success == 0:
                                        self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                        self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                                        self.portfolio_stock_dict[sCode].update({"매수조건": "case2"})
                                        self.portfolio_stock_dict[sCode].update({"매수기준가": maxGoga2})
                                        self.portfolio_stock_dict[sCode].update({"매수포인트": finalResult2})
                                    else:
                                        print("매수주문 전달 실패")
                    elif finalResultLen > 1:

                        subfinalResult = finalResult2[finalResultLen - 2: finalResultLen]

                        if  subfinalResult == case2:

                            if b > maxGoga2 and b > self.portfolio_stock_dict[sCode]['매도가']:
                                quantity = int(5000000 / b)
                                print("시간:%s , result:%s" % (meme, result))
                                print("finalResult1:%s" % finalResult2)
                                print("케이스4 코드:%s 시간:%s 가격:%s, 수량:%s, 시가:%s" % (sCode, meme, b, quantity, j))

                                order_success = self.dynamicCall(
                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                    ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                     sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                if order_success == 0:
                                    self.portfolio_stock_dict[sCode].update({"매수가능여부":"N"})
                                    self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                                    self.portfolio_stock_dict[sCode].update({"매수조건": "case1"})
                                    self.portfolio_stock_dict[sCode].update({"매수기준가": maxGoga2})
                                    self.portfolio_stock_dict[sCode].update({"매수포인트": finalResult2})
                                else:
                                    print("매수주문 전달 실패")

                        elif subfinalResult == case3 :

                            preMesuJogun = self.portfolio_stock_dict[sCode]['매수조건']
                            if preMesuJogun == "case2":
                                if b > maxGoga2 and b > self.portfolio_stock_dict[sCode]['매도가']:
                                    print("finalResult2:%s" % finalResult2)
                                    quantity = int(5000000 / b)
                                    print("케이스5 코드:%s 시간:%s 가격:%s, 수량:%s, 시가:%s" % (sCode, meme, b, quantity, j))

                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                        ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                         sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    if order_success == 0:
                                        self.portfolio_stock_dict[sCode].update({"매수가능여부":"N"})
                                        self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                                        self.portfolio_stock_dict[sCode].update({"매수조건": "case2"})
                                        self.portfolio_stock_dict[sCode].update({"매수기준가": maxGoga2})
                                        self.portfolio_stock_dict[sCode].update({"매수포인트": finalResult2})
                                    else:
                                        print("매수주문 전달 실패")

                            else:
                                if b > j and b > self.portfolio_stock_dict[sCode]['매도가']:
                                    print("finalResult2:%s" % finalResult2)
                                    quantity = int(5000000 / b)
                                    print("케이스6 코드:%s 시간:%s 가격:%s, 수량:%s, 시가:%s" % (sCode, meme, b, quantity, j))

                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                        ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                         sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    if order_success == 0:
                                        self.portfolio_stock_dict[sCode].update({"매수가능여부":"N"})
                                        self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                                        self.portfolio_stock_dict[sCode].update({"매수조건": "case2"})
                                        self.portfolio_stock_dict[sCode].update({"매수기준가": j})
                                        self.portfolio_stock_dict[sCode].update({"매수포인트": finalResult2})
                                    else:
                                        print("매수주문 전달 실패")

                        elif subfinalResult == case5:
                            if self.portfolio_stock_dict[sCode]['e케이스'] == "Y":
                                if j >= b:
                                    caseERate = abs((j - b) / j * 100)
                                    if caseERate > 1:
                                        self.portfolio_stock_dict[sCode].update({"e케이스매수기준": "down"})
                                    else:
                                        self.portfolio_stock_dict[sCode].update({"e케이스매수기준": "up"})
                                else:
                                    self.portfolio_stock_dict[sCode].update({"e케이스매수기준": "up"})
                                self.portfolio_stock_dict[sCode].update({"e케이스":"N"})

                            if self.portfolio_stock_dict[sCode]['e케이스매수기준'] == "down":
                                if b > j:
                                    print("finalResult2:%s" % finalResult2)
                                    quantity = int(5000000 / b)
                                    print("케이스e-3 코드:%s 시간:%s 가격:%s, 수량:%s, 시가:%s" % (sCode, meme, b, quantity, j))

                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                        ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                         sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    if order_success == 0:
                                        self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                        self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                                        self.portfolio_stock_dict[sCode].update({"매수조건": "case2"})
                                        self.portfolio_stock_dict[sCode].update({"매수기준가": j})
                                        self.portfolio_stock_dict[sCode].update({"매수포인트": finalResult2})
                                    else:
                                        print("매수주문 전달 실패")
                            elif self.portfolio_stock_dict[sCode]['e케이스매수기준'] == "up":
                                if b > maxGoga2:
                                    print("finalResult2:%s" % finalResult2)
                                    quantity = int(5000000 / b)
                                    print("케이스e-4 코드:%s 시간:%s 가격:%s, 수량:%s, 시가:%s" % (sCode, meme, b, quantity, j))

                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                        ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                         sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    if order_success == 0:
                                        self.portfolio_stock_dict[sCode].update({"매수가능여부": "N"})
                                        self.portfolio_stock_dict[sCode].update({"매수분봉": endSn})
                                        self.portfolio_stock_dict[sCode].update({"매수조건": "case2"})
                                        self.portfolio_stock_dict[sCode].update({"매수기준가": maxGoga2})
                                        self.portfolio_stock_dict[sCode].update({"매수포인트": finalResult2})
                                    else:
                                        print("매수주문 전달 실패")

            ############################# 매도 #########################################

            if sCode in self.online_jango_dict.keys():

                medoSn = self.portfolio_stock_dict[sCode]['순번']
                mesubunbong = self.portfolio_stock_dict[sCode]['매수분봉']

                asd = self.online_jango_dict[sCode]
                meib = int(asd['매입단가'])
                meme_rate = (b - meib) / meib * 100  # 등락률

                mesuGijunga = self.portfolio_stock_dict[sCode]['매수기준가']
                tempstr = str(mesubunbong) + "분봉저가"
                sonjulGijunga = self.portfolio_stock_dict[sCode][tempstr]

                if medoSn > mesubunbong:

                    # print("매입단가:%s"%meib)
                    #### 익절####

                    profit = 0

                    # print("종목:%s 등락률:%s" % (self.online_jango_dict[sCode]['종목명'], meme_rate))

                    medojogun = range(mesubunbong, medoSn)

                    madojanunManjok = "N"
                    madojanunManjok2 = "N"
                    ikjuljojunmanjok = "N"

                    for g in medojogun:
                        medounitbunbongNmGoga = str(g) + "분봉고가"
                        medounitbunbongNmSiga = str(g) + "분봉시가"
                        medounitbunbongNmJongga = str(g) + "분봉종가"

                        medounitgoga = self.portfolio_stock_dict[sCode][medounitbunbongNmGoga]
                        medounitsiga = self.portfolio_stock_dict[sCode][medounitbunbongNmSiga]
                        medoUnitJonga = self.portfolio_stock_dict[sCode][medounitbunbongNmJongga]

                        jonga_meme_rate = ((medoUnitJonga-meib) / meib) * 100

                        # if 1.0 > jonga_meme_rate:
                        #     ikjuljojunmanjok = "Y"

                        if mesuGijunga > medoUnitJonga or sonjulGijunga > medoUnitJonga:
                            madojanunManjok = "Y"

                        if g == mesubunbong:
                            if mesuGijunga >= medoUnitJonga:
                                if medounitgoga-medoUnitJonga>medoUnitJonga-medounitsiga:
                                    madojanunManjok2="Y"

                    if asd['주문가능수량'] > 0 and meme_rate >= 8:
                        if self.portfolio_stock_dict[sCode]['익절횟수'] == 3:
                            medo_quan = int(asd['주문가능수량'])
                            print(medo_quan)
                            profit = int(b * medo_quan * meme_rate / 100)
                            print("익절5 매도:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))
                            order_success = self.dynamicCall(
                                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                   sCode, medo_quan, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                            if order_success == 0:
                                self.portfolio_stock_dict[sCode].update({"익절횟수": 3})
                                self.online_jango_dict[sCode].update({"매도가격0": b})
                                self.portfolio_stock_dict[sCode].update({"매도가": b})
                                print("매도주문 전달 성공")

                            else:
                                print("매도주문 전달 실패")

                    elif asd['주문가능수량'] > 0 and meme_rate >= 5:
                        if self.portfolio_stock_dict[sCode]['익절횟수'] == 2:
                            medo_quan = int(asd['주문가능수량'] / 2)
                            print(medo_quan)
                            profit = int(b * medo_quan * meme_rate / 100)
                            print("익절0 매도:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))
                            order_success = self.dynamicCall(
                                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                   sCode, medo_quan, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                            if order_success == 0:
                                self.portfolio_stock_dict[sCode].update({"익절횟수": 3})
                                self.online_jango_dict[sCode].update({"매도가격1": b})
                                self.portfolio_stock_dict[sCode].update({"매도가": b})
                                print("매도주문 전달 성공")

                            else:
                                print("매도주문 전달 실패")
                    elif asd['주문가능수량'] > 0 and 2.0 > jonga_meme_rate and self.online_jango_dict[sCode]['매도가격1'] > 0:

                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        print("익절1 매도:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))

                        order_success = self.dynamicCall(
                            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                            , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                               sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                        if order_success == 0:
                            self.portfolio_stock_dict[sCode].update({"매도가": b})
                            print("매도주문 전달 성공")
                        else:
                            print("매도주문 전달 실패")

                    elif asd['주문가능수량'] > 0 and meme_rate > 2:

                        if self.portfolio_stock_dict[sCode]['익절횟수'] == 1:
                            medo_quan = int(asd['주문가능수량'] / 3)
                            print(medo_quan)
                            profit = int(b * medo_quan * meme_rate / 100)
                            print("익절2 매도:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))
                            order_success = self.dynamicCall(
                                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                   sCode, medo_quan, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                            if order_success == 0:
                                self.portfolio_stock_dict[sCode].update({"익절횟수": 2})
                                self.online_jango_dict[sCode].update({"매도가격2": b})
                                self.portfolio_stock_dict[sCode].update({"매도가": b})
                                print("매도주문 전달 성공")

                            else:
                                print("매도주문 전달 실패")

                    elif asd['주문가능수량'] > 0 and 0.5>jonga_meme_rate and self.online_jango_dict[sCode]['매도가격2'] > 0:

                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        print("익절3 매도:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))

                        order_success = self.dynamicCall(
                            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                            , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                               sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                        if order_success == 0:
                            print("매도주문 전달 성공")
                            self.portfolio_stock_dict[sCode].update({"매도가": b})

                        else:
                            print("매도주문 전달 실패")

                    elif asd['주문가능수량'] > 0 and meme_rate > 1.2:

                        if self.portfolio_stock_dict[sCode]['익절횟수'] == 0:
                            medo_quan = int(asd['주문가능수량'] / 4)
                            print(medo_quan)
                            profit = int(b * medo_quan * meme_rate / 100)
                            print("익절4 매도:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))
                            order_success = self.dynamicCall(
                                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                   sCode, medo_quan, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                            if order_success == 0:
                                self.portfolio_stock_dict[sCode].update({"익절횟수": 1})
                                self.online_jango_dict[sCode].update({"매도가격4": b})
                                self.portfolio_stock_dict[sCode].update({"매도가": b})
                                print("매도주문 전달 성공")

                            else:
                                print("매도주문 전달 실패")


                    elif asd['주문가능수량'] > 0 and 0.2>jonga_meme_rate and self.online_jango_dict[sCode]['매도가격4'] > 0:

                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        print("익절5 매도:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))

                        order_success = self.dynamicCall(
                            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                            , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                               sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                        if order_success == 0:
                            print("매도주문 전달 성공")
                            self.portfolio_stock_dict[sCode].update({"매도가": b})

                        else:
                            print("매도주문 전달 실패")

                    elif asd['주문가능수량'] > 0 and meme_rate > 0.5:

                        profit = int(b * asd['주문가능수량'] * meme_rate / 100)

                        self.online_jango_dict[sCode].update({"매도가격3": b})

                        print("0.5프로이상 홀딩:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))


                    # elif asd['주문가능수량'] > 0 and 0.25 >= meme_rate and self.online_jango_dict[sCode]['매도가격3'] > 0:
                    #
                    #     profit = int(b * asd['주문가능수량'] * meme_rate / 100)
                    #
                    #     print("익절5 매도:%s, 수익률:%s, 수익금:%s, 시간:%s" % (sCode, meme_rate, profit, meme))
                    #
                    #     order_success = self.dynamicCall(
                    #         "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                    #         , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                    #            sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    #     if order_success == 0:
                    #         print("매도주문 전달 성공")
                    #
                    #     else:
                    #         print("매도주문 전달 실패")


                    #### 손절 ####
                    else:

                        bunsiga = self.portfolio_stock_dict[sCode][self.bunbongNmSiga]
                        bunjongga = self.portfolio_stock_dict[sCode][self.bunbongNmJongga]
                        mesuJogun = self.portfolio_stock_dict[sCode]['매수조건']

                        sonjulCnt = self.portfolio_stock_dict[sCode]['손절횟수']


                        if madojanunManjok == "Y" or madojanunManjok2 =="Y":
                            if mesuGijunga>sonjulGijunga:
                                if mesuGijunga>b and bunsiga > bunjongga and sonjulCnt ==0:

                                    sonjulQuan1 = int(asd['주문가능수량'])/3
                                    sonjulAmount = (meib - b) * sonjulQuan1
                                    print("손절1 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                                    print("매수기준가:%s 손절기준가:%s" %(mesuGijunga, sonjulGijunga))

                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                        , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                           sCode, sonjulQuan1, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    if order_success == 0:

                                        print("매도주문 전달 성공")
                                        self.portfolio_stock_dict[sCode].update({"손절횟수":1})
                                    else:
                                        print("매도주문 전달 실패")

                                elif sonjulGijunga>b and bunsiga > bunjongga:

                                    sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                                    print("손절2 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                                    print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                        , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                           sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    if order_success == 0:

                                        print("매도주문 전달 성공")
                                    else:
                                        print("매도주문 전달 실패")

                            else:
                                if sonjulGijunga > b and bunsiga > bunjongga and sonjulCnt ==0:
                                    sonjulQuan1 = int(asd['주문가능수량']) / 3
                                    sonjulAmount = (meib - b) * sonjulQuan1
                                    print("손절3 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                                    print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                        , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                           sCode, sonjulQuan1, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    if order_success == 0:
                                        self.portfolio_stock_dict[sCode].update({"손절횟수": 1})
                                        print("매도주문 전달 성공")
                                    else:
                                        print("매도주문 전달 실패")

                                elif mesuGijunga>b and bunsiga > bunjongga:

                                    sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                                    print("손절4 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                                    print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                        , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                           sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    if order_success == 0:

                                        print("매도주문 전달 성공")
                                    else:
                                        print("매도주문 전달 실패")

                        # startSn = self.portfolio_stock_dict[sCode]['순번'] - self.portfolio_stock_dict[sCode][
                        #     '분봉갯수']
                        # endSn = self.portfolio_stock_dict[sCode]['순번']
                        #
                        # jogun = range(mesubunbong, endSn)
                        # madojanunManjok = "N"
                        # madojanunManjok2 = "N"
                        # for z in jogun:
                        #     unitbunbongNmSiga = str(z) + "분봉시가"
                        #     unitbunbongNmJongga = str(z) + "분봉종가"
                        #
                        #     medounitsiga = self.portfolio_stock_dict[sCode][unitbunbongNmSiga]
                        #     medoUnitJonga = self.portfolio_stock_dict[sCode][unitbunbongNmJongga]
                        #
                        #     medoRate = abs(mesuGijunga - medoUnitJonga) / mesuGijunga * 100
                        #
                        #     if medounitsiga > medoUnitJonga and mesuGijunga > medoUnitJonga:
                        #         madojanunManjok = "Y"
                        #
                        # if madojanunManjok == "Y":
                        #     if mesuGijunga > b and bunsiga > bunjongga and memeTime>self.startTime1:
                        #         sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                        #         print("손절1 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                        #
                        #         order_success = self.dynamicCall(
                        #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                        #             , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                        #                sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                        #
                        #         if order_success == 0:
                        #
                        #             print("매도주문 전달 성공")
                        #         else:
                        #             print("매도주문 전달 실패")
                        # else:
                        #     if meme_rate < -1.0 and bunsiga > bunjongga:
                        #
                        #         print("손절2 매도:%s, 주문가:%s, 시간:%s" % (sCode, b, meme))
                        #
                        #         order_success = self.dynamicCall(
                        #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                        #             , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                        #                sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                        #
                        #         if order_success == 0:
                        #
                        #             print("매도주문 전달 성공")
                        #         else:
                        #             print("매도주문 전달 실패")


                elif medoSn == mesubunbong:
                    bunsiga = self.portfolio_stock_dict[sCode][self.bunbongNmSiga]
                    bunjongga = self.portfolio_stock_dict[sCode][self.bunbongNmJongga]

                    mesuGijunga = self.portfolio_stock_dict[sCode]['매수기준가']
                    tempstr = str(mesubunbong)+"분봉저가"
                    sonjulGijunga = self.portfolio_stock_dict[sCode][tempstr]
                    sonjulCnt = self.portfolio_stock_dict[sCode]['손절횟수']

                    sojulRate = ((mesuGijunga - b) / mesuGijunga) * 100

                    if mesuGijunga > sonjulGijunga:
                        if mesuGijunga > b and bunsiga > bunjongga and sonjulCnt==0 and sojulRate >2.0:

                            sonjulQuan1 = int(asd['주문가능수량']) / 2
                            sonjulAmount = (meib - b) * sonjulQuan1
                            print("손절5 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                            print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                            order_success = self.dynamicCall(
                                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                   sCode, sonjulQuan1, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                            if order_success == 0:
                                self.portfolio_stock_dict[sCode].update({"손절횟수": 1})
                                print("매도주문 전달 성공")
                            else:
                                print("매도주문 전달 실패")

                        elif sonjulGijunga > b and bunsiga > bunjongga and sojulRate >2.0:

                            sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                            print("손절6 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                            print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                            order_success = self.dynamicCall(
                                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                   sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                            if order_success == 0:

                                print("매도주문 전달 성공")
                            else:
                                print("매도주문 전달 실패")

                    else:
                        if sonjulGijunga > b and bunsiga > bunjongga and sonjulCnt==0:
                            sonjulQuan1 = int(asd['주문가능수량']) / 2
                            sonjulAmount = (meib - b) * sonjulQuan1
                            print("손절7 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                            print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                            order_success = self.dynamicCall(
                                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                   sCode, sonjulQuan1, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                            if order_success == 0:
                                self.portfolio_stock_dict[sCode].update({"손절횟수": 1})
                                print("매도주문 전달 성공")
                            else:
                                print("매도주문 전달 실패")

                        elif mesuGijunga > b and bunsiga > bunjongga:

                            sonjulAmount = (meib - b) * int(asd['주문가능수량'])
                            print("손절8 매도:%s, 손실금액:%s, 시간:%s" % (sCode, sonjulAmount, meme))
                            print("매수기준가:%s 손절기준가:%s" % (mesuGijunga, sonjulGijunga))
                            order_success = self.dynamicCall(
                                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                   sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                            if order_success == 0:

                                print("매도주문 전달 성공")
                            else:
                                print("매도주문 전달 실패")


                    # bunsiga = self.portfolio_stock_dict[sCode][self.bunbongNmSiga]
                    # bunjongga = self.portfolio_stock_dict[sCode][self.bunbongNmJongga]
                    #
                    # if meme_rate < -1.0 and bunsiga>bunjongga:
                    #
                    #     print("손절3 매도:%s, 주문가:%s, 시간:%s" % (sCode, b, meme))
                    #
                    #     order_success = self.dynamicCall(
                    #         "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                    #         , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                    #            sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])
                    #
                    #     if order_success == 0:
                    #
                    #         print("매도주문 전달 성공")
                    #     else:
                    #         print("매도주문 전달 실패")


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
                not_chegual_quan = int(order_price)

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

            if not_chegual_quan >0:
                if sCode not in self.not_account_stock_dict.keys():
                    self.not_account_stock_dict.update({sCode:{}})

                self.not_account_stock_dict[sCode].update({"주문번호": order_number})
                self.not_account_stock_dict[sCode].update({"미체결수량":not_chegual_quan})

                print("미체결종목:%s 수량:%s" %(sCode, not_chegual_quan))

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
            self.online_jango_dict[sCode].update({"매도가격1": 0})
            self.online_jango_dict[sCode].update({"매도가격2": 0})
            self.online_jango_dict[sCode].update({"매도가격3": 0})
            self.online_jango_dict[sCode].update({"매도가격4": 0})
            
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
                    print("포트폴리오삭제 %s" % self.portfolio_stock_dict[sCode]['종목명'])
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
















