
class DataModel:
    def __init__(self):
        print("데이터 모델")
        self.myLoginInfo = None
        self.itemList = []
        self.myStockBalanceList = []

    class LoginInfo:
        def __init__(self,accCnt,accList,userId,userName,keyBsec,firew,serverGubun):
            self.accCnt = accCnt
            self.accList = accList
            self.userId = userId
            self.userName = userName
            self.keyBsec = keyBsec
            self.firew = firew
            self.serverGubun = serverGubun

            print("사용자이름:"+str(userName))

        def getServerGubun(self):
            if self.serverGubun == "1":
                return "모의투자"
            else:
                return "실투자"

    class ItemInfo:
        def __init__(self, itemCode, itemName):
            self.itemCode = itemCode
            self.itemName = itemName

    class StockBalance:
        def __init__(self, itemCode, itemName, amount, buyPrice, currentPrice, estimateProfit, profitRate):
            self.itemCode = itemCode
            self.itemName = itemName
            self.amount = amount
            self.buyPrice = buyPrice
            self.currentPrice = currentPrice
            self.estimateProfit = estimateProfit
            self.profitRate = profitRate




