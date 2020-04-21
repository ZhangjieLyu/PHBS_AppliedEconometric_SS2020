# PHBS_AppliedEconometric_SS2020
Codes, examples, data and replications of our results



## Data

[link to raw data](https://drive.google.com/drive/folders/1whZRbL03pNZ8LJYGOIpiKf0VRFgaUYsv?usp=sharing)

source: CSMAR

details: view description of separate files

structure:

- stock trading data monthly
- balance sheet variables
- cash-flow statement variables 
- income statement variables
- delist and suspension porfiles
- onlist profiles
- risk-free rate
- announcement date of financial reports
- stock trading data daily
- market return



[link to factor value data(VMG, SMB etc.)](https://drive.google.com/drive/folders/1VUM1wWvsm7nz5Ln7gUVHAowZw599OYZE?usp=sharing)

source: computation

structure:

+ CH 5 drop 30
+ CH5 non-drop 30
+ FF5 drop 30
+ FF5 non-drop 30



## Codes - Data cleaning

[link to codes of data cleaning](https://drive.google.com/drive/folders/1At9v4x0s2aLl1KxnVGAltrNSqmbfwhf-?usp=sharing)



## Codes - Factor computation

### Guidelines 

Author: Robert

Last Update Date: Apr.18

#### Installation

After my consideration, the modules are not packed into a package, which makes the installation a little bit complicated.

**First**, check your working directory and Python version with

```Python
import os
import pandas as pd

print("current working dir:"+os.getcwd())
print(pd.__version__)
```

The module is built under pandas v1.0.3 and Python v3.7.4.

**Second**, drag three documents `ConstructFactors.py`,`CreateFatorTable.py`,`FamaMacbethRegression.py` under your working directly(the same fold as `os.getcwd()`)

**Third**, import them with following lines of codes:

```Python
from CreateFactorTable import CreateFactorTable
from FamaMacbethRegression import FamaMacbethRegression
```

**Done!**



#### Examples

##### Read example data into your RAM

```Python
data = pd.read_csv("YourFilePath", converters = {"SID":str})

# random sample 10 obs to check the data
data.sample(10)
```

**Note:** don't forget to import your favorite libraries:

```Python
# your favorite libraries:
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import os
import collections
import statsmodels.api as sm
from numpy.linalg import inv
import itertools
```



##### Create factor table

Since the way how factors are constructed are pre-defined and not equipped with methods to be modified from outside, the only thing you need to do is calling methods to compute factor values. If needed, will introduce method to allow people define their own factors from outside.

**WARNING: take a long time, $\beta$ is computed based on one-year deposit rate(converted to monthly) adjusted market return&stock return**

```Python
# init a CreateFactorTable object with your data
FT = CreateFactorTable(data)

# call method to tidy data and generate frame for storing data
FT.tidy_data()
FT.gen_DataFrame()

# call method to tell CreateFactorTable which columns should be inherited from your data(the one you used to init the object),you can use your variable viewer or call `data.columns` to see columns in your data
FT.buildDataFrame(["SID","Trading_Month","Trading_Date","Adj_Close_wDR","Tot_MV","Floating_MV"])

# apply pre-defined computation
df_Factors = FT.applyMethod()
```



##### Let the object do the cross-sectional sorting for you

*what is a cross-sectional sorting?*

cross-sectional sorting(here) is to sort a variable in ascending order according to its value on each cross-section. e.g. if there're $T$ time period, $N$ assets on each cross section, the cross-sectional sorting will do $T$ times sorting on $N$ assets of each cross section. Note: $N$ can be a function of $T$, means $N$ is not bound to be a constant.

```Python
# continue the object you have initialized in the previous code chunk

# "logME" can be any numerical column, num_split is to tell the object how many splits(equally divided) you would like to get, and these sorting will skip nan.
FT.labelBySortColumn("logME", num_split = 10)

# check the effect of cross-sectional sorting, the column is named after "labelled_logME", sorting is in an ascending order!
FT.get_DataFrame()
```



##### Create Pure Long Portfolios Returns

*what is a 'pure long portfolio return' mean here?*

A portfolio return here follows the classic definition of Fama&French, e.g. one decides to construct a long portfolio means he/she would like to buy a basket of stocks, and here the module can help you calculate the **total market value weighted** return of the a given type of basket. *The given type* of basket here is defined by double cross-sectional sorting, for example, it can be a long portfolio from top 50% market value(which is "B"/Big type in FF 3 factor), from top 30% BM(which is "V"/Value type in FF 3 facto), and name it "B/V", that exactly what this method is doing

```Python
# define a split structure by "Tot_MV"(Total Market Value) and "EP", define "S"(small) group in "Tot_MV" to be the companies with [10,20,30,40,50], where "10" means smallest(in value) 10%, 20 means samllest 10%-20% etc.
splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "EP":{"G":[10,20,30],"M":[40,50,60,70],"V":[80,90,100]}}

# construct long portfolio, set stock return column to be "monthlyReturn"
df_testPort = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")
```

**Yet another example**

```Python
# this is a 3 x 3 long portfolio, make sure the second key("EP" here) has a split number(here is 3) not smaller than the first key(here is "Tot_MV")
splitStr = {"Tot_MV":{"S":[10,20,30,40,50],"B":[60,70,80,90,100]}, "EP":{"G":[10,20,30],"M":[40,50,60,70],"V":[80,90,100]}}

df_testPort = FT.constructPortfolioBySortedColumns(splitStr,"monthlyReturn")
```



##### Fama-Macbeth regression

*To make example looks better, let's drop nan first, but in reality, the number of nan is close to 0 after stock filter*.

```Python
# dropna
df_reg = df_Factors.dropna()
```

**One-time Fama-Macbeth regression**

**NOTE:** t statistics here is computed by Newey-West adjusted t stat, with 4 lags

```Python
# init a FamaMacbethRegression object with df_reg(the data, in pandas.DataFrame format)
FMR = FamaMacbethRegression(df_reg)

# set your X columns(from columns of df_reg, again, use data viewer or df_reg.columns)
FMR.set_X(["beta","logME","EPplus","DEPsmaller0","logBM","CPplus","DCPsmaller0","logAM"])

# set your Y
FMR.set_Y(["monthlyReturn"])

# run regression
FMR.run_FamaMacbethRegression()

# check your factor premium
FMR.factorPremium

# compute estimation
FMR.compute_factorPremiumEstimation(FMR.factorPremium)
```

**run Fama-Macbeth regression for a group of X**

```Python
# define a group of Xs, here Xgroup variable has 4 groups of X
Xgroup = [["beta","logME","EPplus","DEPsmaller0","logBM","CPplus","DCPsmaller0","logAM"],
          ["beta"],
          ["logME"],
          ["beta","logME"]]

# run it!
recorder = FMR.run_groupOfFamaMacbethRegression(Xgroup)
```

**the result is saved in a ordered dictionary**



## Codes - realization of generating L/S portfolio(i.e.VMG etc.) and statistical testing

View github's corresponding parts

