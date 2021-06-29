#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 14:45:19 2021

@author: loann
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys 
import time 
import datetime as dt 
import importlib


# API connector importation 
quanTradePath = "../"
sys.path.append(quanTradePath)
import quanTrade.mbapi.client as client 


# Strategy importation 
strategyPath = "/home/loann/Travail/Quantums/Travaux/Algorithmes/Quantums_Framework/Q26_QuanTester/tests/"
strategyFile = "strategyExample"
sys.path.append(strategyPath) 
strategy = importlib.import_module(strategyFile)
s = strategy.STRATEGY()

s.volumeFactor = 1

# Connection to the API 
c = client.CLIENT_MAIN("MT4") 
print ("Create the client object")
c.connect(configFile = "../quanTrade/client_connection.json") 
print ("Connecting to the server. 5 seconds wait")
time.sleep(5)
c.newContract("EUR.USD", configFile = "../quanTrade/client_contracts.json") 
 


restTime = 60 
while True : 
    s.run(c) 
    s.show(c) 
    time.sleep(restTime)