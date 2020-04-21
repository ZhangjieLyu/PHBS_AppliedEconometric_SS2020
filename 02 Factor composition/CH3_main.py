# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 14:31:10 2020

@author: Robert
"""
#%% load library

# built-in library
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import os
import collections
import statsmodels.api as sm
from numpy.linalg import inv
import itertools
# os.chdir(\\path\\to\\file)
from CreateFactorTable import CreateFactorTable
from FamaMacbethRegression import FamaMacbethRegression
import tqdm


#%% CLEAN DATA FINAL!!!
# - filter raw data
# - save it(only run once)
# - compute factors according to it
# - save it(only run once)

#%% file path
workingDir = "D:\\working space\\appliedEconometric_Project\\Merged raw data"
dataPath = "FundamentalData_Stock_MarketReturn_RiskFree.csv"

#%% read raw data
data = pd.read_csv(os.path.join(workingDir, dataPath), index_col = None,
                   converters = {"SID":str})

#%% get filter
# - condition1: trading days(2 filters)
# - condition2: time of on list: 1 filter

#filter trading less than 15 in past month
FUN_M_1=pd.DataFrame(data.groupby('SID').apply(lambda x: x["Trading_Status"].shift(1)))
FUN_M_1['Trading_Record'] = FUN_M_1['Trading_Status'] >= 15
FUN_M_2=pd.DataFrame(FUN_M_1.reset_index().sort_values(by = "level_1")["Trading_Record"])
data['Trading_Record_15']=FUN_M_2['Trading_Record']

#exclue firms having less than 120 trading records in the past year
Sum1=pd.DataFrame(data.groupby(['SID'])['Trading_Status'].rolling(window=12).sum())
Sum1['Trading_Status2'] = Sum1 > 120
Sum2=pd.DataFrame(Sum1.reset_index().sort_values(by = "level_1")["Trading_Status2"])
data['Trading_Record_120']=Sum2['Trading_Status2'] 


#exclude firms listed less than 6 month
FUN_M_4=pd.DataFrame(data.groupby(["SID"])["Trading_Month"].count())
FUN_M_4.reset_index(inplace = True)
FUN_M_4.rename(columns = {"Trading_Month":"Listing"}, inplace = True)
FUN_M_4['Listing']=FUN_M_4['Listing'] >= 6
data = pd.merge(data, FUN_M_4, how = "left", on = "SID")

#%% apply filter - 1 to data
data["Filter1"] = data["Trading_Record_120"]&data["Trading_Record_15"]&\
    data["Listing"]

data_Filter1 = pd.DataFrame(data[data["Filter1"] == 1])

#%% create factor table - before drop30 filter
# factor computation

# WARNING: takes a long time, return has been adjusted by risk free rate
FT = CreateFactorTable(data_Filter1)
FT.tidy_data()
FT.gen_DataFrame()
FT.buildDataFrame(["SID","Trading_Month","Trading_Date","Adj_Close_wDR","Tot_MV","Floating_MV"])
df_Factors = FT.applyMethod()

#%% cross sectional sorting and drop last 30 percent - apply ME filter -2
FT.labelBySortColumn("logME", num_split = 10)
df_dropLast30 = FT.get_DataFrame()[~FT.get_DataFrame()["labelled_logME"].isin([1,2,3])]
df_dropLast30.drop(columns = ["labelled_logME"], inplace = True)

#%% adjuest InvA term
df_dropLast30["InvestmentFactor"] = \
    df_dropLast30.groupby("SID").apply(lambda x: x["InvestmentFactor"].replace(to_replace=0, method='ffill')).reset_index().sort_values(by = "level_1")["InvestmentFactor"].values

df_Factors["InvestmentFactor"] = \
    df_Factors.groupby("SID").apply(lambda x: x["InvestmentFactor"].replace(to_replace=0, method='ffill')).reset_index().sort_values(by = "level_1")["InvestmentFactor"].values
#%% write to csv. ONLY ONCE
# df_dropLast30.to_csv(os.path.join(workingDir, "rawFactorTable_Filtered.csv"), index = False)
# df_Factors.to_csv(os.path.join(workingDir, "rawFactorTable_nonFiltered.csv"), index = False)

#%% create CH3 portfolio weighted by total market value - drop30
FT.set_DataFrame(df_dropLast30)
splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "EP":{"G":[10,20,30],"M":[40,50,60,70],"V":[80,90,100]}}
df_CH3_drop30_p1 = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")

splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "ROE":{"L_ROE":[10,20,30],"M_ROE":[40,50,60,70],"H_ROE":[80,90,100]}}
df_CH3_drop30_p2 = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")

splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "InvestmentFactor":{"L_InvA":[10,20,30],"M_InvA":[40,50,60,70],"H_InvA":[80,90,100]}}
df_CH3_drop30_p3 = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")

#%% create CH3 portfolio weighted by total market value - not drop30
FT.set_DataFrame(df_Factors)
splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "EP":{"G":[10,20,30],"M":[40,50,60,70],"V":[80,90,100]}}
df_CH3_p1 = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")

splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "ROE":{"L_ROE":[10,20,30],"M_ROE":[40,50,60,70],"H_ROE":[80,90,100]}}
df_CH3_p2 = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")

splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "InvestmentFactor":{"L_InvA":[10,20,30],"M_InvA":[40,50,60,70],"H_InvA":[80,90,100]}}
df_CH3_p3 = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")

#%% create VMG, SMB，CMA, RMW- drop 30
CH3factor_drop30 = pd.DataFrame(index = df_CH3_drop30_p1.index)
CH3factor_drop30["SMB"] = 1/3*df_CH3_drop30_p1[["S/V","S/M","S/G"]].sum(axis = 1) - \
    1/3*df_CH3_drop30_p1[["B/V","B/M","B/G"]].sum(axis = 1)
CH3factor_drop30["VMG"] = 1/2*df_CH3_drop30_p1[["S/V", "B/V"]].sum(axis=1) - \
    1/2*df_CH3_drop30_p1[["S/G","B/G"]].sum(axis=1)
CH3factor_drop30["RMW"] = 1/2*df_CH3_drop30_p2[["S/H_ROE","B/H_ROE"]].sum(axis=1) -\
    1/2*df_CH3_drop30_p2[["S/L_ROE", "B/L_ROE"]].sum(axis=1)
CH3factor_drop30["CMA"] = 1/2*df_CH3_drop30_p3[["S/L_InvA", "B/L_InvA"]].sum(axis=1) - \
    1/2*df_CH3_drop30_p3[["S/H_InvA", "B/H_InvA"]].sum(axis=1)
CH3factor_drop30["MKT"] = data.groupby("Trading_Month").last()["Market_Return"] - data.groupby("Trading_Month").last()["Risk_Free_Rate"]
# should save CH3factor_drop30

#%% create VMG, SMB, CMA, RMW
CH3factor = pd.DataFrame(index = df_CH3_p1.index)
CH3factor["SMB"] = 1/3*df_CH3_p1[["S/V","S/M","S/G"]].sum(axis = 1) - \
    1/3*df_CH3_p1[["B/V","B/M","B/G"]].sum(axis = 1)
CH3factor["VMG"] = 1/2*df_CH3_p1[["S/V", "B/V"]].sum(axis=1) - \
    1/2*df_CH3_p1[["S/G","B/G"]].sum(axis=1)
CH3factor["RMW"] = 1/2*df_CH3_p2[["S/H_ROE","B/H_ROE"]].sum(axis=1) -\
    1/2*df_CH3_p2[["S/L_ROE", "B/L_ROE"]].sum(axis=1)
CH3factor["CMA"] = 1/2*df_CH3_p3[["S/L_InvA", "B/L_InvA"]].sum(axis=1) - \
    1/2*df_CH3_p3[["S/H_InvA", "B/H_InvA"]].sum(axis=1)
CH3factor["MKT"] = data.groupby("Trading_Month").last()["Market_Return"] - data.groupby("Trading_Month").last()["Risk_Free_Rate"]
# should save CH3factor

#%% create another portfolio FF3 - drop 30
FT.set_DataFrame(df_dropLast30)
splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "logBM":{"L":[10,20,30],"M":[40,50,60,70],"H":[80,90,100]}}
df_FF3_drop30_p1 = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")

splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "ROE":{"L_ROE":[10,20,30],"M_ROE":[40,50,60,70],"H_ROE":[80,90,100]}}
df_FF3_drop30_p2 = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")

splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "InvestmentFactor":{"L_InvA":[10,20,30],"M_InvA":[40,50,60,70],"H_InvA":[80,90,100]}}
df_FF3_drop30_p3 = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")

#%% create another portfolio FF3 - not drop 30
FT.set_DataFrame(df_Factors)
splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "logBM":{"L":[10,20,30],"M":[40,50,60,70],"H":[80,90,100]}}
df_FF3_p1 = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")

splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "ROE":{"L_ROE":[10,20,30],"M_ROE":[40,50,60,70],"H_ROE":[80,90,100]}}
df_FF3_p2 = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")

splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "InvestmentFactor":{"L_InvA":[10,20,30],"M_InvA":[40,50,60,70],"H_InvA":[80,90,100]}}
df_FF3_p3 = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")

#%% create FF3 HML, SMB, CMA, RMW - drop 30
FF3factor_drop30 = pd.DataFrame(index = df_FF3_drop30_p1.index)
FF3factor_drop30["SMB"] = 1/3*df_FF3_drop30_p1[["S/H","S/M","S/L"]].sum(axis = 1) - \
    1/3*df_FF3_drop30_p1[["B/H","B/M","B/L"]].sum(axis = 1)
FF3factor_drop30["HML"] = 1/2*df_FF3_drop30_p1[["S/H", "B/H"]].sum(axis=1) -\
    1/2*df_FF3_drop30_p1[["S/L","B/L"]].sum(axis=1)
FF3factor_drop30["RMW"] = 1/2*df_FF3_drop30_p2[["S/H_ROE","B/H_ROE"]].sum(axis=1) -\
    1/2*df_FF3_drop30_p2[["S/L_ROE", "B/L_ROE"]].sum(axis=1)
FF3factor_drop30["CMA"] = 1/2*df_FF3_drop30_p3[["S/L_InvA", "B/L_InvA"]].sum(axis=1) - \
    1/2*df_FF3_drop30_p3[["S/H_InvA", "B/H_InvA"]].sum(axis=1)
FF3factor_drop30["MKT"] = data.groupby("Trading_Month").last()["Market_Return"] -\
    data.groupby("Trading_Month").last()["Risk_Free_Rate"]
# save FF3factor_drop30
    
#%% create FF3 HML, SMB, CMA, RMW - NOT drop 3-
FF3factor = pd.DataFrame(index = df_FF3_p1.index)
FF3factor["SMB"] = 1/3*df_FF3_p1[["S/H","S/M","S/L"]].sum(axis = 1) - \
    1/3*df_FF3_p1[["B/H","B/M","B/L"]].sum(axis = 1)
FF3factor["HML"] = 1/2*df_FF3_p1[["S/H", "B/H"]].sum(axis=1) -\
    1/2*df_FF3_p1[["S/L","B/L"]].sum(axis=1)
FF3factor["RMW"] = 1/2*df_FF3_p2[["S/H_ROE","B/H_ROE"]].sum(axis=1) -\
    1/2*df_FF3_p2[["S/L_ROE", "B/L_ROE"]].sum(axis=1)
FF3factor["CMA"] = 1/2*df_FF3_p3[["S/L_InvA", "B/L_InvA"]].sum(axis=1) - \
    1/2*df_FF3_p3[["S/H_InvA", "B/H_InvA"]].sum(axis=1)
FF3factor["MKT"] = data.groupby("Trading_Month").last()["Market_Return"] -\
    data.groupby("Trading_Month").last()["Risk_Free_Rate"]
# save FF3factor

#%% write csv ONLY RUN ONCE
# factorFilePath = "Computed factors"
# CH3factor.to_csv(os.path.join(workingDir, factorFilePath,"CH5_onlyFilterTradingDaysAndOnlist.csv"))
# FF3factor.to_csv(os.path.join(workingDir, factorFilePath,"FF5_onlyFilterTradingDaysAndOnlist.csv"))
# CH3factor_drop30.to_csv(os.path.join(workingDir, factorFilePath,"CH5_drop30_allFilterApplied.csv"))
# FF3factor_drop30.to_csv(os.path.join(workingDir, factorFilePath,"FF5_drop30_allFilterApplied.csv"))

#%% FMR regression
# -------------------------------------------------
# THE FOLLOWING ARE FMR!
#%% prepare a test data for famaMacbeth regression- a test example
df_reg = df_dropLast30.dropna()

FMR = FamaMacbethRegression(df_reg)
FMR.set_X(["beta","logME","EPplus","DEPsmaller0","logBM","CPplus","DCPsmaller0","logAM"])
FMR.set_Y(["monthlyReturn"])
factorPremium, tStat = FMR.run_FamaMacbethRegression()

#%% run group of fama macbeth regression
df_reg = df_dropLast30.dropna()

FMR = FamaMacbethRegression(df_reg)
Xgroup = [["beta","logME","EPplus","DEPsmaller0","logBM","CPplus","DCPsmaller0","logAM"],
          ["beta"],
          ["logME"],
          ["beta","logME"],
          ["beta","logME","logBM"],
          ["beta","logME","logAM"],
          ["beta","logME","EPplus","DEPsmaller0"],
          ["beta","logME","CPplus","DCPsmaller0"],
          ["beta","logME","logBM","EPplus","DEPsmaller0"]]
FMR.set_Y(["monthlyReturn"])
recorder = FMR.run_groupOfFamaMacbethRegression(Xgroup)

#%% read result in recorder
num = 0
simplified_result = collections.OrderedDict()
for k,v in recorder.items():
    aggData = []
    for val in v.columns:
        # if val =="EPplus" or val =="CPplus" or val == "logME":
        #     ss = np.quantile(v[val], 0.6)
        #     aggData.append(ss)
        # else:
        ss = np.median(v[val])
        aggData.append(ss)
    newDf = pd.DataFrame(index = v.columns, data = aggData)
    simplified_result[k] = newDf
    
#%%
# for k,v in simplified_result.items():
#     v.to_csv(os.path.join(workingDir, "FMR result simplified", "{}.csv".format(k)))

#%% write FMR reuslt to csv
# for k,v in recorder.items():
#     v.to_csv(os.path.join(workingDir, "FMR result", "{}.csv".format(k)))


#%% CH3 start !
from statsmodels.regression.rolling import RollingOLS
import scipy as sp

# prepare data - drop 30
#can be read from csv
factorData = CH3factor_drop30.loc["2000-07":]

# can be read from csv
stockReturnData = pd.DataFrame(df_dropLast30.sort_values(by = ["Trading_Month"],ascending = True)[["SID","Trading_Month","monthlyReturn"]])

stockReturnData.set_index("Trading_Month", inplace = True)
stockReturnData = stockReturnData.loc["2000-07":]
stockReturnData.reset_index(inplace = True)

# merge data
factorData.reset_index(inplace = True)
data_rollingReg = pd.merge(stockReturnData, factorData, how = "left",
                           left_on = "Trading_Month", right_on = "index")
#%% write csv
# data_rollingReg.to_csv(os.path.join(workingDir, "data_rollingReg_drop30.csv"), index = False)

#%% run rolling regression
def rollingRegressionWrap(X_colName = ["VMG","MKT"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg, refData = stockReturnData, refCol = ["SID"]):
    #init valid SID and invalid SID
    invalid_SID = []
    
    # give variable
    # X_colName = ["VMG","MKT"]
    # Y_colName = ["monthlyReturn"]
    
    SID_list = np.unique(refData[refCol])
    
    # run rolling regression
    newColNames = ["Trading_Month", "SID", "adjusted_rSquared", "JB_pValue"]
    
    t_StatCol = [val + "_t_Stat" for val in X_colName]
    
    newColNames.extend(t_StatCol)
    newColNames.extend(X_colName)
    
    rollingResult_df = pd.DataFrame(columns = newColNames)
    
    progress_bar = tqdm.tqdm(SID_list)
    for asset in progress_bar:
        try:
            # add SID column
            subDataSet = pd.DataFrame(data_rollingReg[data_rollingReg["SID"]==asset])
            Y = subDataSet[Y_colName]
            X = sm.add_constant(subDataSet[X_colName])
            
            Trading_Month = subDataSet["Trading_Month"].values
            SIDs = subDataSet["SID"].values
            JB_pval = subDataSet.rolling(36)["monthlyReturn"].apply(lambda var: sp.stats.jarque_bera(var)[1]).values
            subReg = RollingOLS(Y,X, window = 36, missing = "drop").fit()
            rSquared_adj = subReg.rsquared_adj.values
            t_Stat = subReg.tvalues.values
            params = subReg.params.values
            
            dataDf = np.hstack([SIDs[...,np.newaxis], 
                                Trading_Month[...,np.newaxis], 
                                rSquared_adj[...,np.newaxis], 
                                JB_pval[...,np.newaxis], 
                                params[:,1:], 
                                t_Stat[:,1:]])
            
            assetDf = pd.DataFrame(data = dataDf, columns = newColNames)
            rollingResult_df = pd.concat([rollingResult_df, assetDf], ignore_index = True)
        except:
            # print(asset + ": {} trading months".format(Y.shape[0]))
            invalid_SID.append([asset, Y.shape[0]])
            
        progress_bar.set_description(f'Processing {asset}')
            
    return(rollingResult_df,invalid_SID)

#%% run the rolling regression, drop 30
CH3_rolling_MKT_drop30, _= rollingRegressionWrap(X_colName = ["MKT"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg)
CH3_rolling_MKT_SMB_drop30, _= rollingRegressionWrap(X_colName = ["MKT","SMB"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg)
CH3_rolling_MKT_VMG_drop30, _= rollingRegressionWrap(X_colName = ["MKT","VMG"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg)
CH3_rolling_MKT_SMB_VMG_drop30, _= rollingRegressionWrap(X_colName = ["MKT","SMB", "VMG"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg)
CH3_rolling_3factor_CMA_drop30, _= rollingRegressionWrap(X_colName = ["MKT","SMB", "VMG", "CMA"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg)
CH3_rolling_3factor_RMW_drop30, _= rollingRegressionWrap(X_colName = ["MKT","SMB", "VMG", "RMW"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg)
CH3_rolling_5factor_drop30, _= rollingRegressionWrap(X_colName = ["MKT","SMB", "VMG", "CMA", "RMW"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg)

# %% merge data and run non-drop 30
factorData_nonDrop30 = CH3factor.loc["2000-07":]

# can be read from csv
stockReturnData_nonDrop30 = pd.DataFrame(df_Factors.sort_values(by = ["Trading_Month"],ascending = True)[["SID","Trading_Month","monthlyReturn"]])

stockReturnData_nonDrop30.set_index("Trading_Month", inplace = True)
stockReturnData_nonDrop30 = stockReturnData_nonDrop30.loc["2000-07":]
stockReturnData_nonDrop30.reset_index(inplace = True)

# merge data
factorData_nonDrop30.reset_index(inplace = True)
data_rollingReg_nonDrop30 = pd.merge(stockReturnData_nonDrop30, factorData_nonDrop30, how = "left",
                                     left_on = "Trading_Month", right_on = "index")

#%% write csv
# data_rollingReg_nonDrop30.to_csv(os.path.join(workingDir, "data_rollingReg_nonDrop30.csv"), index = False)

# %% run rolling agaion- not drop 30
CH3_rolling_MKT, _= rollingRegressionWrap(X_colName = ["MKT"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg_nonDrop30)
CH3_rolling_MKT_SMB, _= rollingRegressionWrap(X_colName = ["MKT","SMB"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg_nonDrop30)
CH3_rolling_MKT_VMG, _= rollingRegressionWrap(X_colName = ["MKT","VMG"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg_nonDrop30)
CH3_rolling_MKT_SMB_VMG, _= rollingRegressionWrap(X_colName = ["MKT","SMB", "VMG"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg_nonDrop30)
CH3_rolling_3factor_CMA, _= rollingRegressionWrap(X_colName = ["MKT","SMB", "VMG", "CMA"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg_nonDrop30)
CH3_rolling_3factor_RMW, _= rollingRegressionWrap(X_colName = ["MKT","SMB", "VMG", "RMW"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg_nonDrop30)
CH3_rolling_5factor, _= rollingRegressionWrap(X_colName = ["MKT","SMB", "VMG", "CMA", "RMW"],Y_colName = ["monthlyReturn"],data_rollingReg= data_rollingReg_nonDrop30)

#%% write csv
# CH3_rolling_MKT_drop30.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_MKT_drop30.csv"), index = False)
# CH3_rolling_MKT_SMB_drop30.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_MKT_SMB_drop30.csv"), index = False)
# CH3_rolling_MKT_VMG_drop30.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_MKT_VMG_drop30.csv"), index = False)
# CH3_rolling_MKT_SMB_VMG_drop30.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_MKT_SMB_VMG_drop30.csv"), index = False)
# CH3_rolling_3factor_CMA_drop30.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_3factor_CMA_drop30.csv"), index = False)
# CH3_rolling_3factor_RMW_drop30.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_3factor_RMW_drop30.csv"), index = False)
# CH3_rolling_5factor_drop30.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_5factor_drop30.csv"), index = False)

# CH3_rolling_MKT.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_MKT.csv"), index = False)
# CH3_rolling_MKT_SMB.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_MKT_SMB.csv"), index = False)
# CH3_rolling_MKT_VMG.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_MKT_VMG.csv"), index = False)
# CH3_rolling_MKT_SMB_VMG.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_MKT_SMB_VMG.csv"), index = False)
# CH3_rolling_3factor_CMA.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_3factor_CMA.csv"), index = False)
# CH3_rolling_3factor_RMW.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_3factor_RMW.csv"), index = False)
# CH3_rolling_5factor.to_csv(os.path.join(workingDir,"CH3 result","CH3_rolling_5factor.csv"), index = False)

#%% summary statistics
CH3_rolling_3factor_CMA.info()
