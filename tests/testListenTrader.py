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


telegram_token = ""



t = trader.TRADER()

t.set_trading_log("./outputExample_listen.txt", replace = True)

t.set_client(name                 = "IBKR", 
             client_connect_path  = "../quanTrade/client_connection.json", 
             client_contract_path = "../quanTrade/client_contracts.json")

t.set_strategy(strategy_name = "strategyListenExample", 
               strategy_path = "./") 

t.client.newContract("EUR.USD")

t.strategy.volumeFactor = 1. 


t.initialize_telegram_bot(TOKEN = "", 
                          mode = "listen")

t.set_telegram_listen_mode()
t.enable_telegram_bot()

#time.sleep(10)


t.client.connect()

t.run(latency = 1)


