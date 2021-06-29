#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 07:53:48 2021

@author: loann
"""

import socket 
import datetime as dt 
import pandas as pd 
import time 


class CLIENT_MT4 : 
    
    def __init__(self) : 
        
        self.PORT = 15555
        self.HOST = '127.0.0.1'
        self.path = "/home/loann/Bureau/Programmes de bureau/Admiral Markets MT4/MQL4/Files/"
        
    #========================================================# 
    # ATTRIBUTE EDITION FUNCTIONS 
    #========================================================# 
    
    def setHstDataPath (self, newPath) : 
        self.path = newPath 
    
    #========================================================#
    # SOCKET FUNCTIONS
    #========================================================# 
        
    def send(self, message) : 
        
        data = ""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.HOST, self.PORT))
            s.sendall(str.encode(message))
            data = s.recv(1024)
            print('Received back : ', repr(data))
        
        return str(data) 
    
    #========================================================#
    # CLIENT FUNCTIONS : CONNECTION
    #========================================================#
    def connection(self, configFile) : 
        
        self.PORT = configFile.get("port")
        self.HOST = configFile.get("host") 
        self.path = configFile.get("path")
    
    #========================================================#
    # CLIENT FUNCTIONS : GETTING DATA
    #========================================================#
    
    def getHistoricalData(self, contractFile, start, stop, timeframe, onlyOpen = True, path = "./", fileName = "Q26_hstData.csv") : 
        
        symbolName = contractFile.get("symbol")
        
        getStr  = "" 
        getStr += "getHst-"
        getStr += "symbol:"+symbolName 
        getStr += "-"
        getStr += "start:"+str(start)
        getStr += "-" 
        getStr += "stop:"+str(stop)
        getStr += "-"
        getStr += "timeframe:"+str(timeframe) 
        getStr += "-" 
        getStr += "path:"+path
        getStr += "-" 
        getStr += "fileName:"+fileName
        
        response = self.send(getStr)
        
        try : 
        
            data = pd.read_csv(self.path+fileName)
            
            # print(data)
            
            dataset = {
                "askopen" : list(), 
                "askhigh" : list(),
                "asklow"  : list(),
                "askclose": list(), 
                "bidopen" : list(), 
                "bidhigh" : list(), 
                "bidlow"  : list(), 
                "bidclose": list(), 
                "date"    : list(), 
                "volume"  : list()
                }
            
            
            for i in range(len(data)) : 
                dataset.get("askopen").append(data["open"].iloc[i]) 
                dataset.get("askhigh").append(data["high"].iloc[i]) 
                dataset.get("asklow").append(data["low"].iloc[i]) 
                dataset.get("askclose").append(data["close"].iloc[i])
                dataset.get("bidopen").append(data["open"].iloc[i]) 
                dataset.get("bidhigh").append(data["high"].iloc[i]) 
                dataset.get("bidlow").append(data["low"].iloc[i]) 
                dataset.get("bidclose").append(data["close"].iloc[i])
                dataset.get("date").append(dt.datetime.strptime(data["time"].iloc[i], "%Y.%m.%d %H:%M:%S"))
                dataset.get("volume").append(data["volume"].iloc[i])
            
            
            
            return dataset 
        
        except : 
            
            return False
        
        
    def getLastPrice(self, contractFile, timeframe = 1) : 
        
        symbolName = contractFile.get("symbol")
        
        getStr  = "" 
        getStr += "getPrice-"
        getStr += "symbol:"+symbolName 
        getStr += "-" 
        getStr += "timeframe:"+str(timeframe)
        
        response = self.send(getStr) 
        response = response.split("b'getPrice-")[1] 
        response = response.split("'")[0] 
        
        response = response.split("-") 
        
        dictPrice = dict() 
        for i in range(len(response)) : 
            locResponse = response[i].split("@")
            dictPrice.update({locResponse[0] : locResponse[1]})
        

        
        marketState = None
        if dictPrice.get("tradeAllowed") != '1.00000000' : 
            marketState = "closed" 
        else : 
            marketState = "open"
            
        dataset = {"askopen"      : dictPrice.get("open"), 
                   "askhigh"      : dictPrice.get("high"),
                   "asklow"       : dictPrice.get("low"),
                   "askclose"     : dictPrice.get("close"), 
                   "bidopen"      : dictPrice.get("open"), 
                   "bidhigh"      : dictPrice.get("high"), 
                   "bidlow"       : dictPrice.get("low"), 
                   "bidclose"     : dictPrice.get("close"), 
                   "askprice"     : dictPrice.get("askPrice"),
                   "bidprice"     : dictPrice.get("bidPrice"),    
                   "date"         : dt.datetime.strptime(dictPrice.get("time"), "%Y.%m.%d %H:%M"), 
                   "volume"       : dictPrice.get("volume"), 
                   "market state" : marketState}
        
        

        return dataset 
    
    #========================================================#
    # CLIENT FUNCTIONS : TRANSACTIONS
    #========================================================#
    def placeOrder_(self, 
                    configFile) : 
        # configFile = {
        #     "contract"  : self.contractsList.get(contractName), 
        #     "action"    : action, 
        #     "orderType" : orderType, 
        #     "volume"    : volume, 
        #     "stoploss"  : stoploss, 
        #     "takeprofit": takeprofit, 
        #     "lmtPrice"  : lmtPrice, 
        #     "auxPrice"  : auxPrice
        #     }
        
        symbolName = configFile.get("contract").get("symbol")
        action = configFile.get("action") 
        orderType = configFile.get("orderType")
        volume = configFile.get("volume") 
        stoploss = configFile.get("stoploss") 
        takeprofit = configFile.get("takeprofit") 
        lmtprice = configFile.get("lmtPrice") 
        
        
        orderList = self.placeOrder(symbolName, 
                                    action = action, 
                                    orderType = orderType, 
                                    volume  = volume, 
                                    stoploss = stoploss, 
                                    takeprofit = takeprofit, 
                                    lmtPrice   = lmtprice, 
                                    pendingExpiration = dt.timedelta(hours = 12)) 
        
        return orderList 
        
    
    
    def placeOrder(self, 
                   symbolName, 
                   action = "long", 
                   orderType = "MKT", 
                   volume  = 0.01, 
                   stoploss = 100., 
                   takeprofit = 0., 
                   lmtPrice   = 0., 
                   pendingExpiration = dt.timedelta(hours = 12)) :
        
        today      = dt.datetime.today()
        pendingExp = today + pendingExpiration 
        # orderExp = today + orderExpiration 
        
        # today = str(dt.datetime.today()) 
        # today = today.split(".")[0]
        # today = today.replace("-", ".")
        
        pendingExp = str(pendingExp) 
        pendingExp = pendingExp.split(".")[0]
        pendingExp = pendingExp[:-3]
        pendingExp = pendingExp.replace("-",".")
        
        
        
        orderStr  = ""
        orderStr += "placeOrder-"
        orderStr += "symbol:"+str(symbolName)
        orderStr += "-"
        orderStr += "action:"+str(action)
        orderStr += "-"
        orderStr += "orderType:"+str(orderType)
        orderStr += "-"
        orderStr += "volume:"+str(volume)
        orderStr += "-"
        orderStr += "stoploss:"+str(stoploss)
        orderStr += "-"
        orderStr += "takeprofit:"+str(takeprofit)
        orderStr += "-" 
        orderStr += "lmtPrice:"+str(lmtPrice)
        orderStr += "-" 
        orderStr += "pendingExpiration:"+str(pendingExp)
        
        
        response = self.send(orderStr) 
        
        response = response.split("b'Order ticket : ")
        response = response[1].split("'")
        response = response[0] 
        
        if type(response) == str : 
            
            orderDict = {"ticket" : response, 
                         "lots"   : volume, 
                         "action" : action, 
                         "symbol" : symbolName, 
                         "expiration" : pendingExp, 
                         "type" : orderType, 
                         "stoploss" : stoploss, 
                         "takeprofit" : takeprofit, 
                         "lmtprice" : lmtPrice}
            
            # self.orderExpiration = orderExp
            # self.activeOrder     = True 
            # self.orderTicket     = response
            # self.volume          = volume
            # self.direction       = action 
            # self.symbol          = symbolName
        
            orderResponse = [orderDict, orderDict, orderDict]
        
        else : 
            
            orderResponse = [False, False, False]
        
        return orderResponse
    
    def closePosition(self, symbolName, order) : 
        
        orderStr  = ""
        orderStr += "closeOrder-"
        orderStr += "ticket:"+str(order.get("ticket"))
        orderStr += "-" 
        orderStr += "lots:"+str(order.get("lots"))
        orderStr += "-"
        orderStr += "action:"+str(order.get("action"))
        orderStr += "-"
        orderStr += "symbol:"+str(symbolName)
        
        response = self.send(orderStr) 
        
        response = response.split("b'Closing State : ")
        response = response[1].split("'")
        response = response[0] 
        
        if response == "True" : 
        
            return True 
        
        else : 
            
            return False 
        
    def editPosition(self, 
                     order, 
                     stoploss = None, 
                     takeprofit = None, 
                     lmtPrice = None) : 
        
        if stoploss is None : 
            stoploss_ = order.get("stoploss") 
        else : 
            stoploss_ = stoploss 
        
        if takeprofit is None : 
            takeprofit_ = order.get("takeprofit") 
        else : 
            takeprofit_ = takeprofit 
        
        
        orderStr  = ""
        orderStr += "modifyOrder-"
        orderStr += "ticket:"+str(order.get("ticket"))
        orderStr += "-" 
        orderStr += "stoploss:"+str(stoploss_)
        orderStr += "-"
        orderStr += "takeprofit:"+str(takeprofit_)
        
        response = self.send(orderStr) 
        
        response = response.split("b'Modification state : ")
        response = response[1].split("'")
        response = response[0] 
        
        if response == "True" : 
        
            return True 
        
        else : 
            
            return False 
        
    def cancelOrder(self, 
                    order) : 
        
        orderStr  = ""
        orderStr += "cancelOrder-"
        orderStr += "ticket:"+str(order.get("ticket"))
        
        response = self.send(orderStr) 
        
        response = response.split("b'Cancel state : ")
        response = response[1].split("'")
        response = response[0] 
        
        if response == "True" : 
        
            return True 
        
        else : 
            
            return False 
        

    
    

    