#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 07:18:44 2021

@author: loann
"""


###############################################################################
# MODULE IMPORTATIONS 
###############################################################################
# Standard imports 
import pprint 
import datetime
import queue
import time 
import threading
import socket
# Imports from the folder : ibapi
from quanTrade.mbapi.ibapi.client import EClient
from quanTrade.mbapi.ibapi.wrapper import EWrapper
from quanTrade.mbapi.ibapi.contract import Contract 
from quanTrade.mbapi.ibapi.order import Order 
from quanTrade.mbapi.ibapi.ticktype import TickTypeEnum
from quanTrade.mbapi.ibapi.execution import ExecutionFilter
# Imports from the current library
import quanTrade.mbapi.utils as utils

###############################################################################
# IBAPI CLASS WRAPPER
###############################################################################
class IBAPIWrapper(EWrapper):
    """
    A derived subclass of the IB API EWrapper interface
    that allows more straightforward response processing
    from the IB Gateway or an instance of TWS.
    """
    ###########################################################################
    def init_error(self):
        """
        Place all of the error messages from IB into a
        Python queue, which can be accessed elsewhere.
        """
        error_queue = queue.Queue()
        self._errors = error_queue
        

    def is_error(self):
        """
        Check the error queue for the presence
        of errors.

        Returns
        -------
        `boolean`
            Whether the error queue is not empty
        """
        return not self._errors.empty()

    def get_error(self, timeout=5):
        """
        Attempts to retrieve an error from the error queue,
        otherwise returns None.

        Parameters
        ----------
        timeout : `float`
            Time-out after this many seconds.

        Returns
        -------
        `str` or None
            A potential error message from the error queue.
        """
        if self.is_error():
            try:
                return self._errors.get(timeout=timeout)
            except queue.Empty:
                return None
        return None

    def error(self, id, errorCode, errorString):
        """
        Format the error message with appropriate codes and
        place the error string onto the error queue.
        """
        error_message = (
            "IB Error ID (%d), Error Code (%d) with "
            "response '%s'" % (id, errorCode, errorString)
        )

        self._errors.put(error_message)
        
    ###########################################################################
    def init_time(self):
        """
        Instantiates a new queue to store the server
        time, assigning it to a 'private' instance
        variable and also returning it.

        Returns
        -------
        `Queue`
            The time queue instance.
        """
        time_queue = queue.Queue()
        self._time_queue = time_queue
        return time_queue
    
    def currentTime(self, server_time):
        """
        Takes the time received by the server and
        appends it to the class instance time queue.

        Parameters
        ----------
        server_time : `str`
            The server time message.
        """
        self._time_queue.put(server_time)
        
    ###########################################################################
    def init_streaming(self) : 
        streaming_queue = queue.Queue() 
        self._streaming_queue = streaming_queue 
        return streaming_queue
        
        
    def tickPrice(self, reqId, tickType, price, attrib) : 
        # print ("Tick Price. Ticker Id:", reqId, "tickType:", TickTypeEnum.to_str(tickType), "Price:", price, end = " ")
        # if tickType == 4 : # 4 : Last price, if we're running during the market day
        #     print('The current price is :', price)
        # elif tickType == 9 : # 9 : Close price, if we're running after the market hours
        #     print('The last price is :', price)
        rdict = {
            "Ticker Id" : reqId, 
            "tickType"  : TickTypeEnum.to_str(tickType), 
            "Price"     : price
            }
        # print (rdict)
        self._streaming_queue.put(rdict)
            # print (self._streaming_queue)
        
    def tickSize(self, reqId, tickType, size) : 
        # print ("Tick Size. Ticker Id:", reqId, "tickType:", TickTypeEnum.to_str(tickType), "Size:", size) 
        pass 
    
    ###########################################################################
    def init_historical(self) : 
        print ("init queue")
        historical_queue = queue.Queue()
        self._historical_queue = historical_queue 
        return historical_queue
    
    def historicalData(self, reqId:int, bar):
        """
        See : http://interactivebrokers.github.io/tws-api/classIBApi_1_1Bar.html 
        and : http://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#ac943e5b81f6de111ddf71a1f05ab6282

        """
        
        rdict = {
            "reqId" : reqId, 
            "Time"  : bar.date, 
            "Open"  : bar.open, 
            "High"  : bar.high, 
            "Low"   : bar.low, 
            "Close" : bar.close, 
            "Volume": bar.volume, 
            "Count" : bar.barCount # The number of trades during the bar's timespan
            }
        self._historical_queue.put(rdict)
    
            
    ###########################################################################
    def init_symbolSamples(self) : 
        print ("init queue")
        symbolSample_queue = queue.Queue()
        self._symbolSample_queue = symbolSample_queue 
        return symbolSample_queue
    
    
    def symbolSamples(self, 
                      reqId, 
                      contractDescriptions) : 
        """
        See : http://interactivebrokers.github.io/tws-api/matching_symbols.html

        Parameters
        ----------
        reqId : TYPE
            DESCRIPTION.
        contractDescriptions : TYPE
            DESCRIPTION.

        Returns
        -------
        !!! WARNINGS !!! 
        The reqMatchingSymbol function does not return anything. The problem does not come from the Quamtums 
        trader API but the IBKR TWS APi side. Let's wait they solve the problem. 
        See : https://groups.io/g/twsapi/topic/reqmatchingsymbols_not/76670689?p=

        """

        contracts = []
        for contractDescription in contractDescriptions : 
            derivSecTypes = "" 
            for derivSecType in contractDescription.derivativeSecTypes : 
                derivSecTypes += derivSecType 
                derivSecTypes += " " 
            loc_contract = {"condId" : contractDescription.contract.conId, 
                            "symbol" : contractDescription.contract.symbol, 
                            "secType": contractDescription.contract.secType, 
                            "primaryExchange" : contractDescription.contract.primaryExchange, 
                            "currency" : contractDescription.contract.currency, 
                            "derivSecTypes" : derivSecTypes}
            contracts.append(loc_contract)
        pprint.pprint(contracts)
        self._symbolSample_queue.put(contracts)
        
    ###########################################################################
    def init_managedAccounts(self) : 
        print("init queue") 
        managedAccounts_queue = queue.Queue() 
        self._managedAccounts_queue = managedAccounts_queue 
        return managedAccounts_queue 
    
    def managedAccounts(self, accountsList) : 
        """
        See : http://interactivebrokers.github.io/tws-api/managed_accounts.html

        Parameters
        ----------
        accountsList : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        print ("Account list : ", accountsList)
        accountsList = accountsList.split(",")
        try : 
            self._managedAccounts_queue.put(accountsList)
        except : 
            pass 
    
    ###########################################################################
    def init_accountSummary(self) : 
        print ("init queue")
        accountsSummary_queue = queue.Queue() 
        self._accountsSummary_queue = accountsSummary_queue 
        return accountsSummary_queue 
        

    def accountSummary(self, 
                        reqId, 
                        account, 
                        tag, 
                        value, 
                        currency) : 

        """
        See : http://interactivebrokers.github.io/tws-api/account_summary.html

        Returns
        -------
        None.

        """
        # print ("Account Summary. ReqId :",reqId,", Account :",account,", Tag :",tag,", Value :",value,", Currency :",currency)
        loc_summary = {"ReqId"   : reqId, 
                       "Account" : account, 
                       "Tag"     : tag, 
                       "Value"   : value, 
                       "Currency": currency} 
        self._accountsSummary_queue.put(loc_summary) 
        
        ###########################################################################
    def init_nextValidId(self) : 
        print ("init queue")
        nextValidId_queue = queue.Queue()
        self._nextValidId_queue = nextValidId_queue 
        return nextValidId_queue
        
    def nextValidId(self, 
                    orderId) : 
        """
        Next order valid ID callback. This function is called when using the client 
        function self.simplePlaceOid
        See : http://interactivebrokers.github.io/tws-api/order_submission.html

        Parameters
        ----------
        orderId : TYPE
            DESCRIPTION.

        Returns
        -------^
        None.

        """
        # logging.debug("setting nextValidOrderId: %d", orderId)
        self.nextValidOrderId = orderId 
        print("NextValidId : ", orderId)
        
        try : 
            self._nextValidId_queue.put(orderId) 
        except :
            pass 
        
        

    def init_openOrder(self) : 
        print ("init queue")
        openOrder_queue = queue.Queue()
        self._openOrder_queue = openOrder_queue
        return openOrder_queue
    
    def openOrder(self,
                  orderId, 
                  contract, 
                  order, 
                  orderState) : 
        """
        Open order callback. This function is called when using the client function 
        self.placeOrder(...)

        Parameters
        ----------
        orderId : TYPE
            DESCRIPTION.
        contract : TYPE
            DESCRIPTION.
        order : TYPE
            DESCRIPTION.
        orderState : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
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
        
        # pprint.pprint(loc_order)
        try : 
            self._openOrder_queue.put(loc_order)
        except : pass 
        
    def init_orderStatus(self) : 
        print ("init queue")
        orderStatus_queue = queue.Queue()
        self._orderStatus_queue = orderStatus_queue
        return orderStatus_queue
        
    def orderStatus(self, 
                    orderId, 
                    status, 
                    filled, 
                    remaining, 
                    avgFillPrice, 
                    permId, 
                    parentId, 
                    lastFillPrice,
                    clientId, 
                    whyHeld, 
                    mktCapPrice) : 
        loc_order = {
            "Id"            : orderId, 
            "Status"        : status, 
            "Filled"        : filled, 
            "Remaining"     : remaining, 
            "AvgFillPrice"  : avgFillPrice, 
            "PermId"        : permId, 
            "ParentId"      : parentId, 
            "LastFillPrice" : lastFillPrice, 
            "ClientId"      : clientId, 
            "WhyHeld"       : whyHeld, 
            "MktCapPrice"   : mktCapPrice
            }
        
        # pprint.pprint(loc_order)
        try : 
            self._orderStatus_queue.put(loc_order)
        except : 
            pass 
        
        
        
    def init_position(self) : 
        position_queue = queue.Queue()
        self._position_queue = position_queue
        return position_queue
        
        
    def position(self, 
                  account, 
                  contract, 
                  pos, 
                  avgCost) :
        # super().position(account, contract, pos, avgCost)
        # print ("Position. Account :", account, " Symbol : ", contract.symbol, " SecType: ", contract.secType,
        #        "Contract ID: ", contract.conId,
        #         "Currency: ", contract.currency, " Position : ", pos, "Avg cost :", avgCost)
        if pos > 0 : 
            action = "BUY" 
        elif pos < 0 : 
            action = "SELL"
        else : 
            action = None
        loc_dict = {
            "Account" : account, 
            "Symbol"  : contract.symbol, 
            "SecType" : contract.secType, 
            "ConId"   : contract.conId, 
            "Currency": contract.currency, 
            "Exchange": contract.exchange,
            "Action"  : action,
            "Position": pos, 
            "AvgCost" : avgCost, 
            "Contract": contract
            }
        # pprint.pprint(loc_dict)
        try : 
            self._position_queue.put(loc_dict)
        except : 
            pass 
        
    def init_PnLSingle(self) : 
        pnlSingle_queue = queue.Queue()
        self._pnlSingle_queue = pnlSingle_queue
        return pnlSingle_queue
        
    def pnlSingle(self, 
                  reqId, 
                  pos, 
                  dailyPnL, 
                  unrealizedPnL, 
                  realizedPnL,
                  value) : 
        if abs(realizedPnL) > 1e300 : 
            realizedPnL = None
        loc_dict = {
            "reqId" : reqId, 
            "pos"   : pos,
            "dailyPnL" : dailyPnL, 
            "unrealizedPnL" : unrealizedPnL, # Profit that you can potentially do if you invert the position now
            "realizedPnL" : realizedPnL,     # Profit that you have done if you yet inverted a part of the position
            "value" : value
            }
        # pprint.pprint(loc_dict)
        try : 
            self._pnlSingle_queue.put(loc_dict)
        except : 
            pass 

    def pnl(self, 
            reqId, 
            dailyPnL, 
            unrealizedPnL, 
            realizedPnL) : 
        loc_dict = {
            "reqId" : reqId, 
            "dailyPnL" : dailyPnL, 
            "unrealizedPnL" : unrealizedPnL, 
            "realizedPnL" : realizedPnL
            }
    
    
    
    def init_execDetails(self) : 
        execDetails_queue = queue.Queue()
        self._execDetails_queue = execDetails_queue 
        return execDetails_queue
    
    
    def execDetails(self, 
                    reqId, 
                    contract, 
                    execution) : 

        loc_dict = {
            "Symbol"       : contract.symbol, 
            "SecType"      : contract.secType, 
            "Currency"     : contract.currency, 
            "ConId"        : contract.conId,
            "Execution ID" : execution.execId, 
            "Account"      : execution.acctNumber, 
            "Exchange"     : execution.exchange, 
            "Shares"       : execution.shares, 
            "Cumulated Qty": execution.cumQty, 
            "Price"        : execution.price, 
            "Average Price": execution.avgPrice,
            "Date"         : execution.time,
            "Reference"    : execution.orderRef 
            }
        # pprint.pprint(loc_dict)
        
        try : 
            self._execDetails_queue.put(loc_dict)
        except : 
            pass 
        
    def init_commissionReport(self) : 
        commissionReport_queue = queue.Queue() 
        self._commissionReport_queue = commissionReport_queue 
        return commissionReport_queue 
    
    def commissionReport(self, 
                         commissionReport) : 
        loc_dict = {
            "Execution ID" : commissionReport.execId, 
            "Commission"   : commissionReport.commission, 
            "Currency"     : commissionReport.currency, 
            "Realized P&L" : commissionReport.realizedPNL 
            }
        # pprint.pprint(loc_dict)
        
        try : 
            self._commissionReport_queue.put(loc_dict)
        except : 
            pass 

###############################################################################
# IBAPI CLASS CLIENT
###############################################################################
class IBAPIClient(EClient):
    """
    Used to send messages to the IB servers via the API. In this
    simple derived subclass of EClient we provide a method called
    obtain_server_time to carry out a 'sanity check' for connection
    testing.

    Parameters
    ----------
    wrapper : `EWrapper` derived subclass
        Used to handle the responses sent from IB servers
    """

    MAX_WAIT_TIME_SECONDS = 10

    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)
        
    ###########################################################################
    def obtain_server_time(self):
        """
        Requests the current server time from IB then
        returns it if available.

        Returns
        -------
        `int`
            The server unix timestamp.
        """
        # Instantiate a queue to store the server time
        time_queue = self.wrapper.init_time()

        # Ask IB for the server time using the EClient method
        self.reqCurrentTime()

        # Try to obtain the latest server time if it exists
        # in the queue, otherwise issue a warning
        try:
            server_time = time_queue.get(
                timeout=IBAPIClient.MAX_WAIT_TIME_SECONDS
            )
        except queue.Empty:
            print(
                "Time queue was empty or exceeded maximum timeout of "
                "%d seconds" % IBAPIClient.MAX_WAIT_TIME_SECONDS
            )
            server_time = None

        # Output all additional errors, if they exist
        while self.wrapper.is_error():
            print(self.get_error())

        return server_time
    
    ###########################################################################
    def obtain_streaming_data(self, contract, MarketDatatype = 1, reqId = 1, genericTickList = "",
                              snapshot = True, regulatorySnapshot = False, mktDataOptions = [], 
                              wait_time = 1) : 
        
        streaming_queue = self.wrapper.init_streaming() 
        
        self.wrapper.reqMarketDataType(MarketDatatype) # Switch to live (1) frozen (2) delayed (3) delayed frozen (4).
        self.wrapper.reqMktData(reqId, contract, genericTickList, snapshot , regulatorySnapshot, mktDataOptions)
        
        time.sleep(wait_time)
        streaming_price = []
        # print ("SIZE = ",streaming_queue.qsize())
        try : 
            
            while (streaming_queue.qsize() > 0) : 
                streaming_price.append(streaming_queue.get(
                    timeout=IBAPIClient.MAX_WAIT_TIME_SECONDS
                    ))
            streaming_queue.queue.clear()
            
        except queue.Empty: 
            print(
                "Time queue was empty or exceeded maximum timeout of "
                "%d seconds" % IBAPIClient.MAX_WAIT_TIME_SECONDS
                )
            streaming_price = None
            
        # Output all additional errors, if they exist
        while self.wrapper.is_error():
            print(self.get_error())
        
        if len(streaming_price) > 0 : 
            return streaming_price
        else : 
            return None 
    
    ###########################################################################
    def obtain_historical_data(self, contract, 
                               time_end = datetime.timedelta(minutes = 1), 
                               tickerId = 1, 
                               durationStr = "10 D", 
                               barSizeSetting = "1 hour", 
                               whatToShow = "ASK", 
                               useRTH = 0, 
                               formatDate = 1, 
                               keepUpToDate = False, 
                               chartOptions = [], 
                               waiting_time = 5) : 
        """
        See : http://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#aad87a15294377608e59aec1d87420594

        Parameters
        ----------
        contract : TYPE
            DESCRIPTION.
        time_end : TYPE, optional
            DESCRIPTION. The default is datetime.timedelta(minutes = 1).
        tickerId : TYPE, optional
            DESCRIPTION. The default is 1.
        durationStr : TYPE, optional
            DESCRIPTION. The default is "10 D".
        barSizeSetting : TYPE, optional
            DESCRIPTION. The default is "1 hour".
        whatToShow : TYPE, optional
            DESCRIPTION. The default is "ASK".
        useRTH : TYPE, optional
            DESCRIPTION. The default is 0.
        formatDate : TYPE, optional
            DESCRIPTION. The default is 1.
        keepUpToDate : TYPE, optional
            DESCRIPTION. The default is False.
        chartOptions : TYPE, optional
            DESCRIPTION. The default is [].
        waiting_time : TYPE, optional
            DESCRIPTION. The default is 5.

        Returns
        -------
        historical_price : TYPE
            DESCRIPTION.

        """
        
        historical_queue = self.wrapper.init_historical() 
        
        queryTime = (datetime.datetime.today() - time_end).strftime("%Y%m%d %H:%M:%S")
        self.wrapper.reqHistoricalData(tickerId, 
                                       contract, 
                                       queryTime, 
                                       durationStr, 
                                       barSizeSetting, 
                                       whatToShow, 
                                       useRTH, 
                                       formatDate, 
                                       keepUpToDate, 
                                       chartOptions)
        time.sleep(waiting_time)

        historical_price = []
        try : 
            while(historical_queue.qsize() > 0) : 
                historical_price.append(
                    historical_queue.get(timeout=IBAPIClient.MAX_WAIT_TIME_SECONDS)
                    )
            historical_queue.queue.clear()
        except queue.Empty: 
            print(
                "Time queue was empty or exceeded maximum timeout of "
                "%d seconds" % IBAPIClient.MAX_WAIT_TIME_SECONDS
                )
            
        # Output all additional errors, if they exist
        while self.wrapper.is_error():
            print(self.get_error())
            
        self.wrapper.cancelHistoricalData(tickerId)
        return historical_price
    
    ###########################################################################
    def obtain_symbolSamples(self, symbolPiece, reqId = 1, waiting_time = 5) : 
        symbolSample_queue = self.wrapper.init_symbolSamples() 
        
        self.wrapper.reqMatchingSymbols(reqId, symbolPiece) 
        time.sleep(waiting_time) 
        
        symbols_list = []
        print(symbolSample_queue.qsize())
        try : 
            symbols_list = symbolSample_queue.get(
                timeout = IBAPIClient.MAX_WAIT_TIME_SECONDS
                )
            symbolSample_queue.queue.clear() 
        except queue.Empty: 
            print(
                "Time queue was empty or exceeded maximum timeout of "
                "%d seconds" % IBAPIClient.MAX_WAIT_TIME_SECONDS
                )
        # Output all additional errors, if they exist
        while self.wrapper.is_error():
            print(self.get_error())
            
        return symbols_list
    
    ###########################################################################
    def obtain_accountsList(self, waiting_time = 1) : 
        managedAccounts_queue = self.wrapper.init_managedAccounts() 
        
        self.wrapper.reqManagedAccts() 
        time.sleep(waiting_time) 
        
        managedAccounts_list = [] 
        try : 
            managedAccounts_list = managedAccounts_queue.get(
                timeout = IBAPIClient.MAX_WAIT_TIME_SECONDS
                )
            managedAccounts_queue.queue.clear() 
        except queue.Empty: 
            print(
                "Time queue was empty or exceeded maximum timeout of "
                "%d seconds" % IBAPIClient.MAX_WAIT_TIME_SECONDS
                )
        # Output all additional errors, if they exist
        while self.wrapper.is_error():
            print(self.get_error())
            
        return managedAccounts_list
    
    ###########################################################################
    def obtain_accountsSummary(self, 
                               waiting_time = 3, 
                               reqId = 1, 
                               group = "All", 
                               tags = "$LEDGER") : 
        """
        See : http://interactivebrokers.github.io/tws-api/account_summary.html#acct_summary_req

        """
        accountsSummary_queue = self.wrapper.init_accountSummary() 
        
        self.wrapper.reqAccountSummary(reqId, 
                                       group, 
                                       tags)
        time.sleep(waiting_time) 
        
        accountSummary_list = [] 
        try : 
            while(accountsSummary_queue.qsize() > 0) : 
                accountSummary_list.append(
                    accountsSummary_queue.get(timeout=IBAPIClient.MAX_WAIT_TIME_SECONDS)
                    )
            accountsSummary_queue.queue.clear()
        except queue.Empty: 
            print(
                "Time queue was empty or exceeded maximum timeout of "
                "%d seconds" % IBAPIClient.MAX_WAIT_TIME_SECONDS
                )
        # Output all additional errors, if they exist
        while self.wrapper.is_error():
            print(self.get_error())
            
        
        self.wrapper.cancelAccountSummary(reqId)
        
        return accountSummary_list
    
    ###########################################################################
    def getNextValidOrderId(self) : 
        nextValidOrderId = self.wrapper.nextValidOrderId + 1 
        return nextValidOrderId
    
    def pass_Order(self, nextValidOrderId, contract, order, waiting_time = 1) : 
        

        openOrder_queue = self.wrapper.init_openOrder()
        # nextValidOrderId = self.wrapper.nextValidOrderId +1 
        # self.wrapper.nextValidOrderId  = nextValidOrderId

        
        passed_order = None 
        if (nextValidOrderId) : 
            self.placeOrder(nextValidOrderId, contract, order)
            
            if (order.transmit) : 
                time.sleep(waiting_time)
                
                try : 
                    passed_order = openOrder_queue.get(timeout = IBAPIClient.MAX_WAIT_TIME_SECONDS) 
                    openOrder_queue.queue.clear()
                except queue.Empty: 
                    print(
                        "Time queue was empty or exceeded maximum timeout of "
                        "%d seconds" % IBAPIClient.MAX_WAIT_TIME_SECONDS
                        )
                # Output all additional errors, if they exist
                while self.wrapper.is_error():
                    print(self.get_error())
            
        
        return passed_order 
    
    ###########################################################################
    def obtain_Orders(self, which = "AllOpenOrders", waiting_time = 1) : 
        
        openOrder_queue = self.wrapper.init_openOrder() 
        statusOrder_queue = self.wrapper.init_orderStatus() 
        
        if which == "ClientOpenOrders" : 
            self.reqOpenOrders() 
        elif which == "AllOpenOrders"  : 
            self.reqAllOpenOrders() 
        elif which == "ManualOpenOrders" : 
            self.reqAutoOpenOrders() 
        
        time.sleep(waiting_time)
        
        passedOrders_list = [] 
        ordersStatus_list = [] 
        try : 
            while(openOrder_queue.qsize() > 0 and statusOrder_queue.qsize() > 0) : 
                passedOrders_list.append(
                    openOrder_queue.get(timeout = IBAPIClient.MAX_WAIT_TIME_SECONDS)
                    )
                ordersStatus_list.append(
                    statusOrder_queue.get(timeout = IBAPIClient.MAX_WAIT_TIME_SECONDS)
                    )
            
        except queue.Empty: 
            print (
                "Status Orders and/or Passed Orders queue are either both empty nor have the "
                "same length "
                )
        # Output all additional errors, if they exist
        while self.wrapper.is_error():
            print(self.get_error())
            
        orders_list = [] 
        for i in range(len(passedOrders_list)) : 
            loc_order = {"Order" : passedOrders_list[i], "State" : ordersStatus_list[i]} 
            orders_list.append(loc_order)
        
        return orders_list 
    
    ###########################################################################
    def obtain_Positions(self, hide_null = True, waiting_time_1 = 1, waiting_time_2 = 0.2) : 
        """
        

        Parameters
        ----------
        hide_null : TYPE, optional
            This parameter allows to hide all null positions. The default is True.
        waiting_time_1 : TYPE, optional
            DESCRIPTION. The default is 1.
        waiting_time_2 : TYPE, optional
            DESCRIPTION. The default is 0.2.

        Returns
        -------
        None.

        """
        
        position_queue = self.wrapper.init_position()
        
        
        self.reqPositions() 
        time.sleep(waiting_time_1)
        
        positions_list = [] 
        try : 
            while(position_queue.qsize() > 0) : 
                positions_list.append(
                    position_queue.get(timeout = IBAPIClient.MAX_WAIT_TIME_SECONDS)
                    )
        except queue.Empty : 
            print(
                "Time queue was empty or exceeded maximum timeout of "
                "%d seconds" % IBAPIClient.MAX_WAIT_TIME_SECONDS
                )
        # Output all additional errors, if they exist
        while self.wrapper.is_error():
            print(self.get_error())
            
            
        infos_list      = []
        execution_list  = [] 
        commission_list = []
        if len(positions_list) > 0 : 
            for i in range(len(positions_list)) : 
                pnlSingle_queue        = self.wrapper.init_PnLSingle()
                execDetails_queue      = self.wrapper.init_execDetails()
                commissionReport_queue = self.wrapper.init_commissionReport()
                
                reqId = i+1
                loc_account = positions_list[i].get("Account") 
                contract_ID = positions_list[i].get("ConId")
                
                # We create the execution filter to retrieve infos about the 
                # execution of each position 
                executionFilter = ExecutionFilter() 
                executionFilter.acctCode = loc_account 
                executionFilter.symbol = positions_list[i].get("Symbol")
                executionFilter.secType = positions_list[i].get("SecType")
                executionFilter.exchange = positions_list[i].get("Exchange")
                
        # loc_dict = {
        #     "Account" : account, 
        #     "Symbol"  : contract.symbol, 
        #     "SecType" : contract.secType, 
        #     "ConId"   : contract.conId, 
        #     "Currency": contract.currency, 
        #     "Exchange": contract.exchange,
        #     "Action"  : action,
        #     "Position": pos, 
        #     "AvgCost" : avgCost, 
        #     "Contract": contract
        #     }
                # First we retrive the PnL status of the position 
                self.reqPnLSingle(reqId, loc_account, "", contract_ID)
                time.sleep(waiting_time_2)
                self.cancelPnLSingle(reqId)
                
                try : 
                    infos_list.append(pnlSingle_queue.get(timeout = IBAPIClient.MAX_WAIT_TIME_SECONDS))
                except queue.Empty : 
                    print(
                        "Time queue was empty or exceeded maximum timeout of "
                        "%d seconds" % IBAPIClient.MAX_WAIT_TIME_SECONDS
                        )
                
                # Second we retrieve the execution filter status of the position 
                self.reqExecutions(reqId, executionFilter) 
                time.sleep(waiting_time_2)
                
                loc_execution_list  = []
                try : 
                    while(execDetails_queue.qsize() > 0) : 
                        loc_execution_list.append(
                            execDetails_queue.get(timeout = IBAPIClient.MAX_WAIT_TIME_SECONDS)
                            )
                except queue.Empty : 
                    print(
                        "Time queue was empty or exceeded maximum timeout of "
                        "%d seconds" % IBAPIClient.MAX_WAIT_TIME_SECONDS
                        )
                execution_list.append(loc_execution_list)
                    
                
                
                loc_commission_list = []
                try : 
                    while(commissionReport_queue.qsize() > 0) : 
                        loc_commission_list.append(
                            commissionReport_queue.get(timeout = IBAPIClient.MAX_WAIT_TIME_SECONDS)
                            )
                except queue.Empty : 
                    print(
                        "Time queue was empty or exceeded maximum timeout of "
                        "%d seconds" % IBAPIClient.MAX_WAIT_TIME_SECONDS
                        )
                commission_list.append(loc_commission_list)
                
                
                # Output all additional errors, if they exist
                while self.wrapper.is_error():
                    print(self.get_error())
        
        print (len(execution_list), len(commission_list))
        print(len(positions_list), len(infos_list))
        positions = [] 
        for i in range(len(infos_list)) : 
            loc_position = {"Position" : positions_list[i], "P&L" : infos_list[i], 
                            "Execution": execution_list[i], "Commission" : commission_list[i]}
            if hide_null : 
                if loc_position.get("Position").get("Position") != 0 : 
                    positions.append(loc_position)
            else : 
                positions.append(loc_position)
            
        
        # pprint.pprint(positions_list)
        # pprint.pprint(infos_list)
        #pprint.pprint(positions)
                
        return positions 
    
    ###########################################################################
    def invert_position(self, 
                        account, 
                        contractId, 
                        contract,
                        orderType = "MKT",
                        percentage = 100., 
                        order = None) : 
        """
        Note : Here it is impossible to retrieve the contract object from self.obtain_Positions() because the 
        server forget to return some important contract properties such as the exchange. The best is to input the 
        contract object in the function. 

        Parameters
        ----------
        account : string
            Account name. The default is None.
        contractId : TYPE, optional
            DESCRIPTION. The default is None.
        percentage : TYPE, optional
            DESCRIPTION. The default is 100..

        Returns
        -------
        None.

        """
        openOrder_queue = self.wrapper.init_openOrder()
        
        # We retrieve the list of all non-null positions 
        # self.reqOpenOrders()
        positions_list = self.obtain_Positions()
        
        # We recude the data to the only position we want 
        position = None 
        for i in range(len(positions_list)) : 
            if (positions_list[i].get("Position").get("Account") == account and 
                positions_list[i].get("Position").get("ConId")   == contractId) : 
                position = positions_list[i]
        
        # We create a revert position 
        nextValidOrderId = self.wrapper.nextValidOrderId +1 
        self.wrapper.nextValidOrderId = nextValidOrderId

        
        passed_order = None
        if nextValidOrderId : 
            
            if position.get("Position").get("Action") == "BUY" : 
                action = "SELL"
            elif position.get("Position").get("Action") == "SELL" : 
                action = "BUY"
            
            if (not(order)) : 
                order = Order() 
                order.action = action 
                order.orderType = orderType
                
            order.totalQuantity = abs(position.get("Position").get("Position"))*(percentage/100.)
            
            self.placeOrder(nextValidOrderId, contract, order)
            
            try : 
                passed_order = openOrder_queue.get(timeout = IBAPIClient.MAX_WAIT_TIME_SECONDS) 
                openOrder_queue.queue.clear()
            except queue.Empty: 
                print(
                    "Time queue was empty or exceeded maximum timeout of "
                    "%d seconds" % IBAPIClient.MAX_WAIT_TIME_SECONDS
                    )
            # Output all additional errors, if they exist
            while self.wrapper.is_error():
                print(self.get_error())
        
        # pprint.pprint(positions_list)
        return passed_order
    
    
    
    
    
###############################################################################
# IBAPI CLASS CLIENT
###############################################################################
class CLIENT_IBKR(IBAPIWrapper, IBAPIClient):
    """
    The IB API application class creates the instances
    of IBAPIWrapper and IBAPIClient, through a multiple
    inheritance mechanism.

    When the class is initialised it connects to the IB
    server. At this stage multiple threads of execution
    are generated for the client and wrapper.

    Parameters
    ----------
    ipaddress : `str`
        The IP address of the TWS client/IB Gateway
    portid : `int`
        The port to connect to TWS/IB Gateway with
    clientid : `int`
        An (arbitrary) client ID, that must be a positive integer
    """

    def __init__(self) : 
        IBAPIWrapper.__init__(self)
        IBAPIClient.__init__(self, wrapper=self)
        self.host      = None 
        self.portid    = None 
        self.client_id = None

    def connection(self, 
                   configFile,
                   timeBetweenTwoConnectionTries = 10):
        """ 
        Connect to the socker server
        """
        # Config File extraction 
        ipaddress = configFile.get("ip")
        portid    = configFile.get("port")
        clientid  = configFile.get("client")

        # Connects to the IB server with the
        # appropriate connection parameters
        while not self.isConnected() : 
            try : 
                self.connect(ipaddress, portid, clientid)
            except : 
                print ("Failed connection, retrying ...")
                time.sleep(timeBetweenTwoConnectionTries)
                

        # Initialise the threads for various components
        thread = threading.Thread(target=self.run)
        thread.start()
        setattr(self, "_thread", thread)

        # Listen for the IB responses
        self.init_error()
        
        # Connection informations 
        self.host      = ipaddress 
        self.portid    = portid 
        self.client_id  = clientid
        
    def deconnection(self) : 
        """ 
        Disconnect from the scket server
        """ 
        self.disconnect() 
    
    def checkConnection(self) : 
        """
        Check the connection between the client and the local server. 
        Returns true is connected, else false

        """
        return self.isConnected()
    
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
            takeProfitOrder.orderId = orderParent.orderId + 1 
            takeProfitOrder.action = "SELL" if orderParent.action == "BUY" else "BUY" 
            takeProfitOrder.orderType = "LMT" 
            takeProfitOrder.totalQuantity = configFile.get("volume")
            takeProfitOrder.lmtPrice = configFile.get("takeprofit") 
            takeProfitOrder.parentId = orderParent.orderId 
            takeProfitOrder.transmit = False 
            
            stoplossOrder = Order() 
            stoplossOrder.orderId = orderParent.orderId + 2 
            stoplossOrder.action  = "SELL" if orderParent.action == "BUY" else "BUY" 
            stoplossOrder.orderType = "STP" 
            stoplossOrder.totalQuantity = configFile.get("volume")
            stoplossOrder.auxPrice = configFile.get("stoploss")
            stoplossOrder.parentId = orderParent.orderId  
            stoplossOrder.transmit = True 
            
            bracketOrder = [orderParent, takeProfitOrder, stoplossOrder]
            return bracketOrder 
    
    def placeOrder_(self, contractFile, orderList) : 
        # We generate the good contract 
        contract = self.createContract(contractFile) 
        #print (contract)
        
        for order in orderList : 
            #print ("Order ID : ", order.orderId) 
            #print ("Contract : ", contract)
            #print ("Order : ", order)
            self.placeOrder(order.orderId, contract, order)
            #orderResponse = self.pass_Order(order.orderId, contract, order)
            #print ("Order : ",orderResponse)
            self.nextValidOrderId += 1
    
    def editLimitOrder(self, contractFile, order, newLimit) : 
        contract = self.createContract(contractFile) 
        
        if order.orderType == "LMT" : 
            order.lmtPrice = newLimit 
        if order.orderType == "STP" : 
            order.auxPrice = newLimit 
        
        self.placeOrder(order.orderId, contract, order) 
    
    def cancelOrder_(self, order = None, option = None) : 
        """ 
        This function work but need to be adapted to brackets orders 
        """
        if (order is not None) and (option is None) : 
            self.cancelOrder(order.orderId) 
        if (order is None) and (type(option) == int) : 
            self.cancelOrder(self.nextValidOrderId - option) 
    
    def closePosition_(self, contractFile, order = None) : 
        """ 
        This function allows to close an open position. If only the contractFile is provided, 
        all the positition is closed. If an order that have been placed is provided, then 
        a symmetric order is placed. 
        """ 
        contract = self.createContract(contractFile) 

        if order is None : 
            # To be developped (here we have to close the whole position)
            positions = self.obtain_Positions(hide_null = True, waiting_time_1 = 1, waiting_time_2 = 0.2)
            #pprint.pprint(positions)

            positionIndex = None
            for i in range(len(positions)) : 
                thisPosition = True
                serverContract = positions[i].get("Position").get("Contract")
                for key in list(contractFile.keys()) : 
                    if (getattr(serverContract, key) is not None) and len(getattr(serverContract, key)) > 0 : 
                        #print ("local : (",key,", ",getattr(contract, key),"), distant : (",key,", ",getattr(serverContract, key),")")
                        if getattr(contract, key) != getattr(serverContract, key) : 
                            thisPosition = False
                if thisPosition : 
                    positionIndex = i 
            if positionIndex is not None : 
                totalQuantity = abs(positions[positionIndex].get("Position").get("Position"))
                action = "SELL" if positions[positionIndex].get("Position").get("Action") == "BUY" else "BUY"  

                closeOrder = Order() 
                closeOrder.orderId = self.getNextValidOrderId() 
                closeOrder.action = action 
                closeOrder.orderType = "MKT"
                closeOrder.totalQuantity = totalQuantity 

                self.placeOrder(closeOrder.orderId, contract, closeOrder)

        if order is not None : 
            if order.action == "BUY" : 
                order.action = "SELL" 
            elif order.action == "SELL" : 
                order.action = "BUY" 
            
            self.nextValidOrderId += 1
            order.orderId = self.nextValidOrderId
            order.transmit = True

            self.placeOrder(order.orderId, contract, order)
    
    

    def getHistoricalData_(self, contractFile, dateIni, dateEnd, timeframe, onlyOpen = True) : 
        """ 
        - Simulate the case onlyOpen = False even during days off 
        
        - Find a way to avoid the server responds nothing 
        """
        
        contract = self.createContract(contractFile)
        
        print ("Get Hst Data function : ")
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
        timeLengthUnit_ = [datetime.timedelta(days = 365), 
                           datetime.timedelta(days = 31),
                           datetime.timedelta(days = 7), 
                           datetime.timedelta(days = 1),
                           datetime.timedelta(seconds = 1)]
        
        
        if type(dateIni) != type(dateEnd) : 
            print ("Error. The initial date and the end date should have the same type") 
        elif type(dateIni) == int : 
            if timeframe > 0 : 
                time_end = datetime.timedelta(minutes = 1)*timeframe*dateEnd
                time_ini = datetime.timedelta(minutes = 1)*timeframe*dateIni
                
            if timeframe < 0 : 
                time_end = datetime.timedelta(seconds = 1)*abs(timeframe)*dateEnd
                time_ini = datetime.timedelta(seconds = 1)*abs(timeframe)*dateIni
                
            time_width = time_ini - time_end 
            
            locIndex = 0
            while time_width % timeLengthUnit_[locIndex] != datetime.timedelta(seconds = 0) : 
                locIndex += 1 
            
            locWidth = int(time_width/timeLengthUnit_[locIndex])+1 
            durationStr = str(locWidth)+" "+timeLengthUnit[locIndex]
            
            if locWidth > 86400 : 
                locWidth = int(time_width/timeLengthUnit_[locIndex-1])+1
                durationStr = str(locWidth)+" "+timeLengthUnit[locIndex-1]
            
                
            
            
        elif type(dateIni) == type(datetime.datetime(2020, 1, 10, 10, 10)) : 
            
            time_end = datetime.datetime.now() - dateEnd
            time_width = dateEnd - dateIni 
            
            locIndex = 0
            while time_width % timeLengthUnit_[locIndex] != datetime.timedelta(seconds = 0) : 
                locIndex += 1 
            
            locWidth = int(time_width/timeLengthUnit_[locIndex]) +1
            durationStr = str(locWidth)+" "+timeLengthUnit[locIndex]
            
            
        
        
        print ("time_end = ",time_end) 
        print ("durationStr = ",durationStr) 
        print ("barSizeSetting = ",barSizeSetting)
        
        
        dataAsk = self.obtain_historical_data(contract, 
                                              time_end       = time_end, 
                                              tickerId       = tickerId, 
                                              durationStr    = durationStr, 
                                              barSizeSetting = barSizeSetting, 
                                              whatToShow     = "ASK", 
                                              useRTH         = useRTH, 
                                              formatDate     = formatDate, 
                                              keepUpToDate   = keepUpToDate, 
                                              chartOptions   = [], 
                                              waiting_time   = waiting_time)
        
        dataBid = self.obtain_historical_data(contract, 
                                              time_end       = time_end, 
                                              tickerId       = tickerId, 
                                              durationStr    = durationStr, 
                                              barSizeSetting = barSizeSetting, 
                                              whatToShow     = "BID", 
                                              useRTH         = useRTH, 
                                              formatDate     = formatDate, 
                                              keepUpToDate   = keepUpToDate, 
                                              chartOptions   = [], 
                                              waiting_time   = waiting_time)
        
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
            
            locTime = datetime.datetime.strptime(d.get("Time"),'%Y%m%d  %H:%M:%S') if len(d.get("Time")) > 8 else datetime.datetime.strptime(d.get("Time"),'%Y%m%d')
            
            dataset.get("date").append(locTime)

        for d in dataBid : 
            
            dataset.get("bidopen").append(d.get("Open"))
            dataset.get("bidhigh").append(d.get("High"))
            dataset.get("bidlow").append(d.get("Low"))
            dataset.get("bidclose").append(d.get("Close"))    
            
        
        #print (dataAsk)
        #print (dataBid)
        
        return dataset 
    
    def getLastPrice_(self, contractFile) : 
        
        dataset = self.getHistoricalData_(contractFile, 10, 0, 1, onlyOpen = True)
        
        #print (dataset)
        
        contract = self.createContract(contractFile) 
        
        data = self.obtain_streaming_data(contract, 
                                          MarketDatatype = 1, 
                                          reqId = 3, 
                                          genericTickList = "",
                                          snapshot = True, 
                                          regulatorySnapshot = False, 
                                          mktDataOptions = [], 
                                          wait_time = 1)
        
        #print (data)
        
            # {"askopen" : float, 
            #  "askhigh" : float, 
            #  "asklow"  : float, 
            #  "askclose": float, 
            #  "askprice": float,
            #  "bidopen" : float, 
            #  "bidhigh" : float, 
            #  "bidlow"  : float, 
            #  "bidclose": float,
            #  "bidprice": float, 
            #  "date"    : datetime, 
            #  "volume"  : float, 
            #  "market state" : string ("open" or "closed") }
        
        askPrice = None 
        bidPrice = None 
        for i in range(len(data)) : 
            if data[i].get("tickType") == "ASK" : 
                askPrice = data[i].get("Price")
            if data[i].get("tickType") == "BID" : 
                bidPrice = data[i].get("Price")
        
        marketState = "closed"
        if dataset.get("date")[-1] > datetime.datetime.now() - datetime.timedelta(minutes = 2) : 
            marketState = "open"
        
        
        
        lastPrice = dict() 
        for key in list(dataset.keys()) : 
            try : 
                lastPrice.update({key : dataset.get("key")[-1]})
            except : 
                print ("No "+str(key)+" available in instant data price")
                pass 
        
        
        lastPrice.update({
            "askprice"     : askPrice, 
            "bidprice"     : bidPrice, 
            "market state" : marketState 
            })
        
        return lastPrice 

    
            
# obtain_streaming_data(self, contract, MarketDatatype = 1, reqId = 1, genericTickList = "",
#                               snapshot = True, regulatorySnapshot = False, mktDataOptions = [], 
#                               wait_time = 1)
        
        
    