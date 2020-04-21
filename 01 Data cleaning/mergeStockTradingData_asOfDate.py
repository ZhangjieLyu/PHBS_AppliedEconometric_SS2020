# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 16:04:04 2020

@author: Robert
"""
#%% import library
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import collections

#%% prepare dir
workingDir = "D:\\working space\\appliedEconometric_Project\\rawData"
tradingInfo = "Stock Trading Data Daily"

#%% read csv
# monthlyTradingData_rawDf = pd.read_csv(os.path.join(workingDir, tradingInfo),
#                                        converters = {"Stkcd":str})

# monthlyTradingData_rawDf["Trdmnt"] = pd.to_datetime(monthlyTradingData_rawDf["Trdmnt"],
#                                                     format = "%Y-%m")

# # rename colns
# newColName = ["SID", "Trading_Month", "Month_Open", "Month_Close", 
#               "Month_Volume", "MonthEnd_FloatingMV", "MonthEnd_Tot_MV"]
# monthlyTradingData_rawDf.columns = newColName

# # sort value
# monthlyTradingData_rawDf.sort_values(["SID", "Trading_Month"], inplace = True,
#                                      ascending = [True, True])

# # reset index
# monthlyTradingData_rawDf.reset_index(inplace = True)
# monthlyTradingData_rawDf.drop(columns = ["index"], inplace = True)

# checked: no missing values

#%% read csv using daily data

def read_csv_merge(workingDir, converter, col_drop=[], index_col=None):
    """
    read csv files in workingDir and return a pandas Dataframe
    
    workingDir: os path to target directory
    converter: a dict, use to specify the data type involved in reading csv
    col_drop: a list[str], use to specify which colns to drop
    index_col: use to indicate index coln.
    """
    if os.path.exists(workingDir):
        fileNames = [f for f in os.listdir(workingDir) if f.split(".")[1] == "csv"]
    else:
        print("no such directory!")
        return
    
    outputDf = pd.DataFrame()
    
    for f in fileNames:
        f_path = os.path.join(workingDir, f)
        f_df = pd.read_csv(f_path, index_col = index_col, converters = converter)
        outputDf = pd.concat([outputDf, f_df])
    
    outputDf.reset_index(inplace = True)
    
    if len(col_drop)>0:
        outputDf.drop(columns = col_drop, inplace = True)
        
    outputDf.drop(columns = "index", inplace = True)
        
    return outputDf
        
converter = {"Stkcd":str}
stockTradingDaily_rawDf = read_csv_merge(os.path.join(workingDir, tradingInfo),
                                         converter)

#%% resample the daily data to be monthly data - step 1
newColName = ["SID","Trading_Date","Volume","Floating_MV","Tot_MV",
              "Daily_Ret_wDR","Daily_Ret_nDR","Adj_Close_wDR",
              "Adj_Close_nDR","Trading_Status"]
stockTradingDaily_rawDf.columns = newColName

# reorgnize the data frame
stockTradingDaily_rawDf["Trading_Date"] = pd.to_datetime(stockTradingDaily_rawDf["Trading_Date"],
                                                         format = "%Y-%m-%d")
stockTradingDaily_rawDf.sort_values(by = ["Trading_Date","SID"], inplace = True,
                                    ascending = [True, True])
stockTradingDaily_rawDf.reset_index(inplace = True)
stockTradingDaily_rawDf.drop(columns = ["index"], inplace = True)

# set index to be datetime Range
stockTradingDaily_rawDf.set_index("Trading_Date", inplace = True)
#%% adjust trading status to be bool
# modify "trading status" to be "days that trading volume > 0? True:False"
stockTradingDaily_rawDf["Trading_Status"] = stockTradingDaily_rawDf["Volume"] > 0

#%% resample data - step ii
# groupby SID, resample by month

# warning: takes a very long time
stockTradingMonthly_rawDf = stockTradingDaily_rawDf.groupby("SID").resample("M").agg(
    {
     "Volume": "sum",
     "Floating_MV": "last",
     "Tot_MV": "last", #view monthly ret from the close of the last month to the close to current month
     "Adj_Close_wDR": "last",
     "Adj_Close_nDR": "last",
     "Trading_Status": "sum"
     })
# a summary: note! this is to adjust based on the last trading date before ex-right

#%% write data into csv and prepare to merge with fundamental data
stockTradingMonthly_rawDf.to_csv(os.path.join(workingDir, "StockTradingDataMonthly.csv"))