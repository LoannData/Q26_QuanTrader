#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#############################################################
TRADER FILE
#############################################################
This file contains all the instructions to run a strategy 
in live.

Please, read carefully all the explanations and report any 
bugs found in this file. 
"""

import time 


# API TRADER object importation 
from quanTrade.trader import TRADER

# Trader object creation 
t = TRADER()

# Here we specify the location of the trading output log 
# which contain all the operations performed by the 
# trader. 
t.set_trading_log("./outputExample.txt", replace = True)

# We set the client name according the different clients 
# available in our system. 
# ./client_connection.json and ./client_contracts.json are 
# both files containing client connection informations 
# and contracts identity in every system registered clients 
# respectively.
t.set_client(name                 = "MT4", 
             client_connect_path  = "./client_connection.json", 
             client_contract_path = "./client_contracts.json")

# We import a trading strategy. This strategy has been 
# already tested thanks to the Q26_QuanTester tool 
# and can securely run in live. 
t.set_strategy(strategy_name = "strategyExample", 
               strategy_path = "./") 

# According the instrument we want to trade, 
# we add the contract name as defined in the 
# ./client_contracts.json file. 
# The name specified in the strategy example 
# have to be this exact name. 
t.client.newContract("EUR.USD")

# Depending on the trading plateform, 
# the lot size can be different. That's why we need to 
# input a volumeFactor variable in the strategyExample.py 
# file that we manage here as a function of the client 
# choice in order to define the size of our 
# transactions. 
t.strategy.volumeFactor = 1. 


# Let some time to the system to prepare itself to 
# trade. A too short time could break it as it would 
# try to connect to client before having fetched a 
# bunch of important informations
time.sleep(5)

# The system connects to the client 
t.client.connect()

# The system runs the strategy file 
# every 60 seconds. 
t.run(latency = 60)


