#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 08:55:32 2021

@author: loann
"""

import json 
import numpy as np 

def getClientConnectionInfo(file = None, 
                            brokerName = None, 
                            referenceNumber = 0) : 
    """ 
    Function that reads the json file containing the client connection informations 
    for every registered brokers. 
    """
    if (file is None) : 
        file = "../client_connection.json"
    data = open(file, "r") 
    if (brokerName is not None) : 
        return json.load(data).get(str(referenceNumber)).get(brokerName) 
    return json.load(data)

def getContractInfo(file         = None, 
                    brokerName   = None, 
                    contractName = None) : 
    """ 
    Function that reads the json file containing then client contracts informations 
    for every registered brokers. 
    """
    if (file is None) : 
        file = "../client_contracts.json" 
    data = open(file, "r") 
    if (contractName is not None) :
        if (brokerName is not None) : 
            return json.load(data).get(contractName).get(brokerName) 
        return json.load(data).get(contractName)
    return json.load(data)

def serialNumber(number = 10, size = 20) :
    serie = np.random.randint(number, size = size) 
    serie_str = '' 
    for n in serie : 
        serie_str += str(n) 
    return int(serie_str)

