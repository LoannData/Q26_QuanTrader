#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#############################################################
STRATEGY FILE
#############################################################
This file contains the strategy that will be read and executed 
by the backtester.

Please, read carefully all the explanations and report any 
bugs found in this file. 
"""


class STRATEGY : 
    """ 
    The STYRATEGY class is imported in the SIMULATION class. 
    
    Only 3 functions are important and executed in the backtester : 
        - __init__ : To declare the strategy object 
        - run      : Function called to each timestep of the simulation 
        - show     : Function called to each log step of the simulation 
    
    One can add any function in this class. This will not pertubate the 
    simulation. 
    
    run and show functions take in account a "client" parameter which 
    corresponds to the "PORTFOLIO" object as declared in the simulation
    header file. 
    """ 
    
    def __init__(self) : 
        
        return 
    
    def run(self, client) : 
        
        return 
    
    def show(self, client) : 
        
        return 