#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 08:59:35 2021

@author: loann
"""
from threading import Thread 
import datetime as dt 
import pandas as pd 
import queue 
import time 

import sys, os 
# sys.path.append("../ibkrSide/")





from ibapi.client  import EClient 
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract 
from ibapi.order    import Order 
from ibapi.ticktype import TickTypeEnum

# from enum_IBKR import EnumContract, EnumOrder


class ERROR : 
    """! \private
    Error management sub-class 
    """
    
    def error(self, id, errorCode, errorString):
        """ 
        This function print errors if they happen 
        """
        error_message = (
            "IB Error ID (%d), Error Code (%d) with "
            "response '%s'" % (id, errorCode, errorString)
        )
        print ("IB Error ID (%d), Error Code (%d) with response '%s'" % (id, errorCode, errorString))

        self.error.put(error_message)


class QUEUE : 
    """! \private 
    Queue management sub-class 
    """
    
    def init(self) : 
        file_ = queue.Queue() 
        self.file = file_ 
        return file_
    
    def get(self, file, timeout = 5) : 

        return file.get(timeout = timeout)
    
    def getList(self, file, timeout = 5) : 

        lst = list()
        while(file.qsize() > 0) : 
            lst.append(file.get(timeout = timeout))
        file.queue.clear()
        
        return lst 
    



class WRAPPER(EWrapper, QUEUE, ERROR) :
    """! \private 
    IBKR Wrapper class. 
    """ 
    
    def nextValidId(self, 
                    orderId) :
        self.nextValidOrderId = orderId 
        print ("Next valid ID : ",self.nextValidOrderId) 
    
    def currentTime(self, time) : 
        if self.showLog : print ("Server time : ",time)
        self.file.put(time)
        
    def historicalData(self, reqId, bar) : 
        """
        See : http://interactivebrokers.github.io/tws-api/classIBApi_1_1Bar.html 
        and : http://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#ac943e5b81f6de111ddf71a1f05ab6282

        """
        dataLine = {"reqId" : reqId, 
                    "Time"  : bar.date, 
                    "Open"  : bar.open, 
                    "High"  : bar.high, 
                    "Low"   : bar.low, 
                    "Close" : bar.close, 
                    "Volume": bar.volume, 
                    "Count" : bar.barCount} # The number of trades during the bar's timespan
        if self.showLog : print ("Data line : ",dataLine)
        self.file.put(dataLine)
    
    def tickPrice(self, 
                  reqId, 
                  tickType, 
                  price, 
                  attrib) : 
        if self.showLog : print (TickTypeEnum.to_str(tickType), price, attrib.preOpen)
        dataLine = {"tickType" : TickTypeEnum.to_str(tickType), 
                    "price"    : price, 
                    "isPreOpen": attrib.preOpen}
        self.file.put(dataLine)
        
    def openOrder(self,
                  orderId, 
                  contract, 
                  order, 
                  orderState) : 
        loc_order = {
            "PermId"   : order.permId, 
            "ClientId" : order.clientId, 
            "OrderId"  : orderId, 
            "Account"  : order.account, 
            "Symbol"   : contract.symbol, 
            "SecType"  : contract.secType, 
            "Exchange" : contract.exchange, 
            "Action"   : order.action, 
            "OrderType": order.orderType, 
            "TotalQty" : order.totalQuantity, 
            "CashQty"  : order.cashQty, 
            "LmtPrice" : order.lmtPrice, 
            "AuxPrice" : order.auxPrice, 
            "Status"   : orderState.status
            }
        if self.showLog : print ("Placed order")
        try : 
            self.file.put(loc_order)
        except : 
            pass 
                                        
        



class CLIENT(EClient) : 
    """! \private 
    IBKR Client class 
    """ 
    
    def __init__(self, wrapper) : 
        EClient.__init__(self, wrapper)
        
        self.showLog = False 
        self.reqId = 0 
        
    
    def start(self) : 
        self.thread = Thread(target = self.run) 
        self.thread.start()
    
        
    def serverTime(self) : 
        file = self.wrapper.init()
        self.reqCurrentTime()
        time = self.wrapper.get(file, timeout = 1)
        return time 
    
    def hstData(self, 
                contract, 
                endDateTime, 
                durationStr, 
                barSizeSetting, 
                whatToShow, 
                useRTH, 
                formatDate, 
                keepUpToDate, 
                chartOptions,
                timeQueue = 1) : 
        
        self.reqId += 1 
        file = self.wrapper.init()
        self.reqHistoricalData(self.reqId, 
                               contract, 
                               endDateTime, 
                               durationStr, 
                               barSizeSetting, 
                               whatToShow, 
                               useRTH, 
                               formatDate, 
                               keepUpToDate, 
                               chartOptions)
        time.sleep(timeQueue)
        hstData_ = self.wrapper.getList(file, timeout = 3)
        
        if len(hstData_) > 0 : 
            return hstData_
        else : 
            return False 
    
    def lastPrice(self,
                  contract, 
                  marketDataType, 
                  genericTickList, 
                  snapshot, 
                  regulatorySnapshot, 
                  mktDataOptions,
                  timeQueue = 1) : 
        
        self.reqId += 1 
        file = self.wrapper.init() 
        
        self.reqMarketDataType(marketDataType)
        self.reqMktData(self.reqId, 
                        contract, 
                        genericTickList, 
                        snapshot, 
                        regulatorySnapshot, 
                        mktDataOptions)
        
        time.sleep(timeQueue) 
        lastPrice_ = self.wrapper.getList(file, timeout = 3)
        
        if len(lastPrice_) > 0 : 
            return lastPrice_ 
        else : 
            return False 

    
    def placeOrder__(self, 
                    orderId, 
                    contract, 
                    order) : 
        file = self.wrapper.init()
        self.placeOrder(orderId, contract, order)
        time.sleep(1) 
        try : 
            placedOrder_ = self.wrapper.get(file, timeout = 3)
        except : 
            placedOrder_ = None 
        
        if placedOrder_ is not None : 
            return placedOrder_
        else : 
            return False 
    
    def cancelOrder_(self, 
                     orderId) : 
        self.cancelOrder(orderId)
    

        
        
        





class CLIENT_IBKR(WRAPPER, CLIENT) : 
    """! \private 
    IBKR Main client class 
    """ 
    

    def __init__(self) : 
        WRAPPER.__init__(self)
        CLIENT.__init__(self, wrapper=self)
        self.host      = None 
        self.portid    = None 
        self.client_id = None
        
        self.nextValidOrderId = None  
        
    #==================================
    # Low level functions 
    #==================================
    def getNextValidOrderId(self) : 
        self.nextValidOrderId = self.wrapper.nextValidOrderId 
        self.wrapper.nextValidOrderId += 1 
        return self.nextValidOrderId
        
    def connection(self,
                   host      = "127.0.0.1", 
                   portid    = 7497, 
                   client_id = 0) : 
        
        # Connection to the local server 
        self.host       = host 
        self.portid     = portid 
        self.client_id  = client_id
        
        try : 
            self.connect(self.host, self.portid, self.client_id)
            self.start() 
            time.sleep(0.1)
            self.getNextValidOrderId()
            
            return True 
        except : 
            
            return False 
        
    def closePosition(self, 
                      contract, 
                      openOrder) : 
        
        openOrder.action = "SELL" if openOrder.action == "BUY" else "BUY" 
        openOrder.transmit = True 
        
        closedOrder = self.placeOrder_(contract, openOrder)
        
        return closedOrder
    
    def placeOrder_(self,
                    contract, 
                    order) :
        
        orderId = self.getNextValidOrderId()
        return self.placeOrder__(orderId, 
                                 contract, 
                                 order)
    
    
    #==================================
    # High level functions 
    #==================================
    def connection_(self, configFile) : 
        # Config File extraction 
        ipaddress = configFile.get("ip")
        portid    = configFile.get("port")
        clientid  = configFile.get("client")
        
        connect =  self.connection(host      = ipaddress, 
                                   portid    = portid, 
                                   client_id = clientid) 
        
        
        self.start() 
        time.sleep(1)
        return connect 
    
    def createContract(self, configFile) : 
        """ 
        Function that translate a dictionnary formatted contract into a 
        contract object as required by the api. 
        """
        contract = Contract() 
        for key in list(configFile.keys()) : 
            setattr(contract, key, configFile.get(key))
        return contract
    
    def createOrder(self, configFile) : 
        orderParent = Order()
        orderParent.orderId = self.getNextValidOrderId()
        
        # Order direction 
        if configFile.get("action") == "long" : 
            orderParent.action = "BUY" 
        if configFile.get("action") == "short" : 
            orderParent.action = "SELL" 
        
        # Order volume 
        orderParent.totalQuantity = configFile.get("volume")
        
        
        # Order type 
        if configFile.get("orderType") == "MKT" : 
            orderParent.orderType = "MKT" 
            orderParent.transmit  = False 
            
            takeProfitOrder = Order() 
            takeProfitOrder.orderId = self.getNextValidOrderId()#orderParent.orderId + 1 
            takeProfitOrder.action = "SELL" if orderParent.action == "BUY" else "BUY" 
            takeProfitOrder.orderType = "LMT" 
            takeProfitOrder.totalQuantity = configFile.get("volume")
            takeProfitOrder.lmtPrice = configFile.get("takeprofit") 
            takeProfitOrder.parentId = orderParent.orderId 
            takeProfitOrder.transmit = False 
            
            stoplossOrder = Order() 
            stoplossOrder.orderId = self.getNextValidOrderId()#orderParent.orderId + 2 
            stoplossOrder.action  = "SELL" if orderParent.action == "BUY" else "BUY" 
            stoplossOrder.orderType = "STP" 
            stoplossOrder.totalQuantity = configFile.get("volume")
            stoplossOrder.auxPrice = configFile.get("stoploss")
            stoplossOrder.parentId = orderParent.orderId  
            stoplossOrder.transmit = True 
            
            bracketOrder = [orderParent, takeProfitOrder, stoplossOrder]
            return bracketOrder 
        
    def placeOrderList(self, contractFile, orderList) : 
        # We generate the good contract 
        contract = self.createContract(contractFile) 
        
        for order in orderList : 
            self.placeOrder__(order.orderId, contract, order)
            
    def editLimitOrder(self, contractFile, order, newLimit) : 
        contract = self.createContract(contractFile) 
        
        if order.orderType == "LMT" : 
            order.lmtPrice = newLimit 
        if order.orderType == "STP" : 
            order.auxPrice = newLimit 
            
        self.placeOrder__(order.orderId, contract, order) 
        
    def cancelOrder__(self, order = None) : 
        """ 
        This function work but need to be adapted to brackets orders 
        """
        if order is not None: 
            self.cancelOrder(order.orderId) 
            
    def closePosition_(self, 
                       contractFile, 
                       order = None) : 
        
        contract = self.createContract(contractFile) 
        # print ("Order ID : ",self.getNextValidOrderId())
        order.orderId = self.getNextValidOrderId()
        return self.closePosition(contract, order)
    
    
    def getHistoricalData_(self, contractFile, dateIni, dateEnd, timeframe, onlyOpen = True, timeQueue = 5, maxTimeQueue = 30) : 
        """ 
        - Simulate the case onlyOpen = False even during days off 
        
        - Find a way to avoid the server responds nothing 
        """
        
        contract = self.createContract(contractFile)
        
        print("=================================")
        print ("Get Hst Data function : ")
        print("=================================")
        print ("Date ini : ", dateIni,", Date end : ",dateEnd,", timeframe : ",timeframe) 
        
        
        # Ticker ID 
        tickerId = 1 
        waiting_time = 1 
        
        if onlyOpen : 
            useRTH = 1 
        else : 
            useRTH = 0 
            
        formatDate = 1 
        keepUpToDate = False 
        
        # Timeframe transformation 
        barSizeSetting = None 
        timeframeList      = [-1, -5, -15, -30, 1, 2, 3, 5, 15, 30, 60, 1440]
        barSizeSettingList = ["1 sec", "5 secs", "15 secs", "30 secs", 
                              "1 min", "2 mins", "3 mins", "5 mins", "15 mins", "30 mins", "1 hour", "1 day"]
        maxDurationUnits   = [3600, 2880, 1920, 2880, 2880, 5040, 14400, 8640, 2880, 17520, 8760, 99999999999]

        locIndex = None
        for i in range(len(timeframeList)) : 
            if timeframe == timeframeList[i] : 
                locIndex = i 
        if locIndex is not None : 
            barSizeSetting = barSizeSettingList[locIndex] 
        else : 
            print ("Error. Timeframe not available")
            return 
        
        # Timelength transformation 
        timeLengthUnit  = ["Y", "M", "W", "D", "S"]
        timeLengthUnit_ = [dt.timedelta(days = 365), 
                           dt.timedelta(days = 31),
                           dt.timedelta(days = 7), 
                           dt.timedelta(days = 1),
                           dt.timedelta(seconds = 1)]
        
        
        if type(dateIni) != type(dateEnd) : 
            print ("Error. The initial date and the end date should have the same type") 
        elif type(dateIni) == int : 
            if timeframe > 0 : 
                time_end = dt.timedelta(minutes = 1)*timeframe*dateEnd
                time_ini = dt.timedelta(minutes = 1)*timeframe*dateIni
                
            if timeframe < 0 : 
                time_end = dt.timedelta(seconds = 1)*abs(timeframe)*dateEnd
                time_ini = dt.timedelta(seconds = 1)*abs(timeframe)*dateIni
                
            time_width = (time_ini - time_end)*1.5 # 1.5 = vacations rate 
            
            locIndex = 0
            while time_width % timeLengthUnit_[locIndex] != dt.timedelta(seconds = 0) : 
                locIndex += 1 
            
            locWidth = int(time_width/timeLengthUnit_[locIndex])+1 
            durationStr = str(locWidth)+" "+timeLengthUnit[locIndex]
            
            if locWidth > 86400 : 
                locWidth = int(time_width/timeLengthUnit_[locIndex-1])+1
                durationStr = str(locWidth)+" "+timeLengthUnit[locIndex-1]
            
                
            
            
        elif type(dateIni) == type(dt.datetime(2020, 1, 10, 10, 10)) : 
            
            time_end = dt.datetime.now() - dateEnd
            time_width = dateEnd - dateIni 
            
            locIndex = 0
            while time_width % timeLengthUnit_[locIndex] != dt.timedelta(seconds = 0) : 
                locIndex += 1 
            
            locWidth = int(time_width/timeLengthUnit_[locIndex]) +1
            durationStr = str(locWidth)+" "+timeLengthUnit[locIndex]
            
        if locWidth > maxDurationUnits[locIndex] : 
            print ("Error. Server cannot return ",locWidth," candles.")
        
        print ("loc width = ", locWidth)
        print ("time width = ",time_width)
        print ("time_end = ",time_end) 
        print ("durationStr = ",durationStr) 
        print ("barSizeSetting = ",barSizeSetting)
    
        print ("Getting ASK data : ")
        dataAsk = False 
        startTimeQueue = timeQueue
        while (not dataAsk) and (startTimeQueue < maxTimeQueue): 
            print ("\t timeQueue = ",startTimeQueue," seconds")
            dataAsk = self.hstData(contract, 
                                   (dt.datetime.now() - time_end).strftime("%Y%m%d %H:%M:%S"), 
                                   durationStr, 
                                   barSizeSetting, 
                                   "ASK", 
                                   useRTH, 
                                   formatDate, 
                                   keepUpToDate, 
                                   [], 
                                   timeQueue = startTimeQueue)
            startTimeQueue += 1 
        
        print ("Getting BID data : ")
        dataBid = False 
        startTimeQueue = int(startTimeQueue/2.)
        while not dataBid and (startTimeQueue < maxTimeQueue): 
            print ("\t timeQueue = ",startTimeQueue," seconds")
            dataBid = self.hstData(contract, 
                                   (dt.datetime.now() - time_end).strftime("%Y%m%d %H:%M:%S"), 
                                   durationStr, 
                                   barSizeSetting, 
                                   "BID", 
                                   useRTH, 
                                   formatDate, 
                                   keepUpToDate, 
                                   [], 
                                   timeQueue = startTimeQueue)
            startTimeQueue += 1 
        
        if type(dateEnd) == int :
            if dataAsk : dataAsk = dataAsk[-dateIni:]
            if dataBid : dataBid = dataBid[-dateIni:]
        
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
        

        if dataAsk and dataBid : 
            sizeAsk = len(dataAsk) 
            sizeBid = len(dataBid)
            if sizeAsk != sizeBid : 
                print ("Error. Ask hst data and Bid hst data have not the same lenght")
                return dataset
        
            for d in dataAsk : 
                
                dataset.get("askopen").append(d.get("Open"))
                dataset.get("askhigh").append(d.get("High"))
                dataset.get("asklow").append(d.get("Low"))
                dataset.get("askclose").append(d.get("Close"))     
                dataset.get("volume").append(min(0, d.get("Volume"))) 
                
                locTime = dt.datetime.strptime(d.get("Time"),'%Y%m%d  %H:%M:%S') if len(d.get("Time")) > 8 else dt.datetime.strptime(d.get("Time"),'%Y%m%d')
                
                dataset.get("date").append(locTime)
    
            for d in dataBid : 
                
                dataset.get("bidopen").append(d.get("Open"))
                dataset.get("bidhigh").append(d.get("High"))
                dataset.get("bidlow").append(d.get("Low"))
                dataset.get("bidclose").append(d.get("Close"))    
            
        
            # print (pd.DataFrame(dataset))
    
            return dataset 
        else : 
            return False 
    
    
    def getLastPrice_(self, contractFile, timeQueue = 1, maxTimeQueue = 10) : 
        
        contract = self.createContract(contractFile) 
        
        dataset = self.getHistoricalData_(contractFile, 
                                          2, 0, 
                                          1, 
                                          onlyOpen = True, 
                                          timeQueue=1, maxTimeQueue=10)
        
        
        
        #print (dataset)
        print("=================================")
        print ("Getting streaming data : ")
        print("=================================")
        
        data = False 
        startTimeQueue = timeQueue
        while not data and (startTimeQueue < maxTimeQueue): 
            print ("\t timeQueue = ",startTimeQueue," seconds")
            
            data = self.lastPrice(contract, 
                                  1, 
                                  "", 
                                  True, 
                                  False, 
                                  [],
                                  timeQueue = startTimeQueue)
            startTimeQueue += 1 
        
        if data and dataset : 
        
            askPrice = None 
            bidPrice = None 
            for i in range(len(data)) : 
                if data[i].get("tickType") == "ASK" : 
                    askPrice = data[i].get("price")
                if data[i].get("tickType") == "BID" : 
                    bidPrice = data[i].get("price")
            
            # marketState = "closed"
            # if dataset.get("date")[-1] > dt.datetime.now() - dt.timedelta(minutes = 2) : 
            #     marketState = "open"
            marketState = "closed" 
            if not data[0].get("isPreOpen") : 
                marketState = "open"
            
            
            
            lastPrice = dict() 
            for key in list(dataset.keys()) : 
                try : 
                    lastPrice.update({key : dataset.get(key)[-1]})
                except : 
                    print ("No "+str(key)+" available in instant data price")
                    pass 
            
            
            lastPrice.update({
                "askprice"     : askPrice, 
                "bidprice"     : bidPrice, 
                "market state" : marketState 
                })
            
            # print (lastPrice)
            
            return lastPrice 
        
        else : 
            
            return False 
        
    
        






    
    
        
    