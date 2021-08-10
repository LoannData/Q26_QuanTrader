#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 09:44:13 2021

@author: loann
"""

import importlib
import json 
import time 
import datetime as dt 
import sys, os 

dirname  = os.path.dirname(__file__)
filename = os.path.join(dirname,".")
sys.path.append(filename)
import quanTrade.client as client 
import quanTrade.distant as distant 
#from quanTrade.mbapi.system import SYSTEM

class TRADER : 
    
    def __init__(self) :
        
        # CLIENT_MAIN object informations 
        self.client                       = None 
        self.client_name                  = None 
        self.client_connect_path          = None 
        self.client_contract_path         = None 
        
        # STRATEGY object informations 
        self.strategy_name                = None 
        self.strategy_path                = None
        self.strategy                     = None
        
        # Trading Log file 
        self.trading_log_path             = None 
        self.trading_log                  = None 
        self.trading_log_first_write_mode = None 
        
    
    def set_telegram_listen_mode(self) : 
        
        assert self.client.telegram_bot_mode == "listen", "error, bad telegram mode."
        
        self.client.telegram_bot.set_listen_mode()
        
        return 

    
    
    def initialize_telegram_bot(self, 
                                TOKEN = None, 
                                mode  = "write") : 
        
        assert self.client is not None, "Error, client object have to be defined before"
        assert TOKEN is not None, "Error. No provided token."
        
        self.client.telegram_bot_mode = mode 
        self.client.telegram_bot = distant.TELEGRAM_BOT()
        self.client.telegram_bot.initialize() 
        
        return 
    
    def set_telegram_handler(self, 
                             action    = "place order", 
                             command   = "play") : 
        
        assert self.client is not None, "Error, client object have to be defined before"
        self.client.telegram_bot.set_telegram_handler(action  = action, 
                                               command = command)
        
        return 
    
    def enable_telegram_bot(self) : 
        
        assert self.client is not None, "Error, client object have to be defined before"
        self.client.enabled_telegram_bot = True 
        self.client.telegram_bot.start() 
        
        return 
        
        
    def set_trading_log(self, 
                        path    = None, 
                        replace = False) : 
        
        if path is not None : 
            self.trading_log_path = path 
        
        assert self.trading_log_path is not None, "Error while reading the trading log file. Please provide a path." 
        

        if replace : 
            self.trading_log_first_write_mode = "w"
        else : 
            self.trading_log_first_write_mode = "a"

        
        
    
    def set_client(self, 
                   name                 = None, 
                   client_connect_path  = None, 
                   client_contract_path = None) : 
        """ 
        
        """
        if name is not None : 
            self.client_name = name 
        if client_connect_path is not None : 
            self.client_connect_path = client_connect_path 
        if client_contract_path is not None : 
            self.client_contract_path = client_contract_path 
            
        
        assert self.client_name is not None, "No client selected. Please, provide a client name." 
        assert self.client_connect_path is not None, "No client connection file selected. Please, provide it."
        assert self.client_contract_path is not None, "No client contract file selected. Please, provide it"
        
        self.client = client.CLIENT_MAIN(self.client_name)
        self.client.configFile_connexion = self.client_connect_path 
        self.client.configFile_contract  = self.client_contract_path 
        
        if self.trading_log_path is not None : 
            self.client.trading_log_path     = self.trading_log_path
        
    
    def set_strategy(self, 
                     strategy_name = None, 
                     strategy_path = None) : 
        """ 
        
        """
        
        if strategy_name is not None : 
            self.strategy_name = strategy_name 
        if strategy_path is not None : 
            self.strategy_path = strategy_path 
        
        assert self.strategy_name is not None, "No strategy name provided. Please provide it" 
        assert self.strategy_path is not None, "No strategy path provided. Please, provide it" 
        
        sys.path.append(self.strategy_path) 
        strategy = importlib.import_module(self.strategy_name)
        self.strategy = strategy.STRATEGY()
    

    
    def run(self, latency = 60) : 
        """ 
        
        """
        intro_dict = {"New Trading Session" : str(dt.datetime.now())}
        
        with open(self.trading_log_path, self.trading_log_first_write_mode) as json_file : 
            json.dump(intro_dict, json_file)
            json_file.write("\n")
        
        step_number = 0 
        
        while True : 
            
            step_number += 1 
            local_time   = str(dt.datetime.now())
            
            step_dict    = {
                "Step"       : step_number, 
                "Local time" : local_time 
                }
            
            with open(self.trading_log_path, "a") as json_file : 
                json.dump(step_dict, json_file)
                json_file.write("\n")
            
            self.strategy.run(self.client) 
            self.strategy.show(self.client) 
            
            time.sleep(latency)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    