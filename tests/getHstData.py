#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 11:02:18 2021

@author: loann
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys 
# dirname  = os.path.dirname(__file__)
# filename = os.path.join(dirname,"..")
# sys.path.append(filename)

sys.path.append("../")
import quanTrade.mbapi.client as client 
import time 
import datetime as dt 



c = client.CLIENT_MAIN("IBKR") 
print ("Create the client object")
c.connect(configFile = "../quanTrade/client_connection.json") 
print ("Connecting to the server. 5 seconds wait")
time.sleep(5)
c.newContract("EUR/USD", configFile = "../quanTrade/client_contracts.json") 


time.sleep(1) 

#c.getHistoricalData("EUR/USD", 10, 0, 5, onlyOpen = True)

#time.sleep(1) 

#c.getHistoricalData("EUR/USD", dt.datetime(2021, 3, 17), dt.datetime(2021, 6, 17), 1440, onlyOpen = False)

#time.sleep(1) 

price = c.getLastPrice("EUR/USD")

#c.disconnect()