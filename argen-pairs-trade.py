
# coding: utf-8

# # Seminar paper: Pairs trading

# #### Author: Alexander Franz

# In[26]:

# Import important packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import pytz
from datetime import datetime
import zipline as zp
import itertools

import pandas_datareader.data as web

import pickle


# In[35]:

# Create a list of all ticker symbols of the DAX30 companies

aktien = []

kurz = []


import csv
with open('companylist.csv', 'rb') as csvfile:
     spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
     c = 0
     for row in spamreader:
         c += 1
         if c==1:
             continue
         print ', '.join(row)
         aktien.append( row[1].strip('\n') )
         kurz.append( row[0].strip('\n') )


# Adds the .DE appendix to the list, needed for Yahoo Finance quotes

kurzde = [] 
for i in kurz:
    d = i.strip() #+ ".AR"
    print d
    kurzde.append(d)
 
dax = pd.DataFrame({'company' : aktien, 'ticker' : kurz})


# In[36]:

dax


# In[5]:

# Getting the Data from Yahoo Finance, using the stocks from the "kurzde" list, as Yahoo needs the .DE appendix for German stocks.

#trainStartDate = datetime(2005, 1, 1)
#trainEndDate = datetime(2014, 12, 30)

def grabData( tickers, startDate, endDate ):

    import pandas_datareader.data as web

    ticker = tickers[0]
    data1 = web.DataReader(ticker.strip('\n'), "yahoo", startDate, endDate )
    data1 = data1['Close']
    data1.name = ticker
    print data1.head()
    
    result = data1
    for ticker in tickers[1:]:
        print 'TICKER = ',ticker
        #import time
        #time.sleep(5.0)
        data2 = web.DataReader(ticker.strip('\n'), "yahoo", startDate, endDate)
        data2 = data2['Close']
        data2.name = ticker
        print data2.head()
        result = pd.concat([result, data2], axis=1, join_axes=[result.index])
        print result.head() 
    return result   

#data = grabData(tickers=kurzde, startDate=trainStartDate, endDate=trainEndDate)


try:
    pkl_file = open('data.pkl', 'rb')
    data = pickle.load(pkl_file)
except:    
    start = datetime(2013, 1, 1, 0, 0, 0, 0, pytz.utc)
    end = datetime(2015, 12, 31, 0, 0, 0, 0, pytz.utc)
    data = zp.utils.factory.load_from_yahoo(stocks = kurzde, indexes={}, start=start, end=end, adjusted=True)
    output = open('data.pkl', 'wb')
    # Pickle dictionary using protocol 0.
    pickle.dump(data, output)
data.head()



# In[12]:

# Adds the old ticker without the .DE appendix
data.columns = kurz
# Remove Christmas as a non-trading day
#data = data.drop(pd.Timestamp('2009-12-24 00:00:00'))
# BMW had a non trading day, replacing with last close price
# data['BMW'][pd.Timestamp("2009-03-09")] = data['BMW'][pd.Timestamp("2009-02-09")]



# In[13]:

data.describe()


# In[19]:

# Normalize the whole DataFrame by dividing by first observation
# Remove 2009-12-24 and 2009-12-31, as nontrading on those days.
def norming(x):
    #if isinstance(x, basestring):
    #    return x
    return x / x[0]


datanorm = data.apply(norming)
print 'datanorm!!!'
print datanorm.head()


# In[20]:

# Saving both DataFrames as .csv
data.to_csv("dax.csv")
datanorm.to_csv("dax_normalized.csv")


# # Pairs formation

# #### The second part involves finding potential trading pairs. For this, we create all possible pair combinations and compute the sum of squared distances (SSD) in normalized prices as a selection criterion. We then rank the pairs according to minimal SSD and choose our pairs!

# In[22]:

daxnorm = pd.read_csv("dax_normalized.csv", index_col=0, parse_dates=True)


# In[23]:

def combomaker(x):
    combos = itertools.combinations(x, 2)
    usable_pairs = []
    for i in combos:
        usable_pairs.append(i)
    return usable_pairs
    # Takes a list of ticker symbols as an input and returns a list of
    # all possible combination without repetition



# In[24]:

def ssd(X,Y):
#This function returns the sum of squared differences between two lists, in addition the
#standard deviation of the spread between the two lists are calculated and reported.
    spread = [] #Initialize variables
    std = 0
    cumdiff = 0
    for i in range(len(X)): #Calculate and store the sum of squares
        cumdiff += (X[i]-Y[i])**2
        spread.append(X[i]-Y[i])
    std = np.std(spread)  #Calculate the standard deviation
    return cumdiff,std


# In[28]:

def pairsmatch(x, daxnorm):
    allpairs = combomaker(x)
    squared = []
    std = []
    for i in allpairs:
        squared.append(ssd(daxnorm[i[0]],daxnorm[i[1]])[0])
        std.append(ssd(daxnorm[i[0]],daxnorm[i[1]])[1])
    distancetable = pd.DataFrame({'Pair' : allpairs, 'SSD' : squared, 'Standard Deviation' : std})
    distancetable.sort(columns=['SSD'], axis=0, ascending=True, inplace=True)
    return distancetable

