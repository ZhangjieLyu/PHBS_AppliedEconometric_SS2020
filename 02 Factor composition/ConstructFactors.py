# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 14:29:14 2020

@author: Robert
"""
import numpy as np
import pandas as pd
import collections
import statsmodels.api as sm
from numpy.linalg import inv
import itertools

class ConstructFactors(object):
    def __init__(self, data):
        self.data = data
        
    def tidy_data(self):
        # sort_values and reset_index first
        data = self.get_rawData()
        data["Trading_Date"] = pd.to_datetime(data["Trading_Date"], format = "%Y-%m-%d")
        data.sort_values(by = ["SID","Trading_Date"], inplace = True,
                         ascending = [True, True])
        data.reset_index(drop = True, inplace = True)
        self.set_rawData(data)
        
    def set_rawData(self, newData):
        self.data = newData
    
    def get_rawData(self):
        return self.data
        
    def compute_logME(self):
        ME = self.data["Floating_MV"].values
        return(np.log(ME))
    
    def compute_EP(self):
        E = self.data["Net_Profit_After_Min_Int_Inc"].values
        P = self.data["Tot_MV"].values
        return(np.divide(E,P))
    
    def compute_EPplus(self):
        EP = self.compute_EP()
        EP[EP<0] = 0
        return(EP)
    
    def compute_DEPsmaller0(self):
        EP = self.compute_EP()
        return(np.array(EP<0, dtype=float))
    
    def compute_logBM(self):
        B = self.data["Tot_SE_After_Min_Int"].values
        M = self.data["Tot_MV"].values
        return(np.log(np.divide(B,M)))
    
    def compute_CP(self):
        C = self.data["Cash_Cash_Equ_End"].values - self.data["Cash_Cash_Equ_Begin"].values
        P = self.data["Tot_MV"].values
        return(np.divide(C,P))
    
    def compute_CPplus(self):
        CP = self.compute_CP()
        CP[CP<0] = 0
        return(CP)
    
    def compute_DCPsmaller0(self):
        CP = self.compute_CP()
        return(np.array(CP<0, dtype = float))
    
    def compute_logAM(self):
        A = self.data["Tot_Assets"].values
        M = self.data["Tot_MV"].values
        return(np.log(np.divide(A,M)))
    
    def compute_monthlyReturn(self):
        returnSIDDate = pd.DataFrame(self.data[["SID","Trading_Date","Adj_Close_wDR"]])
        return(returnSIDDate.groupby("SID").
               apply(lambda x:x["Adj_Close_wDR"].pct_change()).
               reset_index().
               sort_values(by = "level_1")["Adj_Close_wDR"].values)
    
    def compute_beta(self, window = 12, r_f = None): 
        self.data["monthlyReturn"] = self.compute_monthlyReturn()

        self.data["monthlyReturn"] = self.compute_monthlyReturn() - self.data["Risk_Free_Rate"].values
        self.data["Market_Return"] = self.data["Market_Return"].values - self.data["Risk_Free_Rate"].values
        returnSIDDate = pd.DataFrame(self.data[["SID","Trading_Date","monthlyReturn","Market_Return"]])
        
        corr_MarketRet_StockRet = returnSIDDate.groupby("SID")[["monthlyReturn","Market_Return"]].rolling(window).corr().iloc[0::2,-1].reset_index().sort_values(by = "level_1")["Market_Return"].values
        var_StockRet = returnSIDDate.groupby("SID")["monthlyReturn"].rolling(window).var().reset_index().sort_values(by = "level_1")["monthlyReturn"].values
        var_MarketRet = returnSIDDate.groupby("SID")["Market_Return"].rolling(window).var().reset_index().sort_values(by = "level_1")["Market_Return"].values
               
        return(corr_MarketRet_StockRet*(var_StockRet**0.5)/(var_MarketRet**0.5)) 

    def compute_ROE(self):
        R = self.data["Net_Profit_After_Min_Int_Inc"].values
        E = self.data["Tot_SE_After_Min_Int"].values
        return(np.divide(R,E))

    def compute_InvestmentFactor(self):
        returnSIDDate = pd.DataFrame(self.data[["SID","Trading_Date","Tot_Assets"]])
        return(returnSIDDate.groupby("SID").
               apply(lambda x:x["Tot_Assets"].pct_change()).
               reset_index().
               sort_values(by = "level_1")["Tot_Assets"].values)
                
