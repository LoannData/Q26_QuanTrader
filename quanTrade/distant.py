#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 08:10:57 2021

@author: loann
"""
from telegram.ext import MessageHandler, Filters
from telegram.ext import CommandHandler
from telegram.ext import Updater
import logging
import time 

class TELEGRAM_BOT : 
    
    def __init__(self) : 
        
        self.bot_address = "t.me/Q26_Signal_bot"
        self.TOKEN = ""
        
        #self.telegram_handler_command = "play"
        
        self.message = None
        self.received_message = None 
        
        return 
        
    def initialize(self) : 
        
        # 1. Create the updater object 
        
        self.updater = Updater(token=self.TOKEN, use_context=True)
        
        # 2. Local access to the dispatcher 
        self.dispatcher = self.updater.dispatcher
        
        # 3. Logging module to get a debug info 
        
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                             level=logging.INFO)
    
    
    def echo(self, update, context):
        
        self.received_message = update.message.text
        print (self.received_message)

        #context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    
    
    def set_listen_mode(self) : 
        
        echo_handler = MessageHandler(Filters.text & (~Filters.command), self.echo)
        self.dispatcher.add_handler(echo_handler)
        

    def set_telegram_handler(self, 
                             action    = "place order", 
                             command   = "play") : 
        
        if action == "place order" : 
            
            handler = CommandHandler(command, self.place_order_)
            self.dispatcher.add_handler(handler) 
            
        if action == "edit stoploss order" : 
            
            handler = CommandHandler(command, self.edit_SL_order_)
            self.dispatcher.add_handler(handler) 
        
        if action == "edit takeprofit order" : 
            
            handler = CommandHandler(command, self.edit_TP_order_)
            self.dispatcher.add_handler(handler)  
            
        if action == "cancel order" : 
            
            handler = CommandHandler(command, self.cancel_order_)
            self.dispatcher.add_handler(handler)
            
        if action == "close position" : 
            
            handler = CommandHandler(command, self.close_position_)
            self.dispatcher.add_handler(handler) 
        
        if action == "transactions mode" : 
            
            handler = CommandHandler(command, self.place_order_)
            self.dispatcher.add_handler(handler) 
            handler = CommandHandler(command, self.edit_SL_order_)
            self.dispatcher.add_handler(handler) 
            handler = CommandHandler(command, self.edit_TP_order_)
            self.dispatcher.add_handler(handler) 
            handler = CommandHandler(command, self.cancel_order_)
            self.dispatcher.add_handler(handler)
            handler = CommandHandler(command, self.close_position_)
            self.dispatcher.add_handler(handler)
            
        return 
            
        

        
    # 4. Function that should process a specific type of update 
    def place_order_(self, update, context):
        while True :          
            if self.message is not None : 
                if self.message.get("SYSTEM ACTION") == "place order" : 
                    self.message = str(self.message)
                    context.bot.send_message(chat_id=update.effective_chat.id, text=self.message)
                    self.message = None
        return 
    
    def edit_SL_order_(self, update, context):
        while True :          
            if self.message is not None : 
                if self.message.get("SYSTEM ACTION") == "edit stoploss order" : 
                    self.message = str(self.message)
                    context.bot.send_message(chat_id=update.effective_chat.id, text=self.message)
                    self.message = None
        return 
    
    def edit_TP_order_(self, update, context):
        while True :          
            if self.message is not None : 
                if self.message.get("SYSTEM ACTION") == "edit takeprofit order" : 
                    self.message = str(self.message)
                    context.bot.send_message(chat_id=update.effective_chat.id, text=self.message)
                    self.message = None
        return 

    def cancel_order_(self, update, context):
        while True :          
            if self.message is not None : 
                if self.message.get("SYSTEM ACTION") == "cancel order" : 
                    self.message = str(self.message)
                    context.bot.send_message(chat_id=update.effective_chat.id, text=self.message)
                    self.message = None
        return 
    
    def close_position_(self, update, context):
        while True :          
            if self.message is not None : 
                if self.message.get("SYSTEM ACTION") == "close position" : 
                    self.message = str(self.message)
                    context.bot.send_message(chat_id=update.effective_chat.id, text=self.message)
                    self.message = None
        return 
            
            

    def start(self) : 
        self.updater.start_polling(poll_interval = 10)

        
        
        
        