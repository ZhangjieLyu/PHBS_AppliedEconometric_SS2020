# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 2020

@author: Robert
"""
#%% load library

# built-in library
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import scipy as sp
import os
import collections
import statsmodels.api as sm
from numpy.linalg import inv
import itertools
# os.chdir(\\path\\to\\file)
from CreateFactorTable import CreateFactorTable
from FamaMacbethRegression import FamaMacbethRegression

#%% file path
workingDir = "D:\\working space\\appliedEconometric_Project\\rawData"
dataPath = "FundamentalData_Stock_MarketReturn_RiskFree.csv"

#%% read data into RAM
data = pd.read_csv(os.path.join(workingDir, dataPath), index_col = None,
                   converters = {"SID":str})

#%% create factor table
# factor computation

# WARNING: takes a long time, return has been adjusted by risk free rate
FT = CreateFactorTable(data)
FT.tidy_data()
FT.gen_DataFrame()
FT.buildDataFrame(["SID","Trading_Month","Trading_Date","Adj_Close_wDR","Tot_MV","Floating_MV"])
df_Factors = FT.applyMethod()

#%% start EDA - cross-sectional EDA
def MEDIAN(x):
    return(np.nanmedian(x))

def SKEWNESS(x):
    return(sp.stats.skew(x, nan_policy = "omit"))

def KURTOSIS(x):
    return(sp.stats.kurtosis(x, nan_policy = "omit"))

aggragation = {
    "NumberOfAssets": ("SID", "size"),
    "MeanMonthlyReturn": ("monthlyReturn", "mean"),
    "MedianMonthlyReturn": ("monthlyReturn", MEDIAN),
    "SkewnessMonthlyReturn": ("monthlyReturn", SKEWNESS),
    "KurtosisMonthlyReturn": ("monthlyReturn", KURTOSIS),
    "TotalMarketValue": ("Tot_MV", "sum"),
    "MeanTotalMarketValueOfAssets": ("Tot_MV","mean"),
    "TotalFloatingMarketValue": ("Floating_MV", "sum")
    }
df_CrossSectional = df_Factors.groupby("Trading_Month").agg(**aggragation)

#%% write csv
df_CrossSectional.to_csv(os.path.join(workingDir, "data_EDA.csv"))