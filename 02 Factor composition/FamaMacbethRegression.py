import numpy as np
import pandas as pd
import collections
import statsmodels.api as sm
import statsmodels.formula.api as smf
from numpy.linalg import inv
import itertools
import tqdm

class FamaMacbethRegression(object):
    def __init__(self, data):
        self.data = data
        
    def set_data(self, newdata):
        self.data = newdata
        
    def get_data(self):
        return self.data
    
    def set_X(self, columnNames):
        self.X_col_step1 = columnNames
        
    def set_Y(self, columnName):
        self.Y_col_step1 = columnName
        
    def compute_factorPremiumEstimation(self, result):
        return(result.values.mean(axis = 0))
    
    def compute_tStat(self, result):
        MEAN = result.values.mean(axis = 0)
        STD = result.values.std(axis = 0)
        T = result.shape[0]
        return(MEAN/(STD/T**0.5))
        
    def compute_factorExpousre(self, classifyBy = "SID", NW_lags = 4):
        
        # init data
        X_col_step1 = self.X_col_step1
        Y_col_step1 = self.Y_col_step1
        df_reg = self.get_data()
        
        # init variable
        betaMatrix = []
        valid_SID = []
        invalid_SID = []
        
        # init classify
        SID_list = np.unique(df_reg[classifyBy])
        
        # run #assets times regression for T time period
        progress_bar = tqdm.tqdm(SID_list)
        for asset in progress_bar:
            try:
                dataStep1Sub = df_reg[df_reg[classifyBy] == asset]
                formula = Y_col_step1[0] + "~1+" + "+".join(X_col_step1)
                reg = smf.ols(formula, data=dataStep1Sub).fit(cov_type='HAC',cov_kwds={'maxlags':NW_lags})
                # factor = np.mat(dataStep1Sub[X_col_step1].values)
                # rts = np.mat(dataStep1Sub[Y_col_step1].values)
                # constantCol = np.ones((rts.shape[0],1))
                # X = np.hstack((constantCol, factor))
                # betaMatrix.append(sm.OLS(rts, X).fit().params[:].tolist())
                betaMatrix.append(reg.params.values.tolist())
                valid_SID.append(asset)
            except:
                invalid_SID.append(asset)

            #print progress bar
            progress_bar.set_description(f'step1 regression: Processing {asset}')
        
        X_col_names = [0]*(len(X_col_step1)+1)
        X_col_names[0] = "Intercept"
        X_col_names[1:] = X_col_step1

        self.validStep1Filter = valid_SID
        self.factorExposure = pd.DataFrame(index = valid_SID, data = betaMatrix, columns = X_col_names)
        
        return
    
    def compute_factorPremium(self, classifyBy = "Trading_Month", step1ClassifyBy = "SID", NW_lags = 4):
        
        #init data
        X_col_step1 = self.X_col_step1
        Y_col_step1 = self.Y_col_step1
        valid_SID = self.validStep1Filter
        df_reg = self.get_data()
        betaDf = self.factorExposure
        
        # init variables
        lambdaMatrix = []
        valid_Dates = []
        invalid_Dates = []
        t_statList = []
        
        # init classification
        Dates_list = np.unique(df_reg[classifyBy])
        
        progress_bar = tqdm.tqdm(Dates_list)
        for date in progress_bar:
            try:
                SID_byDate = set(df_reg[df_reg[classifyBy] == date][step1ClassifyBy].values)
                valid_SID_byDate = set(valid_SID).intersection(SID_byDate)
                dataStep2Sub = pd.DataFrame(betaDf.loc[betaDf.index.isin(valid_SID_byDate),:])
                Y = df_reg[np.logical_and(df_reg[classifyBy] == date,
                           df_reg[step1ClassifyBy].isin(valid_SID_byDate))][Y_col_step1].values
                dataStep2Sub[Y_col_step1[0]] = Y
                formula = Y_col_step1[0] + "~1+" + "+".join(X_col_step1)
                reg = smf.ols(formula, data=dataStep2Sub).fit(cov_type='HAC',cov_kwds={'maxlags':NW_lags})
                # Y = np.mat(df_reg[np.logical_and(df_reg[classifyBy] == date,
                #                           df_reg[step1ClassifyBy].isin(valid_SID_byDate))][Y_col_step1].values)
                # X = np.mat(betaDf.loc[betaDf.index.isin(valid_SID_byDate),:].values)
                # aLambda = inv(X.T@X)@(X.T@Y).tolist()
                # lambdaMatrix.append(aLambda.T.tolist()[0])
                lambdaMatrix.append(reg.params.values.tolist())
                t_statList.append(reg.tvalues.values.tolist())
                valid_Dates.append(date)
            except:
                invalid_Dates.append(date)

            # progress bar
            progress_bar.set_description(f'step2 regression: Processing {date}')

        newColNames = [0]*(len(X_col_step1)+1)
        newColNames[0] = "Intercept"
        newColNames[1:] = X_col_step1
                
        self.factorPremium = pd.DataFrame(index = valid_Dates, data = lambdaMatrix, columns = newColNames)
        self.NW_t_stat = pd.DataFrame(index = valid_Dates, data = t_statList, columns = newColNames)
        
    def run_FamaMacbethRegression(self, step1ClassifyBy = "SID", step2ClassifyBy = "Trading_Month", NW_lags = 4):
        # return a dataframe
        self.compute_factorExpousre(classifyBy = step1ClassifyBy, NW_lags= NW_lags)
        self.compute_factorPremium(classifyBy = step2ClassifyBy, step1ClassifyBy = step1ClassifyBy, NW_lags= NW_lags)
        
        return(self.factorPremium, self.NW_t_stat)
    
    def run_groupOfFamaMacbethRegression(self, Xgroups, step1ClassifyBy = "SID", step2ClassifyBy = "Trading_Month", NW_lags = 4):
        recorder = collections.OrderedDict()
        for groupNum in range(len(Xgroups)):
            print("progress: {}/{}".format(groupNum+1, len(Xgroups)))
            print("")
            self.set_X(Xgroups[groupNum])
            recorder["group"+str(groupNum)+"_pointEstimation"], recorder["group"+str(groupNum)+"_tStat"]= \
                self.run_FamaMacbethRegression(step1ClassifyBy, step2ClassifyBy, NW_lags=NW_lags)    
            
        return(recorder)            