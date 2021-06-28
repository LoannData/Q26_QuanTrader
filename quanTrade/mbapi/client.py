#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 15:24:37 2021

@author: loann
"""

import quanTrade.mbapi.utils as utils
import sys, os 


class CLIENT_MAIN : 
    
    def __init__(self, 
                 brokerName, 
                 accountNumber = 0) : 
        self.broker           = brokerName    # Broker Name
        self.refNumber        = accountNumber # Broker's reference number 
        self.api              = None # Broker's api object 
        self.contractsList    = {}   # List of the available contracts for the current instance
                                     # Here a contract is a contract object compatible with the broker api 
        
        # Local client initialisation 
        if self.broker == "IBKR" : 
            dirname  = os.path.dirname(__file__)
            filename = os.path.join(dirname,".")
            sys.path.append(filename)
            import quanTrade.mbapi.client_IBKR as client
            # IBKR API initialisation 
            self.api = client.CLIENT_IBKR()  
        
        return 
    
    #########################################################################################
    # CONNECTION METHODS 
    #########################################################################################
    def connect(self, 
                configFile = None) :
        """
        Function that connect the instance to the broker's API and 
        fill the associated api object. 
        Variables : 
            brokerName [str]  : Name of the broker to connect 
            configFile [dict] : Dictionnary that contains the broker's connection informations 
        """
        if self.broker == "IBKR" : 
            # Connection to the client API
            self.api.connection_(utils.getClientConnectionInfo(file = configFile, 
                                                               brokerName = self.broker, 
                                                               referenceNumber = self.refNumber))
        return 
    
    def checkConnection(self) : 
        """ 
        Function that check if the Broker's api object is connected to the broker. 
        """
        if self.broker == "IBKR" : 
            return self.api.checkConnection()
        return 
    
    def disconnect(self) : 
        """ 
        If connected, this function disconnect the broker's API object from the server. 
        """
        if self.broker == "IBKR" : 
            self.api.disconnect()
        return 
    
    #########################################################################################
    # CONTRACT DEFINITION METHODS
    #########################################################################################
    def newContract(self, 
                    contractName, 
                    configFile = None) : 
        """
        Function that allows to define a new contract object compatible with a selected 
        broker. 
        """
        if self.broker == "IBKR" : 
            self.contractsList[contractName] = utils.getContractInfo(file         = configFile, 
                                                                     brokerName   = self.broker, 
                                                                     contractName = contractName)
        return 
    
    def removeContract(self, 
                       contractName) : 
        """ 
        Function that allows to remove a contract existing in the contractsList object. 
        """
        if self.broker == "IBKR" : 
            del self.contractsList[contractName] 
    #########################################################################################
    # CONTRACT DATA METHODS 
    #########################################################################################
    def getHistoricalData(self, contractName, dateIni, dateEnd, timeframe, onlyOpen = True) : 
        """ 
        Function that returns an historical dataset for the selected contract. 
        """
        if self.broker == "IBKR" : 
            contract = self.contractsList.get(contractName)
            return self.api.getHistoricalData_(contract, dateIni, dateEnd, timeframe, onlyOpen = onlyOpen)
            
        return 
    
    def getLastPrice(self, contractName) : 
        """ 
        Function that returns the last existing price for the selected contract. 
        """
        if self.broker == "IBKR" : 
            contract = self.contractsList.get(contractName)
            return self.api.getLastPrice_(contract)
        return

    #########################################################################################
    # TRADING ORDER METHODS
    #########################################################################################
    def placeOrder(self, 
                   contractName,
                   action     = "long", # "long" or "short". 
                   orderType  = "bracket", # Order kind : "bracket" 
                   volume     = 0.1, # Volume of the asset to trade in the asset unit 
                   stoploss   = None, # Stoploss value
                   takeprofit = None, # Take profit value 
                   lmtPrice   = None, # Order executed if price reaches the lmtPrice 
                   auxPrice   = None) : 
        """
        Function that allows to place an order with a selected contract object, on a selected 
        broker.  
        This function returns a list of 3 orders (with respect to the following order): 
            - A market order 
            - The limit takeprofit order 
            - The stoploss order 
        """
        configFile = {
            "contract"  : self.contractsList.get(contractName), 
            "action"    : action, 
            "orderType" : orderType, 
            "volume"    : volume, 
            "stoploss"  : stoploss, 
            "takeprofit": takeprofit, 
            "lmtPrice"  : lmtPrice, 
            "auxPrice"  : auxPrice
            }

        if self.broker == "IBKR" : 
            orderList = self.api.createOrder(configFile) 
            self.api.placeOrderList(configFile.get("contract"), orderList)
        
        return orderList  
    
    def editSLOrder(self, 
                    contractName, 
                    order, 
                    stoploss = None) : 
        """ 
        Function that allows to edit the stoploss of a bracket order 
        """
        if stoploss is not None : 
            if self.broker == "IBKR" : 
                self.api.editLimitOrder(self.contractsList.get(contractName), order, stoploss)
                
    def editTPOrder(self, 
                    contractName, 
                    order, 
                    takeprofit = None) : 
        """ 
        Function that allows to edit the takeprofit of a bracket order 
        """
        if takeprofit is not None : 
            if self.broker == "IBKR" : 
                self.api.editLimitOrder(self.contractsList.get(contractName), order, takeprofit)
    
    def cancelOrder(self, 
                    contractName, 
                    order) : 
        """
        Function that allows to cancel an order that have been previously placed but not 
        executed yet on a given contract and to a given broker.  
        """
        if self.broker == "IBKR" : 
            self.api.cancelOrder__(order = order) 
        return
    
    def cancelLastOrder(self, n = 1) : 
        """  
        Function that cancel the last-n specific order. 
        """
        if self.broker == "IBKR" : 
            self.api.cancelOrder_(option = n) 
        return 
    
    def readPositions(self) : 
        """
        Function that returns the positions informations opened by the current client account.  
        """
        return 
    
    def closePosition(self, 
                      contractName, 
                      order = None) : 
        """ 
        Function that close a specific position on a given contract. 
        """
        if self.broker == "IBKR" : 
            self.api.closePosition_(self.contractsList.get(contractName), order = order)
        return 

    def closeAllPositions(self) : 
        """ 
        Function that close positions for every existing contract 
        """
        return 
    
    def getPositionInfo(self, contractName) : 
        """ 
        Function that returns informations on a global position for a specified contract. 
        """ 
        return 
    

    
    
    


