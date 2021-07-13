#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 11:00:05 2021

@author: loann
"""

import json 

class SYSTEM : 


    def place_order(function) : 
        def func(self, *args, **kwargs) : 
            result = function(self, *args, **kwargs)
            
            arguments = dict()
            
            arguments.update({"SYSTEM ACTION" : "place order"})
            arguments.update({"contractName" : args[0]})
            arguments.update(kwargs)
            arguments.update({"client response" : result})
            

            with open(self.trading_log_path, "a") as json_file : 
                json.dump(arguments, json_file)
                json_file.write("\n")
                
            return result 
        return func

    