daxpairs = pairsmatch(kurz,daxnorm)


# In[40]:

# Save the Top Five Pairs in a new variable
topfive = daxpairs[:3]
print 'TOPFIVE PAIRS:'
print topfive


# In[37]:

# Create a dictionary, that makes it easier to connect Ticker and Company name
dax_dict = dict(zip(dax.ticker, dax.company))
dax_dict


# In[41]:

# Get a list of the tickers of the 
topfive['Pair']
fivedax = []
for i in topfive['Pair'].to_dict().values():
    fivedax.append(i[0])
    fivedax.append(i[1])
    
uniquefivedax = list(set(fivedax))
uniquefivedax


# ## Getting data for the backtest

# In[44]:

shortde = [] # Adds the .DE appendix to the list, needed for Yahoo Finance quotes
for i in uniquefivedax:
    d = i.strip() #+ ".DE"
    shortde.append(d)

#start = datetime(2016, 1, 1, 0, 0, 0, 0, pytz.utc)
#end = datetime(2016, 6, 30, 0, 0, 0, 0, pytz.utc)
#backtest = zp.utils.factory.load_from_yahoo(stocks = shortde, indexes={}, start=start, end=end, adjusted=True)

try:
    pkl_file = open('backtest.pkl', 'rb')
    backtest = pickle.load(pkl_file)
except:    
    start = datetime(2016, 1, 1, 0, 0, 0, 0, pytz.utc)
    end = datetime(2016, 12, 31, 0, 0, 0, 0, pytz.utc)
    backtest = zp.utils.factory.load_from_yahoo(stocks = shortde, indexes={}, start=start, end=end, adjusted=True)
    output = open('backtest.pkl', 'wb')
    # Pickle dictionary using protocol 0.
    pickle.dump(backtest, output)
data.head()

#backtestStartDate = datetime(2016, 1, 1)
#backtestEndDate = datetime(2016, 6, 30)
#shortde = sorted(shortde)
#print 'shortde = ',shortde
#backtest = grabData(tickers=shortde, startDate=backtestStartDate, endDate=backtestEndDate)

backtest.head()


# In[45]:

backtest.describe()


# In[47]:

# Remove the .DE appendix in the columnnames
#colnamesfive = []
#for i in backtest.columns:
#    colnamesfive.append(i[:-3])
#colnamesfive
#backtest.columns = colnamesfive
#backtest.head()


# In[48]:

# Saving as a csv
backtest.to_csv("dax_backtest.csv")


# In[49]:

backtest = pd.read_csv("dax_backtest.csv", index_col=0, parse_dates=True)#, names=colnamesfive)
backtest.head()


# In[50]:

backtestnorm = backtest.apply(norming)
print 'BACKTEST!!!!!'
print backtestnorm.head()

# In[51]:

# Create a dictionary for each pair with its corresponding standard deviation
fivepair = []
fivesd = []

for i in topfive['Pair']:
    fivepair.append(i[0]+i[1])

for i in topfive['Standard Deviation']:
    fivesd.append(i)

fivedic = dict(zip(fivepair, fivesd))
fivedic


# # The Backtesting Function

# In[56]:

