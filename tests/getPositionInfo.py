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
time.sleep(5)
c.closePosition("EUR/USD")
time.sleep(5)
c.disconnect()