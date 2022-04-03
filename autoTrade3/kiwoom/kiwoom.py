import os
import sys

from kiwoom.viewController import *

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *

class Kiwoom(QAxWidget):  #QAxWidget
    def __init__(self):
        super().__init__()

        ###############################UI##################################
        self.ui = viewController()
        self.ui.show()
        self.ui.setUI()

        # UI event Triger
        self.ui.searchItemButton.clicked.connect(self.searchItem)
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
        self.jango_dict = {} # 오늘산 종목
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
        self.detail_account_mystock() #계좌평가 잔고내역 가져오기
        self.not_concluded_account() # 미체결 요청
        self.getItemList() #종목코드가져오기

        self.read_code() # 저장된 종목 파일 불러오기
        self.screen_number_setting() # 스크린번호를 할당

        # 장이 시작인지 끝인지 체크
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '', self.realType.REALTYPE['장시작시간']['장운영구분'], "0")

        for code in self.portfolio_stock_dict.keys():
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            fids = self.realType.REALTYPE['주식체결']['체결시간']

            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1")
            print("실시간등록코드 : %s, 스크린번호: %s, fid번호: %s" %(code, screen_num, fids))



    def get_ocx_instance(self):
        #키움오픈api를 사용하게 하는
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        # QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")


    ############################################# UI #######################################################
    # def setUI(self):
    #     self.ui.setupUi(self)
    #
    #     column_head = ["00:지정가", "03:시장가", "05:조건부지정가", "06:최유리지정가", "07:최우선지정가", "10:지정가IOC",
    #                    "13:시장가IOC", "16:최유리IOC", "20:지정가FOK", "26:최유리FOK", "61:장전시장외종가"]
    #     self.ui.gubuncomboBox.addItems(column_head)
    #
    #     column_head = ["1:신규매수", "2:신규매도", "3:매수취소", "4:매도취소", "5:매수정정", "6:매도정정"]
    #     self.ui.tradeGubuncomboBox.addItems(column_head)

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

        
    def searchItem(self):
        print("종목조회")
        itemName = self.ui.searchItemTextEdit.toPlainText()
        for item in self.market_stock_list.keys():
            print(item)
            if item == itemName:
                print(self.market_stock_list[item]['종목코드'])
                tempStockCode = self.market_stock_list[item]['종목코드']
                if tempStockCode not in self.portfolio_stock_dict.keys():
                    self.day_kiwoom_db(code=tempStockCode)
                break

    ############################################# UI #######################################################

    

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

        self.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역", "opw00018", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    # 미체결 내역
    def not_concluded_account(self, sPrevNext="0"):
        print("미체결 요청")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")

        self.dynamicCall("CommRqData(String, String, int, String)", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    #종목분석용
    def calculator_fnc(self):
        '''
        종목분석 실행용 함수
        :return:
        '''
        code_list = self.get_code_list_by_market("10")
        print("코스닥갯수 %s" % len(code_list))

        for idx, code in enumerate(code_list):
            # 스크린번호를 끊어줌 (A코드로 요청->끊어줌 ->B코드로 요청->끊어줌 ->C코드로 요청)
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculator_stock)

            print("%s / %s: 가지고온 코드 갯수 %s" % (idx+1, len(code_list), code))

            self.day_kiwoom_db(code=code)

    #종목코드를 가져옴
    def get_code_list_by_market(self, market_code):
        '''
        종목코드들 반환
        :param market_code:
        :return:
        '''
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(";")[:-1]# 마지막에 공백나오니 하나 지우는것
        return code_list



    # 일봉데이터 받아오기
    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        print("일봉데이터:%s" % code)

        QTest.qWait(3600) #3.6초 딜레이(과도한 조회로 오류방지)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculator_stock)

        self.calculator_event_loop.exec_()

    #저장된 종목 파일 불러오기
    def read_code(self):
        if os.path.exists("files/condition_stock.txt"):
            f = open("files/condition_stock.txt", "r", encoding="utf8")

            lines = f.readlines()
            for line in lines:
                if line != "":
                    ls = line.split("\t") # 파일 쓸때 \t로 구분지어 놨기때문에

                    stock_code = ls[0]
                    stock_nm = ls[1]
                    stock_price = int(ls[2].split("\n")[0]) # 마지막에 엔터가 들어있으므로 스플릿 또 해줌
                    stock_price = abs(stock_price) #절대값

                    self.portfolio_stock_dict.update({stock_code:{"종목명":stock_nm, "현재가": stock_price}})

            f.close() #파일 닫기
            print(self.portfolio_stock_dict)

    def screen_number_setting(self):
        screen_overwrite = []

        # 계좌평가잔고내역에 있는 종목들
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

            elif code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({code:{"스크린번호":str(self.screen_real_stock), "주문용스크린번호":str(self.screen_meme_stock)}})

            cnt +=1

            print(self.portfolio_stock_dict)


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

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명":code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt += 1

            print("가지고있는 종목갯수 %s" % cnt)
            print("가지고있는 종목 %s" % self.account_stock_dict)

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

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print("데이터일수 %s" % cnt)

            #한번조회하면 600일치 일봉데이터를 받을 수 있다.
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


            if sPrevNext =="2":
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else:
                ######더이상 데이터가 없으니 조건에 부합하는 건 따로 저장해놓는다

                # print("총 일수 %s "% len(self.calcul_data))
                # pass_success = False
                #
                # ##120일 이평선을 그릴수 있는 데이터가 있는지 체크
                # if self.calcul_data ==None or len(self.calcul_data) <120:
                #     pass_success = False
                # else:
                #     ##120일 이상 되면
                #     total_price = 0
                #     for value in self.calcul_data[:120]: #오늘부터 120일 미만일까지
                #         total_price += int(value[1]) # 1:현재가
                #
                #     moving_average_price = total_price/120
                #
                #
                #     bottom_stock_price = False
                #     check_price = None
                #     # 오늘 저가가 이평선보다 아래고 오늘 고가가 이평선보다 위다
                #     if int(self.calcul_data[0][7]) <= moving_average_price and int(self.calcul_data[0][6]) >= moving_average_price:
                #         print("오늘주가가 120이평선에 걸쳐잇는 것 확인")
                #
                #         bottom_stock_price = True
                #         check_price = int(self.calcul_data[0][6])
                #
                #     # 과거 일봉들이 120 이평선보다 밑에 있는지 확인
                #     # 그렇게 확인을 하다가 일봉이 120일 이평선보다 위에 있으면 계산진행
                #
                #     prev_price = None #과거에 120일선 위에 있던 일봉의 저가
                #
                #     if bottom_stock_price == True:
                #
                #         moving_average_price_prev = 0 # 과거 각 일자마다 이평값
                #         price_top_moving = False
                #
                #         idx = 1 # 1봉전값부터 시작
                #
                #         while True:
                #             if len(self.calcul_data[idx:]) <120: # 120일치 데이터가 있는지 계속 확인
                #                 print("120일치가 없음")
                #                 break
                #
                #             total_price =0
                #             for value in self.calcul_data[idx:120+idx]: #1일씩 과거로 가며 120일 치 데이터 가지고옴
                #                 total_price += int(value[1])
                #
                #             moving_average_price_prev = total_price/120
                #
                #             if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <=20:
                #                 print("20일동안 주가가 120선과 같거나 위에 있으면 통과못함")
                #                 price_top_moving = False
                #                 break
                #
                #             elif int(self.calcul_data[idx][7]) > moving_average_price_prev and idx>20:
                #                 print("120일 이평선 위에있는 일봉 확인됨")
                #                 price_top_moving = True
                #                 prev_price = int(self.calcul_data[idx][7])
                #                 break
                #
                #             idx += 1 # 다성립안했으면 그 하루전거 계산
                #
                #         # 해당부분의 이평선이 가장 최근일자의 이평선 가격보다 낮은지 확인
                #         if price_top_moving == True:
                #             if moving_average_price>moving_average_price_prev and check_price>prev_price:
                #                 print("최종조건 만족")
                #                 pass_success = True
                #
                #
                # if pass_success == True:
                print("조건 통과됨")

                code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)

                # 조건만족한 종목 파일로 저장하기
                f = open("files/condition_stock.txt", "a", encoding="utf8")
                print(code)
                print(code_nm)
                print(str(self.calcul_data[0][1]))

                f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                f.close()

                # elif pass_success == False:
                #     print("조건 통과 못함")

                self.calcul_data.clear()
                self.calculator_event_loop.exit()


    ###########################################################################################
    ########################################실시간 slot#########################################
    ###########################################################################################

    def realdata_slot(self, sCode, sRealType, sRealData):

        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']
            value = self.dynamicCall("GetCommRealData(QString, int)", sCode, fid)

            if value =="0":
                print("장 시작 전")
            elif value == "3":
                print("장 시작")
            elif value == "2":
                print("장 종료, 동시호가로 넘어감")
            elif value == "4":
                print("3시 30분 장 종료")

                for code in self.portfolio_stock_dict.keys():
                    self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['스크린번호'],code)


                self.file_delete()
                self.calculator_fnc()

                sys.exit()

        elif sRealType == "주식체결":
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

            print(self.portfolio_stock_dict[sCode])


            #############################
            ######## 매수 매도 조건########

            # 이전에 사놨엇던게 있고, 오늘 산거에는 없어야 함
            if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():

                asd = self.account_stock_dict[sCode]

                meme_rate = (b- asd['매입가']) / asd['매입가'] *100 # 등락률

                if asd['매매가능수량']>0 and (meme_rate>5 or meme_rate <-5):


                    order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                 , ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                 sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                if order_success == 0:
                    print("매도주문전달성공")
                    del self.account_stock_dict[sCode]
                else :
                    print("매도주문전달실패")

            # 오늘산 잔고에 있는경우
            elif sCode in self.jango_dict.keys():
                jd = self.jango_dict[sCode]
                meme_rate = (b - jd['매입단가']) / jd['매입단가'] *100

                if jd['주문가능수량']>0 and (meme_rate>5 or meme_rate<-5):
                    order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                                     ,["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                                       sCode, jd['주문가능수량'], 0, self.realType.REALTYPE['거래구분']['시장가'], ""])

                    if order_success == 0:
                        self.logging.logger.debug("매도주문 전달 성공")
                    else:
                        self.logging.logger.debug("매도주문 전달 실패")


            
            # 등락률이 2.0 이상이고 오늘산 잔고에 없는경우
            elif d > 2.0 and sCode not in self.jango_dict.keys():
                print("%s %s" % ("신규매수", sCode))

                result = (self.use_money * 0.1) /e
                quantity = int(result)

                order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                                 ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                                                  sCode, quantity, e, self.realType.REALTYPE['거래구분']['지정가'], ""])

                if order_success == 0:
                    self.logging.logger.debug("매수주문 전달 성공")
                else:
                    self.logging.logger.debug("매수주문 전달 실패")


            not_meme_list = list(self.not_account_stock_dict) # 리스트를 씌우면 copy라서 하나바꾼다고 다른게 같이 바뀌진 않음
            for order_num in not_meme_list:                   # 계산중에 미체결잔고가 늘어나서 발생하는 에러를 없애기 위해 복사
                code = self.not_account_stock_dict[order_num]['종목코드']
                meme_price = self.not_account_stock_dict[order_num]['주문가격']
                not_quantity = self.not_account_stock_dict[order_num]['미체결수량']
                # meme_gubun = self.not_account_stock_dict[order_num]['매수도구분']
                order_gubun = self.not_account_stock_dict[order_num]['주문구분']

                # 매수취소 : 기존주문 매수이고, 미체결수량이 0보다 크고, 현재가가 주문가격보다 높을경우
                if order_gubun == "매수" and not_quantity >0 and e > meme_price :
                    print("%s %s" %"매수취소", sCode)

                    order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                        ["매수취소", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 3,
                         code, 0, 0, self.realType.REALTYPE['거래구분']['지정가'], order_num])

                    if order_success == 0:
                        self.logging.logger.debug("취소주문 전달 성공")
                    else:
                        self.logging.logger.debug("취소주문 전달 실패")



                elif not_quantity == 0:
                    del self.not_account_stock_dict[order_num]



    #################################################################################################
    ############################### 주문 slot #######################################################

    def chejan_slot(self, sGubun, nItemCnt, sFidList):

        if int(sGubun) == 0:
            print("주문체결")
            account_num = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결'],['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['종목명'])
            stock_name = stock_name.strip()

            original_order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['원주문번호'])
            order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['주문번호'])
            order_status = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['주문상태'])
            order_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['주문수량'])
            order_quan = int(order_quan)

            order_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['주문가격'])
            order_price = int(order_price)

            not_chegual_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['미체결수량'])
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
            current_price = abs(int(current_price))

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결'], ['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))


            ##### 새로운 주문이면 주문번호 할당
            if order_number not in self.not_account_stock_dict.keys():
                self.not_account_stock_dict.update({order_number:{}})

            self.not_account_stock_dict[order_number].update({"종목코드": sCode})
            self.not_account_stock_dict[order_number].update({"주문번호": order_number})
            self.not_account_stock_dict[order_number].update({"종목명": stock_name})
            self.not_account_stock_dict[order_number].update({"주문상태": order_status})
            self.not_account_stock_dict[order_number].update({"주문수량": order_quan})
            self.not_account_stock_dict[order_number].update({"주문가격": order_price})
            self.not_account_stock_dict[order_number].update({"미체결수량": not_chegual_quan})
            self.not_account_stock_dict[order_number].update({"원주문번호": original_order_number})
            self.not_account_stock_dict[order_number].update({"주문구분": order_gubun})
            # self.not_account_stock_dict[order_number].update({"매도수구분": meme_gubun})
            self.not_account_stock_dict[order_number].update({"주문/체결시간": chegual_time_str})
            self.not_account_stock_dict[order_number].update({"체결가": chegual_price})
            self.not_account_stock_dict[order_number].update({"체결량": chegual_quantity})
            self.not_account_stock_dict[order_number].update({"현재가": current_price})
            self.not_account_stock_dict[order_number].update({"(최우선)매도호가": first_sell_price})
            self.not_account_stock_dict[order_number].update({"(최우선)매수 호가": first_buy_price})

            print(self.not_account_stock_dict)


        # 잔고
        elif int(sGubun) == 1:
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목코드'])[1:]

            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['현재가'])
            current_price = abs(int(current_price))

            stock_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['보유수량'])
            stock_quan = int(stock_quan)

            like_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)

            buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매입단가'])
            buy_price = abs(int(buy_price))

            total_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['총매입가'])
            total_buy_price = int(total_buy_price)

            meme_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매도매수구분'])
            meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            if sCode not in self.jango_dict.keys():
                self.jango_dict.update({sCode:{}})

            self.jango_dict[sCode].update({"현재가":current_price})
            self.jango_dict[sCode].update({"종목코드": sCode})
            self.jango_dict[sCode].update({"종목명": stock_name})
            self.jango_dict[sCode].update({"보유수량": stock_quan})
            self.jango_dict[sCode].update({"주문가능수량": like_quan})
            self.jango_dict[sCode].update({"매입단가": buy_price})
            self.jango_dict[sCode].update({"총매입가": total_buy_price})
            self.jango_dict[sCode].update({"매도매수구분": meme_gubun})
            self.jango_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            self.jango_dict[sCode].update({"(최우선)매수호가": first_buy_price})

            if stock_quan == 0 :
                del self.jango_dict[sCode]
                self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[sCode]['스크린번호'], sCode)


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



                












