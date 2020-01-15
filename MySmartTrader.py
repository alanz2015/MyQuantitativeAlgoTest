# -*- coding: utf-8 -*- 
# Multiple thread for Stock Trader, one is for identify which stocks are fall into candidates;
# the second one is for performing sell action.
 
import threading 
import tushare as ts 
import numpy as np 
import matplotlib.pyplot as plt 
import mpl_finance as mpf 
import talib
import pandas
import matplotlib.dates as mdates
from matplotlib.pylab import date2num
import datetime
from matplotlib.backends.backend_pdf import PdfPages

def sellAction(num): 
	""" 
	function to print cube of given num 
	"""
	print("Cube: {}".format(num * num * num)) 

""" 
This function will execute the following logic:
1. Retrieve all listed stocks code;
2. Retrieve historical information of the enumerated stock item one by one;
3. Calculate the MA5, BBANDS, RSI, OBV, and MACD indicators of the retrieve stock item;
4. Put the indicators of specific stock item into condition expression to see this stock
   item is the buy candidate, if yes, add it into the candidate queue that will be process by
   sell thread per the registed date.
"""
def identifyCandidate():
    global stockCodeList

    for indexNb in range (0, stockCodeList.size):
        stockCode = stockCodeList[indexNb]
        df4stockitem = ts.get_k_data(stockCode, start = Start_date, end = End_date, ktype = 'D')

    print("Start here")

today = datetime.date.today()
strDate = today.strftime("%YYYY-%MM-%DD")
print("Today: ", strDate)
allData = ts.get_day_all(strDate)
stockCodeList = allData['code']
# creating thread 
t1 = threading.Thread(target=sellAction, args=(10,)) 
t2 = threading.Thread(target=identifyCandidate, args=()) 

# starting thread 1 
t1.start() 
# starting thread 2 
t2.start() 

# wait until thread 1 is completely executed 
t1.join() 
# wait until thread 2 is completely executed 
t2.join() 

# both threads completely executed 
print("Done!") 

