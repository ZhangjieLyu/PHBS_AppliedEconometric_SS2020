# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11

@author: Robert
"""
#%% import library
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import os
import collections

#%% file path
workingDir = "D:\\working space\\appliedEconometric_Project\\rawData"
FA_dataPath = "FundamentalData_AsOfDate.csv"
stockTrading_dataPath = "StockTradingDataMonthly.csv"

#%% read files into RAM
FA_df = pd.read_csv(os.path.join(workingDir, FA_dataPath), index_col = 0,
                    converters = {"SID":str})

stockData_df = pd.read_csv(os.path.join(workingDir, stockTrading_dataPath),
                           converters = {"SID":str})

#%% modification of unit in market value of Financial Accounting data
stockData_df["Floating_MV"] = stockData_df["Floating_MV"]*1000
stockData_df["Tot_MV"] = stockData_df["Tot_MV"]*1000

#%% pre-merge - modify date
FA_df["Annodt"] = pd.to_datetime(FA_df["Annodt"], format = "%Y-%m-%d")
stockData_df["Trading_Date"] = pd.to_datetime(stockData_df["Trading_Date"], format = "%Y-%m-%d")

# add one month offset to avoid look-ahead bias
FA_df["Annodt_offsetXMon"] = FA_df["Annodt"] + pd.tseries.offsets.DateOffset(months=0) #no lag

#%% use left join, where left is stockData_df 
# add a left key 'Trading_Month' as well as a right key 'Trading_Month'
FA_df["Trading_Month"] = FA_df["Annodt_offsetXMon"].dt.strftime("%Y-%m")
stockData_df["Trading_Month"] = stockData_df["Trading_Date"].dt.strftime("%Y-%m")

#%% check duplication of FA_df
FA_duplicateDf = FA_df[FA_df.duplicated(subset = ["SID", "Trading_Month"], keep = False)] # keep all obs for check

#%% after check duplication, further process of data set
# when duplicates, keep the latest term. 
FA_df.drop_duplicates(subset = ["SID", "Trading_Month"], keep = "last", inplace = True)

# drop unused colns
FA_df.drop(columns = ["Annodt", "Annodt_offsetXMon"], inplace = True)

#%% left merge
# direct left merge show the duplicate record in FA_df with same SID and trading_month
FA_stock_mergeDf = pd.merge(stockData_df, FA_df, how = 'left', on = ["SID", "Trading_Month"])

#%% fill data point(data point from FA_df) of FA_stock_mergeDf using ffill
FA_df_colns = FA_df.columns.values
FA_stock_mergeDf_colns = FA_stock_mergeDf.columns.values
# FA_stock_mergeDf[FA_df_colns] = FA_stock_mergeDf[FA_df_colns].fillna(method = "ffill")
# before ffill, sort_value just in case
FA_stock_mergeDf.sort_values(by = ["Trading_Month", "SID"],
                             inplace = True,
                             ascending = [True, True])
FA_stock_mergeDf.reset_index(inplace = True, drop = True)

FA_stock_mergeDf[FA_df_colns] = \
    FA_stock_mergeDf.groupby("SID")[FA_df_colns].transform(lambda x: x.ffill(axis = 0))

FA_stock_mergeDf = FA_stock_mergeDf[FA_stock_mergeDf_colns]

#%% write csv
# UNCOMMENT ME
FA_stock_mergeDf.to_csv(os.path.join(workingDir,"Fundamental_Stock_merged.csv"),index = False)

#%% group by date, sort by SID, form a new multi-index table
FA_stock_mergeDf.set_index(["Trading_Date","SID"],inplace = True)
FA_stock_mergeDf.sort_index(inplace = True)