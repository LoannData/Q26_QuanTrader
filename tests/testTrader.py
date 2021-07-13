#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 09:55:52 2021

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
import quanTrade.mbapi.trader as trader



t = trader.TRADER()

t.set_trading_log("./outputExample.txt", replace = True)

t.set_client(name                 = "MT4", 
             client_connect_path  = "../quanTrade/client_connection.json", 
             client_contract_path = "../quanTrade/client_contracts.json")

t.set_strategy(strategy_name = "strategyExample", 
               strategy_path = "./") 

t.client.newContract("EUR.USD")

t.strategy.volumeFactor = 1. 

t.client.connect()

t.run(latency = 60)


