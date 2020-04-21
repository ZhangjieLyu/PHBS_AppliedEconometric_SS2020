# Executive summary -- data 

author: Robert

latest revised date: Apr.14/2020

environment: Python 3.7.4, Pandas 1.0.3



## General description

+ To estimate the size of raw data: Jan 2000 - Dec 2016 = 17yrs, approx. 252 trading days/yr, approx. 3000 stocks in SH + SZ stock market, approx. 30 features, approx. 6 bytes for each entry => **estimated data size** = 2,313,360,000‬ bytes $\approx$ 2.15GB.

+ To estimate the size of cleaned data: Jan 2000 - Dec 2016 = 17yrs, approx. 12 months/yr, approx. 2000 stocks in SH + SZ stock market, approx. 30 features, approx. 6 bytes for each entry => **estimated data size** $\approx$  0.1GB = 100MB.

+ To eliminate 'survivorship bias', the stocks list is selected in advance, which contains all stocks that ever existed in the A share - Shanghai stock exchange & Shenzhen stock exchange during the *data time period*.
+ Data time period: **Jan. 2000 - Dec.2016**(*note*: some data is empty for Dec.2016)
+ Multiple way of organizing data:
  + pandas(Python lib)'s data structure: panel/multi-index data frame
  + use one csv file for one feature/one stock

It's important to make sure all data is comparable and this file is describing the steps that makes data comparable.



## About fundamental data

For company's fundamental data, all data is of unit 1 RMB.

The dataset from CSMAR has 2 records in the end of the year, they are XXXX-12-31 and XXXX-01-01, and XXXX-01-01 is a minor review of the XXXX-12-31. But here, only data of XXXX-12-31 is used, because don't have the exact announcement date of XXXX-01-01. 

**Income statement variables**

**Assumption:** if minority interest income(Chinese:少数股东损益) is missing, assume them to be zero.



**Balance sheet variables**

**Assumption:** if minority interest(Chinese:少数股东权益) is missing, assume them to be zero.

For other items, Missing not processed, remain missing data to be NaN



**Cash flow statement variables**

**Process:** use np.nansum to process cash + cash equivalence 

Missing not processed, remain missing data to be NaN



**"As of date" tag**

To avoid "look-ahead bias", all data are tagged with its "announcement date of financial report". And the fundamental data will be updated right in the month of announcement because the fundamental data is known in the end of the announcement month.



## About stock trading data

Use daily data to make a monthly data, adj. close price is adjusted based on the last trading day before the ex-right date.(Chinese: 后复权)

**When composite daily trading data to monthly trading data**

*Trading Volume*: sum over a month

*Floating market value*: use the data in the end of the month

*Total market value*: use the data in the end of the month

*Adjusted month close price with cash dividend reinvested(count cash dividend into the return)*: last observation in a month

*Adjusted month close price without cash dividend reinvested(doesn't count cash dividend in to the return)*: last observation in a month

*Trading status*: sum over trading days whose trading volume > 0 over the past one month.

**Assumption:** holding period of an asset will be from the last trading day's market close to current trading day's market close( = intraday return + overnight return), indicating the L/S portfolio are always exposed to overnight risk which cannot be hedged unless one use T+0 or intraday trading(which is not in the range of discussion).



## Data merge

use exact **outer** logic to avoid loss of data when merge fundamental data

use **left/right** logic to merge fundamental data with trading data and drop duplicates to preserve the consistency of data set.

**Notes**: when fundamental data duplicates with respect to stock ID and announcement month, only use the latest data(keep the last duplicated observation)[**Assumption**]



**Very Important**:

must be aware of the **close price** in the paper. When calculating fundamental indicator, one **MUST** use real value of close price at specific time point instead of any adjusted one!