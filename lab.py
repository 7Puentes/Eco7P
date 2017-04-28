'''
Created on Apr 26, 2017

@author: joign
'''

from datetime import datetime
from pandas_datareader import data, wb
import pandas_datareader.data as web
import pandas as pd


kurzde = ['ARCO','BFR','CRESY']

startDate = datetime(2015, 1, 1)
endDate = datetime(2015, 12, 31)

ticker = kurzde[0]
data1 = web.DataReader(ticker.strip('\n'), "yahoo", startDate, endDate )
data1 = data1['Close']
data1.name = ticker
print data1.head()

result = data1
for ticker in kurzde[1:]:
    data2 = web.DataReader(ticker.strip('\n'), "yahoo", startDate, endDate)
    data2 = data2['Close']
    data2.name = ticker
    print data2.head()
    result = pd.concat([result, data2], axis=1, join_axes=[result.index])
    print result.head()    
    

print '='*80
print result.head()


# data1 = web.DataReader('ARCO'.strip('\n'), "yahoo", datetime(2015, 1, 1), datetime(2015, 12, 31))
# data1 = data1['Close']
# data1.name = 'ARCO'
# print data1.head()
# 
# data2 = web.DataReader('BFR'.strip('\n'), "yahoo", datetime(2015, 1, 1), datetime(2015, 12, 31))
# data2 = data2['Close']
# data2.name = 'BFR'
# print data2.head()
# 
# result = pd.concat([data1, data2], axis=1, join_axes=[data1.index])
# print result.head()