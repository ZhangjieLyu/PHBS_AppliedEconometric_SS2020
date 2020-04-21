# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 17:57:06 2020

@author: Robert
"""
#%% load library
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import os
import collections
import statsmodels.api as sm
from numpy.linalg import inv
import itertools
import tqdm

#%% prepare market return and risk-free rate - part 1
workingDir = "D:\\working space\\appliedEconometric_Project\\rawData"
marketReturnDataPath = "Monthly Market Return\\TRD_Mont.csv"

monthlyMarketReturn = pd.read_csv(os.path.join(workingDir, marketReturnDataPath), index_col = False)
monthlyMarketReturn = monthlyMarketReturn[np.logical_or(monthlyMarketReturn["Markettype"] == 1,
                                                        monthlyMarketReturn["Markettype"] == 4)][["Markettype","Trdmnt","Mretwdtl","Mmvttl"]]
monthlyMarketReturn.columns = ["Markettype","Trading_Month","Market_Return","MV_MarketType"]
monthlyMarketReturn.reset_index(drop = True, inplace = True)
#%% prepare market return and risk-free rate - part 2
SH_marketReturn = monthlyMarketReturn[monthlyMarketReturn["Markettype"]==1]
SZ_marketReturn = monthlyMarketReturn[monthlyMarketReturn["Markettype"]==4]

marketRt_mergedDf = pd.DataFrame(data = SH_marketReturn["Trading_Month"], columns = ["Trading_Month"])
marketRt_mergedDf["Market_Return"] = (SH_marketReturn["Market_Return"].values*SH_marketReturn["MV_MarketType"].values+
                                      SZ_marketReturn["Market_Return"].values*SZ_marketReturn["MV_MarketType"].values)/(SH_marketReturn["MV_MarketType"].values + SZ_marketReturn["MV_MarketType"].values)

#%% prepare risk-free rate
riskFreeRateDataPath = "Risk-free rate\\TRD_Nrrate.csv"
riskFreeData_rawDf = pd.read_csv(os.path.join(workingDir, riskFreeRateDataPath))

riskFreeData_rawDf.index = pd.to_datetime(riskFreeData_rawDf["Clsdt"],format = "%Y-%m-%d")
riskFreeData_monthly = riskFreeData_rawDf.resample("M").agg({"Nrrmtdt":"last"})

riskFreeData_monthly.reset_index(inplace = True)
riskFreeData_monthly["Trading_Month"] = riskFreeData_monthly["Clsdt"].dt.strftime("%Y-%m")
riskFreeData_monthly.drop(columns = "Clsdt", inplace = True)
riskFreeData_monthly.columns = ["Risk_Free_Rate","Trading_Month"]

#%% merge market return and riskFree_data
riskFreeData_monthly["Risk_Free_Rate"] = riskFreeData_monthly["Risk_Free_Rate"]/100
df_wRiskFree_wMarketReturn = pd.merge(marketRt_mergedDf, riskFreeData_monthly,
                                      how = "left", on = "Trading_Month")

#%% other file path
workingDir = "D:\\working space\\appliedEconometric_Project\\rawData"
dataPath = "Fundamental_Stock_merged.csv"

#%% read data into RAM
data = pd.read_csv(os.path.join(workingDir, dataPath), index_col = None,
                   converters = {"SID":str})
#%% merge with market return & risk free rate
data_wFA_wStock_wMarketRet_wRf = pd.merge(data, df_wRiskFree_wMarketReturn,
                                          how = 'left', on = ["Trading_Month"])

#%% save to disc
data_wFA_wStock_wMarketRet_wRf.to_csv(os.path.join(workingDir,"FundamentalData_Stock_MarketReturn_RiskFree.csv"), index= False)
