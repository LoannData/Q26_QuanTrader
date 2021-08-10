#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#############################################################
STRATEGY FILE
#############################################################
This file contains the strategy that will be read and executed 
by the trader. This file should have been already tested 
thanks to the Q26_quanTester tool.

Please, read carefully all the explanations and report any 
bugs found in this file. 
"""

import pandas as pd 
import matplotlib.pyplot as plt 


class STRATEGY : 
    """ 
    The STYRATEGY class is imported in the TRADER class. 
    
    Only 3 functions are important and executed in the backtester : 
        - __init__ : To declare the strategy object 
        - run      : Function called to each timestep of the simulation 
        - show     : Function called to each log step of the simulation 
    
    One can add any function in this class. This will not pertubate the 
    simulation. 
    
    run and show functions take in account a "client" parameter which 
    corresponds to the client connection socket object which allows us 
    to interact with trading platform. 
    """ 
    
    def __init__(self) : 
        # Name of the symbol to trade 
        # Note : The names of the symbol used in the strategy object
        #        have to be the the exact same as the ones defined in 
        #        the trader header file 
        self.symbolName = "EUR.USD"
        self.timeframe = 5
        
        # Volume factor 
        self.volumeFactor = 1.
        
        
        # Moving average parameters 
        self.SMA1 = None 
        self.SMA2 = None 
        
        self.SMA1_period = 10 
        self.SMA2_period = 30 
        
        # Trading status memory 
        self.activePosition = None
        self.placedOrder    = None 
        
        #  Other options 
        self.showInfo = True 
        
        return 
    
    def run(self, client) : 
        
        # We ask for the last existing price 
        self.lastPrice = client.getLastPrice(self.symbolName)
        self.dataSet1  = None 
        self.dataSet2  = None  
        
        # If the market if open 
        if self.lastPrice.get("market state") == "open" : 
            # We ask for 2 datasets in H1 period 
            self.dataSet1 = client.getHistoricalData(self.symbolName, self.SMA1_period, 0, self.timeframe, onlyOpen = True)
            self.dataSet2 = client.getHistoricalData(self.symbolName, self.SMA2_period, 0, self.timeframe, onlyOpen = True)
            # We calculate 2 SMA indicators 
            if len(self.dataSet1.get("askclose")) > 0 : 
                self.SMA1 = SMA(self.dataSet1.get("askclose"), period = self.SMA1_period, offset = 0)
            if len(self.dataSet2.get("askclose")) > 0 : 
                self.SMA2 = SMA(self.dataSet2.get("askclose"), period = self.SMA2_period, offset = 0)
            
            # If we have no active position 
            if self.activePosition is None : 
                
                # Long order 
                if self.SMA1.value[-1] > self.SMA2.value[-1] :
                    
                    if self.showInfo : print ("Placing long order")
                    
                    # We place an order. 
                    # Note, the placeOrder function return a list 
                    # of three elements. If the order have been 
                    # correctly placed, the output is : [Executed order, lmt SL, lmt TG], 
                    # else, the output is : [False, False, False] 
                    orderList = client.placeOrder(self.symbolName,
                                                  action     = "long", 
                                                  orderType  = "MKT", 
                                                  volume     = 0.1*self.volumeFactor, 
                                                  stoploss   = 0.5, 
                                                  takeprofit = 2.)
                    
                    if orderList[0] is not False : 
                        self.placedOrder = orderList[0] 
                        self.activePosition = "long"
                    
                # Short order 
                if self.SMA1.value[-1] < self.SMA2.value[-1] : 
                    
                    if self.showInfo : print ("Placing short order")
                    
                    orderList = client.placeOrder(self.symbolName,
                                                     action     = "short", 
                                                     orderType  = "MKT", 
                                                     volume     = 0.1*self.volumeFactor, 
                                                     stoploss   = 2., 
                                                     takeprofit = 0.5)
                    if orderList[0] is not False : 
                        self.placedOrder = orderList[0] 
                        self.activePosition = "short"
                    
            elif ((self.SMA1.value[-1] > self.SMA2.value[-1] and self.activePosition == "short") or 
                  (self.SMA1.value[-1] < self.SMA2.value[-1] and self.activePosition == "long")): 
                
                # To close a position, one have to provide the order that have been 
                # executed to open the position. 
                client.closePosition(self.symbolName, self.placedOrder)
                self.placedOrder    = None 
                self.activePosition = None
        
        return 
    
    def show(self, client) : 
        
        if self.showInfo : 
            
            print ("===================================")
            print ("EXAMPLE TRADING STRATEGY LOG OUTPUT")
            print ("===================================")
            print ("Actual date:   ",str(self.lastPrice.get("date"))) 
            print ("Market status: ",self.lastPrice.get("market state"))
            print ("Actual price: ")
            print ("- Ask Open:  ",self.lastPrice.get("askopen"))
            print ("- Ask High:  ",self.lastPrice.get("askhigh"))
            print ("- Ask Low:   ",self.lastPrice.get("asklow"))
            print ("- Ask Close: ",self.lastPrice.get("askclose"))
            print ("- Ask Price: ",self.lastPrice.get("askprice"))
            print ("-----------------------------------")
            if self.dataSet1 is not None:
                print ("The last requested data :")
                print (pd.DataFrame(self.dataSet1))
                print (pd.DataFrame(self.dataSet2))
                print ("The last known moving average values : ")
                print ("SMA(10): ",self.SMA1.value[-1])
                print ("SMA(30): ",self.SMA2.value[-1])
            
        return 






class SMA : 
    
    def __init__(self, y, period = 20, offset = 0) : 
        """

        """
        
        if (offset != 0) : 
            y = y[:-offset]
        
        sma_temp = [y[0]]
        for ii in range(1, len(y)) :  
            
            if (ii < period) : 
                sum_temp = 0 
                for jj in range(0, ii) : 
                    sum_temp += y[jj]
                sum_temp = sum_temp / (ii)
                
                sma_temp.append(sum_temp)

            if (ii >= period) : 
                sum_temp = 0
                for jj in range(ii - period, ii) : 
                    sum_temp += y[jj]
                sum_temp = sum_temp / (period)
                
                sma_temp.append(sum_temp)
        
        self.value  = sma_temp 
        self.period = period 
        self.offset = offset 
