#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys 
dirname  = os.path.dirname(__file__)
filename = os.path.join(dirname,"..")
sys.path.append(filename)
import mbapi.client as client 
import time 



c = client.CLIENT_MAIN("IBKR") 
print ("Create the client object")
c.connect() 
print ("Connecting to the server. 5 seconds wait")
time.sleep(5)
c.newContract("EUR/USD") 
print ("Placing an order and wait for 10 seconds")
orderList = c.placeOrder("EUR/USD", 
                         action     = "long", # "long" or "short". 
                         orderType  = "bracket", # Order kind : "bracket" 
                         volume     = 100, # Volume of the asset to trade in the asset unit 
                         stoploss   = 1.19250, # Stoploss value
                         takeprofit = 1.19900, # Take profit value 
                         lmtPrice   = None, # Order executed if price reaches the lmtPrice 
                         auxPrice   = None)

time.sleep(10) 
print ("Editing the stoploss value and wait for 10 seconds")
c.editSLOrder("EUR/USD", orderList[2], stoploss = 1.19145) 
time.sleep(10) 
print ("Editing the takeprofit value and wait for 10 seconds")
c.editTPOrder("EUR/USD", orderList[1], takeprofit = 1.19950) 
time.sleep(10)
print ("Cancelling the stoploss order and wait for 10 seconds")
c.cancelOrder("EUR/USD", orderList[2]) 
time.sleep(10)
print ("Cancelling the takeprofit order and wait for 10 seconds")
c.cancelOrder("EUR/USD", orderList[1])
time.sleep(10)
print ("Closing the first initial order and wait for 10 seconds")
c.closePosition("EUR/USD", order = orderList[0])
time.sleep(10)
print ("Disconnecting")
c.disconnect() 
