#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 11:00:05 2021

@author: loann
"""

import json 
import time 
import datetime as dt 

class SYSTEM : 
    
    def listen_telegram_message(self) : 
        
        message = None 
        if self.telegram_bot_mode == "read" and self.enabled_telegram_bot : 
            
            if self.received_message is not None : 
                
                self.telegram_message = self.received_message 
                self.received_message = None 
                message = self.telegram_message
        
        return message


    def place_order(function) : 
        def func(self, *args, **kwargs) : 
            result = function(self, *args, **kwargs)
            
            arguments = dict()
            
            arguments.update({"SYSTEM ACTION" : "place order"})
            arguments.update({"SYSTEM LOCAL TIME" : str(dt.datetime.now())})
            
            arguments.update({"contractName" : args[0]})
            arguments.update(kwargs)
            arguments.update({"client response" : result})
            
            # Telegram step 
            if self.enabled_telegram_bot and self.telegram_bot_mode == "write" : 
                self.telegram_bot.message = arguments 
            

            with open(self.trading_log_path, "a") as json_file : 
                json.dump(arguments, json_file)
                json_file.write("\n")
                
            return result 
        return func
    
    
    def get_historical_data(function) : 
        def func(self, *args, **kwargs) : 
            result = function(self, *args, **kwargs)
            
            arguments = dict()
            
            arguments.update({"SYSTEM ACTION" : "get historical data"})
            arguments.update({"SYSTEM LOCAL TIME" : str(dt.datetime.now())})
            
            arguments.update({"contractName" : args[0], 
                              "dateIni"      : args[1], 
                              "dateEnd"      : args[2], 
                              "timeframe"    : args[3]})
            
            
            arguments.update(kwargs)
            #arguments.update({"client response" : result})
            
            # Telegram step 
            if self.enabled_telegram_bot and self.telegram_bot_mode == "write" : 
                self.telegram_bot.message = arguments 
            

            with open(self.trading_log_path, "a") as json_file : 
                json.dump(arguments, json_file)
                json_file.write("\n")
                
            return result 
        return func
    
    def get_last_price(function) : 
        def func(self, *args, **kwargs) : 
            result = function(self, *args, **kwargs)
            
            arguments = dict()
            
            arguments.update({"SYSTEM ACTION" : "get last price"})
            arguments.update({"SYSTEM LOCAL TIME" : str(dt.datetime.now())})
            
            arguments.update({"contractName" : args[0]})
            
            
            arguments.update(kwargs)
            arguments.update({"client response" : str(result)})
            
            # Telegram step 
            if self.enabled_telegram_bot and self.telegram_bot_mode == "write" : 
                self.telegram_bot.message = arguments 

            
            with open(self.trading_log_path, "a") as json_file : 
                json.dump(arguments, json_file)
                json_file.write("\n")
                
            return result 
        return func
    
    def edit_SL_order(function) : 
        def func(self, *args, **kwargs) : 
            result = function(self, *args, **kwargs)
            
            arguments = dict()
            
            arguments.update({"SYSTEM ACTION" : "edit stoploss order"})
            arguments.update({"SYSTEM LOCAL TIME" : str(dt.datetime.now())})
            
            arguments.update({"contractName" : args[0], 
                              "order"        : args[1]})
            
            
            arguments.update(kwargs)
            arguments.update({"client response" : result})
            
            # Telegram step 
            if self.enabled_telegram_bot and self.telegram_bot_mode == "write" : 
                self.telegram_bot.message = arguments 
            

            with open(self.trading_log_path, "a") as json_file : 
                json.dump(arguments, json_file)
                json_file.write("\n")
                
            return result 
        return func
    
    def edit_TP_order(function) : 
        def func(self, *args, **kwargs) : 
            result = function(self, *args, **kwargs)
            
            arguments = dict()
            
            arguments.update({"SYSTEM ACTION" : "edit takeprofit order"})
            arguments.update({"SYSTEM LOCAL TIME" : str(dt.datetime.now())})
            
            arguments.update({"contractName" : args[0], 
                              "order"        : args[1]})
            
            
            arguments.update(kwargs)
            arguments.update({"client response" : result})
            
            # Telegram step 
            if self.enabled_telegram_bot and self.telegram_bot_mode == "write" : 
                self.telegram_bot.message = arguments 
            

            with open(self.trading_log_path, "a") as json_file : 
                json.dump(arguments, json_file)
                json_file.write("\n")
                
            return result 
        return func


    def cancel_order(function) : 
        def func(self, *args, **kwargs) : 
            result = function(self, *args, **kwargs)
            
            arguments = dict()
            
            arguments.update({"SYSTEM ACTION" : "cancel order"})
            arguments.update({"SYSTEM LOCAL TIME" : str(dt.datetime.now())})
            
            arguments.update({"contractName" : args[0], 
                              "order"        : args[1]})
            
            
            #arguments.update(kwargs)
            arguments.update({"client response" : result})
            
            # Telegram step 
            if self.enabled_telegram_bot and self.telegram_bot_mode == "write" : 
                self.telegram_bot.message = arguments 
            

            with open(self.trading_log_path, "a") as json_file : 
                json.dump(arguments, json_file)
                json_file.write("\n")
                
            return result 
        return func
    
    def close_position(function) : 
        def func(self, *args, **kwargs) : 
            result = function(self, *args, **kwargs)
            
            arguments = dict()
            
            arguments.update({"SYSTEM ACTION" : "close position"})
            arguments.update({"SYSTEM LOCAL TIME" : str(dt.datetime.now())})
            
            arguments.update({"contractName" : args[0]})
            
            
            arguments.update(kwargs)
            arguments.update({"client response" : result})
            
            # Telegram step 
            if self.enabled_telegram_bot and self.telegram_bot_mode == "write" : 
                self.telegram_bot.message = arguments 
            

            with open(self.trading_log_path, "a") as json_file : 
                json.dump(arguments, json_file)
                json_file.write("\n")
                
            return result 
        return func
    