def tradedax(daxtuple):
    
    X = daxtuple[0]
    Y = daxtuple[1]
    portfolio = 1000
    half = portfolio*0.5
    f1 = backtestnorm[X]
    f2 = backtestnorm[Y]
    
    s1 = backtest[X]
    s2 = backtest[Y]

    pairstring = str(X)+str(Y)
    hsd = fivedic[pairstring]
   
    openpos = False
    trades = [] # Contains logs of the the entire pair trades occured in the period
    tradeno = 0
    forcedclose = False
    tradingday_enter = []
    tradingday_exit = []
    spread = []    # Spread of normalized prices on i-th trading day
    pricediff = [] # Absolute price difference of raw stock prices
    profits = []
    period = []
    possize = []
    overval = ""
    treshold = 2*hsd #2*hsd # Uses the standard deviation from the dax_dict Dictionary here
    for i in range(len(f1)): #Calculate and store the sum of squares
        #ordersize1 = (half - (half%s1[i]))/s1[i]
        
        
        date = f1.index[i]
        spread.append(f1[i]-f2[i])
        pricediff.append(s1[i]-s2[i])
        
        
        
        if openpos == False:
            
            if abs(spread[i]) > treshold:
                
                if spread[i] > 0:
                    overval = "A"
                else:
                    overval = "B"
                order1 = (half - (half%s1[i]))/s1[i]
                remaining = portfolio - order1*s1[i]
                order2 = (remaining - (remaining%s2[i]))/s2[i]
                if overval == "A":   # A is overvalued, thus we short it and buy B long
                    
                    shortpos = s1[i]*order1
                    remaining = portfolio - shortpos
                    tradingday_enter.append(date)
                    dayenter = i
                    longpos = s2[i]*order2
                    posvolume = longpos + shortpos
                    possize.append(posvolume)
                    tradelog = "Enter:%i %s short @ %s, %i %s long @ %s on %s" % (order1, X, s1[i], order2, Y, s2[i], date)
                    trades.append(tradelog)
                    

                    openpos = True
                        
                if overval == "B": # Same for above, just other way around
                    
                    tradingday_enter.append(date)
                    shortpos = s2[i]*order2
                    longpos = s1[i]*order1
                    posvolume = longpos + shortpos
                    possize.append(posvolume)
                    tradelog = "Enter:%i %s long @ %s, %i %s short @ %s on %s, Volume: %i" % (order1, X, s1[i], order2, Y, s2[i], date, posvolume)
                    trades.append(tradelog)
                    openpos = True

        if openpos == True:
            
            prevspread = spread[i-1]
            
            if abs(spread[i]) < treshold*0.5:
                
                if overval == "A":
                    
                    shortprofit = shortpos - s1[i]*order1
                    longprofit = s2[i]*order2 - longpos
                    totalprofit = shortprofit + longprofit
                    tradelog = "Exit: %s short @ %s, %s long @ %s on %s with total profit of %s." % (X, s1[i], Y, s2[i], date, totalprofit)
                    trades.append(tradelog)
                    portfolio += totalprofit
                    profits.append(totalprofit)
                    tradingday_exit.append(date)
                    tradeno += 1
                    openpos = False
                    

                if overval == "B":
                                
                    shortprofit = shortpos - s2[i]*order2
                    longprofit = s1[i]*order1 - longpos
                    totalprofit = shortprofit + longprofit
                    portfolio += totalprofit
                    tradelog = "Exit: %s long @ %s, %s short @ %s on %s with total profit of %s." % (X, s1[i], Y, s2[i], date, totalprofit)
                    trades.append(tradelog)
                    profits.append(totalprofit)
                    tradingday_exit.append(date)
                    tradeno += 1
                    openpos = False
                
    if openpos == True:
        if overval == "A":
            shortprofit = shortpos - s1[i]*order1
            longprofit = s2[i]*order2 - longpos
            totalprofit = shortprofit + longprofit
            portfolio += totalprofit
                    
            tradelog = "Exit: No convergence to the end of trading period, Profit: %s" % (totalprofit)
            trades.append(tradelog)
            profits.append(totalprofit)
            tradingday_exit.append(date)
            forcedclose = True
            openpos = False

        if overval == "B":
                                
            shortprofit = shortpos - s2[i]*order2
            longprofit = s1[i]*order1 - longpos
            totalprofit = shortprofit + longprofit
            portfolio += totalprofit
            tradelog = "Exit: No convergence to the end of trading period, Profit: %s" % (totalprofit)
            trades.append(tradelog)
            profits.append(totalprofit)
            tradingday_exit.append(date)
            forcedclose = True
            openpos = False
                
    totalprofits = sum(profits)            
    lastlog = "Total profits of this pair in this timewindow: %s, Portfolio value = %i " % (totalprofits,portfolio) 
    trades.append(lastlog)
    totalinvested = sum(possize)
    totalinvestedlog = "Total invested capital: %s" % (totalinvested) 
    trades.append(totalinvestedlog)
    return trades, tradeno, totalinvested, totalprofits


# In[53]:

#Makes tuples from the pairs
fivedaxpairs = zip(fivedax[::2], fivedax[1::2])
fivedaxpairs


# ## Trading log of the first pair

# In[59]:

print fivedaxpairs[0]
tradedax(fivedaxpairs[0])[0]


# ## Summary and returns

# In[65]:

def portfolio():
    print '='*80
    profits = []
    roundtrips = []
    invested = []
    forced = ["No","No","Yes","Yes","Yes"]
              
    for pair in fivedaxpairs:
        profits.append(tradedax(pair)[3])
        roundtrips.append(tradedax(pair)[1])
        invested.append(tradedax(pair)[2])
    
    relreturn = []
    for i in profits:
        ret = i/1000
        relreturn.append(ret)
    print 'fivedaxpairs'
    print fivedaxpairs
    print 'Absolute profits'
    print profits
    print 'Completed roundtrips'
    print roundtrips
    print 'Total invested'
    print invested
    print 'Relative return'
    print relreturn
    print 'Forced close'
    print forced
    summary = pd.DataFrame({'Pair' : fivedaxpairs, 'Absolute profits ' : profits, 'Completed roundtrips' : roundtrips, 
                            'Total invested': invested, 'Relative return': relreturn, 'Forced close' : forced[:len(profits)]})
    avreturn = np.mean(relreturn)
    return  summary, avreturn
   
table = portfolio()[0]    
print table


# In[71]:

# Average return across the five pairs
avgreturn = portfolio()[1]
annualized = ((1 + avgreturn) ** (12/6)) - 1
print 'ANNUALIZED RETURNS ACCROSS ALL SELECTED PAIRS = %.2f PERCENT' % (100.0*annualized)


# ### 1.04% annualized returns for the five pairs presented!
