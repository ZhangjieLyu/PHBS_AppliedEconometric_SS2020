# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 19:29:16 2020

@author: Robert
"""
#%% import library
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import collections

#%% set path
workingDir = "D:\\working space\\appliedEconometric_Project\\rawData"
balSheet = "Balance sheet variables\\FS_Combas.csv"
iS = "Income statement variables\\FS_Comins.csv"
cF = "Cash-flow statement variables\\FS_Comscfi.csv"

#%% read balance sheet
balSheet_rawDf = pd.read_csv(os.path.join(workingDir, balSheet), 
                             converters = {"Stkcd":str})
balSheet_rawDf['Accper'] = pd.to_datetime(balSheet_rawDf['Accper'], 
                                          format = "%Y-%m-%d")

# rename columns
bS_colName = ["SID","Accper","TypeRep","Monetary_Cap","Tradable_Fin_Assets",
              "Tot_Cur_Assets", "Tot_Assets","ST_Borrowing","Tradable_Fin_Liab",
              "Notes_Payable","Taxes_Sur_Payable","Non_Cur_Liab_DueIn1Y",
              "Tot_Cur_Liab","LT_Liab","Min_Int","Tot_SE"]

balSheet_rawDf.columns = bS_colName

# drop redundant cols
balSheet_rawDf.drop(columns=['TypeRep'], inplace = True)

# sort by date
balSheet_rawDf.sort_values(by = ['Accper','SID'], inplace = True, ascending = [True, True])

# reset index
balSheet_rawDf.reset_index(inplace = True)
balSheet_rawDf.drop(columns=['index'], inplace = True)

#%% read income statement
incomeStatement_rawDf = pd.read_csv(os.path.join(workingDir, iS), 
                                    converters = {"Stkcd":str})
incomeStatement_rawDf['Accper'] = pd.to_datetime(incomeStatement_rawDf['Accper'], 
                                                 format = "%Y-%m-%d")

# rename colns
iS_colName = ["SID", "Accper", "TypeRep", "Net_Profit", "Min_Int_Inc"]

incomeStatement_rawDf.columns = iS_colName

# drop and re-orgnize
incomeStatement_rawDf.sort_values(by = ['Accper', 'SID'], inplace = True, ascending = [True, True])
incomeStatement_rawDf.reset_index(inplace = True)
incomeStatement_rawDf.drop(columns = ["index","TypeRep"], inplace = True)

#%% read cash flow statement
cashFlowStatement_rawDf = pd.read_csv(os.path.join(workingDir, cF),
                                      converters = {"Stkcd":str})
cashFlowStatement_rawDf['Accper'] = pd.to_datetime(cashFlowStatement_rawDf['Accper'],
                                                   format = "%Y-%m-%d")

# rename colns
cF_colName = ["SID","Accper","TypeRep","Depr_FA_COGA_DPBA", "Amort_Intang_Assets",
              "Cash_At_End", "Cash_At_Begin","Cash_Equ_End", "Cash_Equ_Begin"]

cashFlowStatement_rawDf.columns = cF_colName

# drop and re-orgnize
cashFlowStatement_rawDf.sort_values(by = ['Accper', 'SID'], inplace = True, ascending = [True, True])
cashFlowStatement_rawDf.reset_index(inplace = True)
cashFlowStatement_rawDf.drop(columns = ["index", "TypeRep"], inplace = True)

#%% clean data - balance sheet

# note: special obs: XXXX-01-01 and XXXX-12-31
# XXXX-01-01 is a minor review of the previous term, tend to drop XXXX-01-01 because
# we don't know when we can get the adjustment

# current asset's absence may result from a consequence of different industry,
# see 600030(CITI securities) vs. 002415(HKVI, a manufacturer) for example.

# give up cleaning, no good solution

# set Minority interest to be 0 if it is nan
balSheet_rawDf["Min_Int"] = balSheet_rawDf["Min_Int"].fillna(0)

# compute new variable
balSheet_rawDf["Tot_SE_After_Min_Int"] = balSheet_rawDf["Tot_SE"] - \
    balSheet_rawDf["Min_Int"]
#%% clean data - income statement
# 4 obs with net profit = 0(their Min-Int-Inc are also 0)
# 1 obs with unknown net profit, but non-zero Min-Int-Inc
# if Min-Int-Inc is null, assume to be 0
# further WIN.D: no obs of operating cost, but has record of net profit 
incomeStatement_rawDf.at[8668, "Net_Profit"] = 4664929.85
incomeStatement_rawDf.fillna(0, inplace = True)

# compute Net_Profit_After_Min_Int_Inc
incomeStatement_rawDf["Net_Profit_After_Min_Int_Inc"] = incomeStatement_rawDf["Net_Profit"] -\
    incomeStatement_rawDf["Min_Int_Inc"]
    
# checked: Net_Profit_After_Min_Int_Inc no null value
    
#%% clean data - cash flow statement
# this is a quarter data

# fill cash equvalence with 0
# cashFlowStatement_rawDf[["Cash_Equ_Begin", "Cash_Equ_End"]].fillna(0, inplace = True)

# fill Amortization of intangible assets with ffill
# cashFlowStatement_rawDf["SID_copy"] = cashFlowStatement_rawDf["SID"]
# cashFlowStatement_rawDf["Amort_Intang_Assets"] = \
#      cashFlowStatement_rawDf.groupby(["SID"])["Amort_Intang_Assets"].apply(lambda x: x.fillna(method = 'ffill')) #FIXME: should be groupby first

# fill nan in cash equ with 0
# cashFlowStatement_rawDf[["Cash_Equ_End", "Cash_Equ_Begin"]] = \
#     cashFlowStatement_rawDf[["Cash_Equ_End", "Cash_Equ_Begin"]].fillna(0)
    
# use nansum to build new variable
# compute new variable
cashFlowStatement_rawDf['Cash_Cash_Equ_Begin'] = cashFlowStatement_rawDf[["Cash_At_Begin","Cash_Equ_Begin"]].sum(axis = 1)
    
cashFlowStatement_rawDf['Cash_Cash_Equ_End'] = cashFlowStatement_rawDf[["Cash_At_End","Cash_Equ_Begin"]].sum(axis = 1)

# checked: no null for new variables

#%% merge - step 1. drop date of "XXXX-01-01"

# clean balance sheet
bS_colName_left = ["SID","Accper","Monetary_Cap","Tradable_Fin_Assets",
                   "Tot_Cur_Assets", "Tot_Assets","ST_Borrowing","Tradable_Fin_Liab",
                   "Notes_Payable","Taxes_Sur_Payable","Non_Cur_Liab_DueIn1Y",
                   "Tot_Cur_Liab","LT_Liab","Min_Int","Tot_SE_After_Min_Int"]
    
balSheet_dfForMerge = pd.DataFrame(balSheet_rawDf[np.logical_or(balSheet_rawDf["Accper"].dt.month!=1,
                                                                balSheet_rawDf["Accper"].dt.day!=1)][bS_colName_left])

# clean income statement sheet
iS_colName_left = ["SID", "Accper", "Net_Profit_After_Min_Int_Inc"]

incomeStatement_dfForMerge = pd.DataFrame(incomeStatement_rawDf[np.logical_or(
    incomeStatement_rawDf["Accper"].dt.month!=1,
    incomeStatement_rawDf["Accper"].dt.day!=1)][iS_colName_left])

# clean cash-flow statement sheet
cF_colName_left = ["SID","Accper","Depr_FA_COGA_DPBA", "Amort_Intang_Assets",
              "Cash_Cash_Equ_Begin", "Cash_Cash_Equ_End"]

cashFlowStatement_dfForMerge = pd.DataFrame(cashFlowStatement_rawDf[np.logical_or(
    cashFlowStatement_rawDf["Accper"].dt.month!=1,
    cashFlowStatement_rawDf["Accper"].dt.day!=1
    )][cF_colName_left])

#%% merge - step 2. merge tables by SID and Accper
# 3211 companies in all

# merge with style 'outer'
bal_iS = pd.merge(balSheet_dfForMerge, incomeStatement_dfForMerge,
                  how = "outer", on = ["SID","Accper"])

FA_fullyOuterMerge = pd.merge(bal_iS, cashFlowStatement_dfForMerge,
                              how = "outer", on = ["SID", "Accper"])

#%% process asOf_Date
# after proceesing financial reports, the next step is to mark financial report
# with the announcement date, so that we can clearly know when the data is avaiable
# for computation

annDate_filePath = "Announcement date of financial reports\\IAR_Rept.csv"
annDate_rawDf = pd.read_csv(os.path.join(workingDir, annDate_filePath),
                            converters = {"Stkcd":str})
annDate_rawDf["Accper"] = pd.to_datetime(annDate_rawDf["Accper"],
                                         format = "%Y-%m-%d")
annDate_rawDf["Annodt"] = pd.to_datetime(annDate_rawDf["Annodt"],
                                         format = "%Y-%m-%d")

# rename colns
initName_annDate_rawDf = annDate_rawDf.columns.values
initName_annDate_rawDf[0] = "SID"
annDate_rawDf.columns = initName_annDate_rawDf

# drop stockname coln
annDate_rawDf.drop(columns = ["Stknme"], inplace = True)

# sort by date
annDate_rawDf.sort_values(by = ['Accper','SID'], inplace = True, ascending = [True, True])

# reset index
annDate_rawDf.reset_index(inplace = True)
annDate_rawDf.drop(columns=['index'], inplace = True)
#%% merge Annodt with data

# sort FA before merge
FA_fullyOuterMerge.sort_values(by = ['Accper','SID'], inplace = True, ascending = [True, True])

# outer merge
FA_with_asOf_Date = pd.merge(FA_fullyOuterMerge, annDate_rawDf,
                             how = "outer", on = ["SID", "Accper"])

#%% check data with no announcement date and fill raw data
data_NoAnnDate = FA_with_asOf_Date[pd.isnull(FA_with_asOf_Date["Annodt"])]
col_despTime = [["SID","Accper","Reptyp", "Annodt"]]

# decide to leave it empty

#%% write into csv, and then move to cleaning the stock trading data
# Note: the data including fundamental data and stock trading data, they're
# all factors(float), after processing factors, we will then move to the processing
# of Filters(Bool) & Classifiers(str or int)
FA_with_asOf_Date.to_csv(os.path.join(workingDir, "FundamentalData_AsOfDate.csv"))