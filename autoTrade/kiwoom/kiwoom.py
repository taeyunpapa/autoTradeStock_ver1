import os
import sys

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *

class Kiwoom(QAxWidget):  #QAxWidget
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
        self.screen_real_stock = "5000" # 종목별로 할당할 스크린번호
        self.screen_meme_stock = "6000" # 종목별로 할당할 주문용 스크린 번호
        self.screen_start_stop_real = "1000" # 장이 시작인지 끝인지
        ################################


        #######변수모음##############
        self.account_num = None
        self.market_open_f = None

        ###########################

        #######계좌관련 변수##########
        self.use_money = 0
        self.use_money_persent = 0.5
        #############################

        ##########변수모음##############
        self.market_stock_list = {}
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        self.portfolio_stock_dict = {}
        self.portfolio_stock_buy = {}
        self.jango_dict = {} # 잔고
        self.online_jango_dict = {}  # 실시간잔고
        self.jongmok1_hoga = {} # 종목1 호가별 거래대금 모음
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
        self.detail_account_info() #예수금 가져오기
        self.not_concluded_account() # 미체결 요청
        self.getItemList() #종목코드가져오기
        self.read_code()  # 저장된 종목 파일 불러오기
        self.detail_account_mystock()  # 계좌평가 잔고내역 가져오기

        self.screen_number_setting() # 스크린번호를 할당

        # 장이 시작인지 끝인지 체크
       # print("장시작체크")
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '', self.realType.REALTYPE['장시작시간']['장운영구분'], "0")




    def get_ocx_instance(self):
        #키움오픈api를 사용하게 하는
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
                    self.market_stock_list.update({name:{}})

                self.market_stock_list[name].update({"종목코드":code})

        
    def searchItem(self,itemName):
        print("종목조회 : %s" % itemName)
        meme_code = None
        # itemName = self.ui.searchItemTextEdit.toPlainText()
        for item in self.market_stock_list.keys():
            if item == itemName:
                print(self.market_stock_list[item]['종목코드'])
                tempStockCode = self.market_stock_list[item]['종목코드']
                if tempStockCode not in self.portfolio_stock_dict.keys():
                    self.portfolio_stock_dict.update({tempStockCode: {"종목명": itemName,
                        "주문용스크린번호":self.screen_meme_stock, "익절횟수":0, "조건11":"N", "조건12":"N"
                        , "조건21":"N", "조건22":"N", "조건23":"N", "조건31":"N", "조건32":"N", "조건33":"N"}})
                    print("매매종목추가:%s" % self.portfolio_stock_dict[tempStockCode]['종목명'])
                    meme_code = tempStockCode
                    # 일봉데이터 받아오기
                    self.day_kiwoom_db(code=tempStockCode)

                break

        for code in self.portfolio_stock_dict.keys():
            screen_num = self.portfolio_stock_dict[code]['주문용스크린번호']
            fids = self.realType.REALTYPE['주식체결']['체결시간']

            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1")
            print("실시간등록코드 : %s, 스크린번호: %s, fid번호: %s" %(code, screen_num, fids))


    # 이벤트 슬롯
    def event_slot(self):
        #로그인 이벤트 슬롯
        self.OnEventConnect.connect(self.login_slot)

        #tr이벤트 슬롯
        self.OnReceiveTrData.connect(self.trData_slot)

        self.OnReceiveMsg.connect(self.msg_slot)

    # 실시간 이벤트 슬롯
    def real_event_slot(self):
        self.OnReceiveRealData.connect(self.realdata_slot)
        self.OnReceiveChejanData.connect(self.chejan_slot) ## 주문관련 슬롯

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.event_login_loop = QEventLoop()
        self.event_login_loop.exec_()

    def login_slot(self, errCode):
        print(errors(errCode))

        #로그인이 완료되면 이벤트 로그인 루프를 끊어줌
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

    #계좌평가잔고내역
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

        self.dynamicCall("CommRqData(String, String, int, String)", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()





    # 일봉데이터 받아오기
    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        print("일봉데이터:%s" % code)

        QTest.qWait(300) #3.6초 딜레이(과도한 조회로 오류방지)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculator_stock)

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

        #스크린번호 할당
        cnt = 0
        for code in screen_overwrite:

            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            # 스크린번호 하나당 종목 50개씩 넣는다
            if (cnt %50) ==0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)

            if (cnt %50) == 0:
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code].update({"스크린번호":str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호":str(self.screen_meme_stock )})

            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({code:{"스크린번호":str(self.screen_real_stock), "주문용스크린번호":str(self.screen_meme_stock)}})

            cnt +=1

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

            print("예수금 %s" %deposit)

            self.use_money = deposit * self.use_money_persent
            self.use_money = self.use_money / 4

            ok_deposit = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액"))
            print("출금가능금액 %s" % ok_deposit)

            ####결과 다 받았으니깐 이벤트 끊어줌
            self.detail_account_info_event_loop.exit()

        if sRQName == "계좌평가잔고내역":

            total_buy_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result = int(total_buy_money)

            print("총매입금액 %s" % total_buy_money_result)

            total_profit_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)")
            total_profit_rate_result = float(total_profit_rate)

            print("총수익률 %s" % total_profit_rate_result)

            #보유종목가져오기
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName) #보유종목갯수 : 한번에 20개씩밖에 조회안됨
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                #strip : 공백지우기
                code = code.strip()[1:] # A12345 --> 12345

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

                if code in self.jango_dict.keys():
                    pass
                else:
                    self.jango_dict.update({code:{}})

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.jango_dict[code].update({"종목명":code_nm})
                self.jango_dict[code].update({"보유수량": stock_quantity})
                self.jango_dict[code].update({"매입가": buy_price})
                self.jango_dict[code].update({"수익률(%)": learn_rate})
                self.jango_dict[code].update({"현재가": current_price})
                self.jango_dict[code].update({"매입금액": total_chegual_price})
                self.jango_dict[code].update({"매매가능수량": possible_quantity})

                if code not in self.online_jango_dict.keys():
                    self.online_jango_dict.update({code:{}})

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
                self.detail_account_info_event_loop.exit()  #더이상 다음페이지가 없으니 연결 끊어줌


        elif sRQName == "실시간미체결요청":
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            for i in range(rows):
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태") #접수/확인/체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분") #매도/매수/정정/취소
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")

                order_no = int(order_no.strip())
                code = code.strip()
                code_nm = code_nm.strip()
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-') #-매도 --> 매도
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
            cnt=5
            print("데이터일수 %s" % cnt)

            #한번조회하면 600일치 일봉데이터를 받을 수 있다.
            self.calcul_data.clear()
            sum = 0
            for i in range(cnt):

                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                row_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")


                data.append("") #GetCommDataEx 함수와 동일형태로 만들어주기 위해
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
                self.price_sum.update({code:{}})

            self.price_sum[code].update({'합계':sum})
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
                    self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['주문용스크린번호'], code)

                # del self.jongmok1_hoga

                # self.file_delete()
                # self.calculator_fnc()
                self.jango_dict.clear()

                sys.exit()

        elif sRealType == "주식체결":
            # print("주식체결:%s" % sCode)
            a = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간']) #HHMMSS
            
            b = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가']) #+(-)2500
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

            i = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['고가'])
            i = abs(int(i))

            j = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['시가'])
            j = abs(int(j))

            k = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['저가'])
            k = abs(int(k))

            if sCode not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({sCode:{}})

            self.portfolio_stock_dict[sCode].update({"체결시간": a})
            self.portfolio_stock_dict[sCode].update({"현재가": b})
            self.portfolio_stock_dict[sCode].update({"전일대비": c})
            self.portfolio_stock_dict[sCode].update({"등락율": d})
            self.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
            self.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
            self.portfolio_stock_dict[sCode].update({"거래량": g})
            self.portfolio_stock_dict[sCode].update({"누적거래량": h})
            self.portfolio_stock_dict[sCode].update({"고가": i})
            self.portfolio_stock_dict[sCode].update({"시가": j})
            self.portfolio_stock_dict[sCode].update({"저가": k})
            print(self.portfolio_stock_dict)





            #############################
            ######## 매수 매도 조건########

            ############### 매수 #################
            average5 = int((self.price_sum[sCode]['합계'] + j) / 5)

            if self.market_open_f == "Y" or self.market_open_f == None:

                if sCode in self.portfolio_stock_dict.keys() and sCode not in self.portfolio_stock_buy.keys():

                    if self.portfolio_stock_dict[sCode]['조건21'] == "N" and self.portfolio_stock_dict[sCode]['조건31']=="N":
                        if j > average5:
                            if j > b:
                                if average5 > b:
                                    self.portfolio_stock_dict[sCode]['조건11'] = "Y"
                                    #print("종목:%s 조건11:Y" % self.portfolio_stock_dict[sCode]['종목명'])
                                elif b > average5:
                                    if self.portfolio_stock_dict[sCode]['조건11'] == "Y":
                                        self.portfolio_stock_dict[sCode]['조건12'] = "Y"
                                        #print("종목:%s 조건12:Y" % self.portfolio_stock_dict[sCode]['종목명'])

                                        quantity = int(2000000 / b)
                                        order_success = self.dynamicCall(
                                            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                            ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                             sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                        if order_success == 0:
                                            print("케이스1 매수:%s" % sCode)

                                            if sCode not in self.portfolio_stock_buy.keys():
                                                self.portfolio_stock_buy.update({sCode: {}})

                                        else:
                                            print("매수주문 전달 실패")

                    if self.portfolio_stock_dict[sCode]['조건11'] =="N" and self.portfolio_stock_dict[sCode]['조건31'] == "N":
                        if j > average5:
                            if j > b:
                                if b > average5:
                                    self.portfolio_stock_dict[sCode]['조건21'] = "Y"
                                    #print("종목:%s 조건21:Y" % self.portfolio_stock_dict[sCode]['종목명'])

                                elif average5 > b:
                                    if self.portfolio_stock_dict[sCode]['조건21'] == "Y":
                                        self.portfolio_stock_dict[sCode]['조건22'] = "Y"
                                       # print("종목:%s 조건22:Y" % self.portfolio_stock_dict[sCode]['종목명'])

                                if self.portfolio_stock_dict[sCode]['조건22'] == "Y" and b > average5:

                                    quantity = int(2000000 / b)
                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                        ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                         sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    if order_success == 0:
                                        print("케이스21 매수:%s" % sCode)
                                        if sCode not in self.portfolio_stock_buy.keys():
                                            self.portfolio_stock_buy.update({sCode: {}})
                                    else:
                                        print("매수주문 전달 실패")

                            elif b > j:
                                if self.portfolio_stock_dict[sCode]['조건21'] == "Y":
                                    self.portfolio_stock_dict[sCode]['조건23'] = "Y"
                                   # print("종목:%s 조건23:Y" % self.portfolio_stock_dict[sCode]['종목명'])

                                    quantity = int(2000000 / b)
                                    order_success = self.dynamicCall(
                                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                        ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                         sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    if order_success == 0:
                                        print("케이스22 매수:%s" % sCode)
                                        if sCode not in self.portfolio_stock_buy.keys():
                                            self.portfolio_stock_buy.update({sCode: {}})
                                    else:
                                        print("매수주문 전달 실패")

                    if self.portfolio_stock_dict[sCode]['조건11'] == "N" and self.portfolio_stock_dict[sCode]['조건21'] == "N":
                        if b > j:
                            self.portfolio_stock_dict[sCode]['조건31'] = "Y"
                           # print("종목:%s 조건31:Y" % self.portfolio_stock_dict[sCode]['종목명'])

                        elif j > b:
                            if self.portfolio_stock_dict[sCode]['조건31'] == "Y":
                                self.portfolio_stock_dict[sCode]['조건32'] = "Y"
                               # print("종목:%s 조건32:Y" % self.portfolio_stock_dict[sCode]['종목명'])

                            else:
                                self.portfolio_stock_dict[sCode]['조건33'] = "Y"
                               # print("종목:%s 조건33:Y" % self.portfolio_stock_dict[sCode]['종목명'])

                        if b > j and self.portfolio_stock_dict[sCode]['조건32'] == "Y":

                            print("케이스31 매수:%s" % sCode)
                            quantity = int(2000000 / b)
                            order_success = self.dynamicCall(
                                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                 sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                            if order_success == 0:
                                print("케이스31 매수:%s" % sCode)
                                if sCode not in self.portfolio_stock_buy.keys():
                                    self.portfolio_stock_buy.update({sCode: {}})

                            else:
                                print("매수주문 전달 실패")

                        if b > j and self.portfolio_stock_dict[sCode]['조건33'] == "Y":

                            quantity = int(2000000 / b)
                            order_success = self.dynamicCall(
                                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                 sCode, quantity, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                            if order_success == 0:
                                print("케이스32 매수:%s" % sCode)
                                if sCode not in self.portfolio_stock_buy.keys():
                                    self.portfolio_stock_buy.update({sCode: {}})

                            else:
                                print("매수주문 전달 실패")


                ######################################## 매도 ###########################################
                ########################################################################################

                if sCode in self.online_jango_dict.keys():

                    asd = self.online_jango_dict[sCode]

                    #### 익절####

                    medo_base_price1 = 0
                    medo_base_price2 = 0
                    meme_rate = (b - asd['매입단가']) / asd['매입단가'] * 100  # 등락률
                    print("종목:%s 등락률:%s" %(self.online_jango_dict[sCode]['종목명'], meme_rate))

                    if asd['주문가능수량'] > 0 and meme_rate > 5:
                        medo_base_price1 = b

                    elif asd['주문가능수량'] > 0 and 5 >= meme_rate and medo_base_price1 > 0:

                       if medo_base_price1 > b:
                           order_success = self.dynamicCall(
                               "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                               , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                  sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                           if order_success == 0:
                               print("익절1 매도:%s" % sCode)

                           else:
                               print("매도주문 전달 실패")

                       else:
                            print("5프로이상 홀딩")


                    elif asd['주문가능수량'] > 0 and meme_rate > 2:

                       if self.portfolio_stock_dict[sCode]['익절횟수'] == 0:
                           medo_base_price2 = b
                           medo_quan = int(asd['주문가능수량'] / 2)

                           order_success = self.dynamicCall(
                               "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                               , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                  sCode, medo_quan, b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                           if order_success == 0:
                                self.portfolio_stock_dict[sCode].update({"익절횟수": 1})
                                print("익절2 매도:%s" % sCode)
                           else:
                               print("매도주문 전달 실패")

                    elif asd['주문가능수량'] > 0 and 2 >= meme_rate and medo_base_price2> b:

                       order_success = self.dynamicCall(
                           "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                           , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                              sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                       if order_success == 0:
                           print("익절3 매도:%s" % sCode)
                           self.portfolio_stock_dict[sCode].update({"익절횟수": 1})

                       else:
                           print("매도주문 전달 실패")

                    #### 손절 ####
                    else:

                        if sCode in self.online_jango_dict.keys():
                            buyprice = self.online_jango_dict[sCode]['매입단가']
                            #if self.account_stock_dict[sCode]['매수구분'] == "case11" \
                                  #  or self.account_stock_dict[sCode]['매수구분'] == "case21":

                            if buyprice>b:

                                order_success = self.dynamicCall(
                                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                        , ["신규매도", self.online_jango_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                        sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                if order_success == 0:
                                    print("케이스1 매도:%s" % sCode)

                                else:
                                    print("매도주문 전달 실패")

                        if sCode in self.account_stock_dict.keys():

                            if self.account_stock_dict[sCode]['매수구분'] == "case22" \
                                or self.account_stock_dict[sCode]['매수구분'] == "case31" \
                                or self.account_stock_dict[sCode]['매수구분'] == "case32":

                                    if j>b:

                                         order_success = self.dynamicCall(
                                            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                            , ["신규매도", self.online_jango_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                            sCode, asd['주문가능수량'], b, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                         if order_success == 0:

                                            print("케이스2 매도:%s" % sCode)

                                         else:
                                            print("매도주문 전달 실패")



    #################################################################################################
    ############################### 주문 slot #######################################################

    def chejan_slot(self, sGubun, nItemCnt, sFidList):

        if int(sGubun) == 0:
            print("주문체결")
            account_num = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결'],['계좌번호'])
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
                not_chegual_quan =0
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
                self.account_stock_dict.update({sCode:{}})

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

            print(rowsCode)
            print(sCode)
            print(self.account_stock_dict)


        # 잔고
        elif int(sGubun) == 1:
            print("잔고")
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목코드'])[1:]

            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['현재가'])
            if current_price =='':
                current_price=0

            current_price = abs(int(current_price))

            stock_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['보유수량'])
            if stock_quan =='':
                stock_quan=0
            stock_quan = int(stock_quan)

            like_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)

            buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매입단가'])
            if buy_price =='':
                buy_price=0
            buy_price = abs(int(buy_price))

            total_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['총매입가'])
            if total_buy_price =='':
                total_buy_price=0
            total_buy_price = int(total_buy_price)

            meme_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매도매수구분'])
            meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            if sCode not in self.online_jango_dict.keys():
                self.online_jango_dict.update({sCode:{}})

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

            if stock_quan == 0:
                del self.online_jango_dict[sCode]
                # self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[sCode]['스크린번호'], sCode)

                if sCode in self.portfolio_stock_buy.keys():
                    del self.portfolio_stock_buy[sCode]

                for sCode in self.portfolio_stock_dict.keys():
                    # 조건초기화
                    self.portfolio_stock_dict[sCode]['조건11'] = "N"
                    self.portfolio_stock_dict[sCode]['조건12'] = "N"
                    self.portfolio_stock_dict[sCode]['조건21'] = "N"
                    self.portfolio_stock_dict[sCode]['조건22'] = "N"
                    self.portfolio_stock_dict[sCode]['조건23'] = "N"
                    self.portfolio_stock_dict[sCode]['조건31'] = "N"
                    self.portfolio_stock_dict[sCode]['조건32'] = "N"
                    self.portfolio_stock_dict[sCode]['조건33'] = "N"

           # else:

                #for sCode in self.online_jango_dict.keys():
                    #self.day_kiwoom_db(code=sCode)

                   # fids = self.realType.REALTYPE['주식체결']['체결시간']

                    #self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_meme_stock, sCode, fids, "1")
            ##print(self.online_jango_dict)


    # 송수신 메세지 get
    def msg_slot(self, sScrNo, sRgName, sTrCode, msg):
        print("스크린: %s, 요청이름: %s, tr코드:%s----%s " %(sScrNo, sRgName, sTrCode, msg))


    # 파일 삭제
    def file_delete(self):
        if os.path.isfile("files/condition_stock.txt"):
            os.remove("files/condition_stock.txt")


    class ItemInfo:
        def __init__(self, itemCode, itemName):
            self.itemCode = itemCode
            self.itemName = itemName



                












