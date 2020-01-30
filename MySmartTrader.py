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

ts.set_token('ba1431283cda64abef91c1ee0df98b382bfde0645a4f5175d5145d6d')
pro = ts.pro_api()

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
    global totalStockCodeListed, pro

    for indexNb in range (0, totalStockCodeListed.size):
        stockCode = totalStockCodeListed[indexNb]
        '''
        Due to interface parameter change, so no need to remove .SZ or .SH substring
        if '.SZ' in stockCode:
            strCode = stockCode.replace('.SZ', '')
        elif '.SH' in stockCode:
            strCode = stockCode.replace('.SH', '')
        else:
            print("Not recognized stock code:", stockCode)
        '''

        # dfStockItem = pro.daily(ts_code = strCode, start = Start_date, end = End_date)
        dfStockItem = pro.daily(ts_code = stockCode, start = Start_date, end = '20200120')
        dfStockItem.sort_index()

        # Calculate MA5, BBANDS, RSI, OBV, and MACD indicators
        sma_5  = talib.MA(np.array(dfStockItem['close']), timeperiod = 5,  matype = 1)
        macd, macdSignal, macdHist = talib.MACD(np.array(dfStockItem['close']),
                            fastperiod = 5, slowperiod = 12, signalperiod = 9)  
        rsi = talib.RSI(np.array(dfStockItem['close']), timeperiod = 5)     #RSI的天数一般是6、12、24
        mom = talib.MOM(np.array(dfStockItem['close']), timeperiod = 5)

        # Bollinger Bands: Help to judge the derivation between current price and the price's normal distribution model
        # So if mid is NOT equal to the current price, so there will be high possibility to adjust back.
        up, mid, low = talib.BBANDS(np.array(dfStockItem['close']), timeperiod=5, nbdevup=2, nbdevdn=2, matype=4)

        # Accumulation/Distribution Line: Combines price and volume to show how money may be flowing into or out of a stock.
        # %B Indicator: Shows the relationship between price and standard deviation Bollinger Bands. Similar to MACD vs BBANDS?
        # On Balance Volume (OBV): Combines price and volume in a very simple way to show how money may be flowing into or out of a stock.
        ad  = talib.AD(dfStockItem['high'], dfStockItem['low'], dfStockItem['close'], dfStockItem['vol']).values
        adosc = talib.ADOSC(dfStockItem['high'], dfStockItem['low'], dfStockItem['close'], dfStockItem['vol'], fastperiod=3, slowperiod=10).values
        obv = talib.OBV(dfStockItem['close'], dfStockItem['vol']).values
        if  ((mid[-1] > mid[-2]) and
            (sma_5[-1] > sma_5[-2]) and
            (mid[-1] > sma_5[-2]) and
            (rsi[-1] > rsi[-2]) and
            (obv[-1] > obv[-2]) and
            (macd[-1] > macdSignal[-1])):
            # Add into Buy Candidate
            print("===============================================")
            print(dfStockItem.tail(n = 5))
            print("Candidate IndexNb: ", stockCode, " Record: ", dfStockItem.tail(1))
            print("-----------------------------------------------")


    print("Scanning finish")
    return


# Judge whether today is the last trading day.
today = datetime.datetime.today().strftime('%Y-%m-%d')
startTradingDay = (datetime.datetime.today() - datetime.timedelta(days = 30)).strftime('%Y-%m-%d')
print("Start date: ", startTradingDay, ", End date: ", today)

'''
Comment for work around process
alldays = pro.trade_cal(exchange = '', start_date = startTradingDay, end_date = today)
tradingdays = alldays[alldays['isOpen'] == 1]   # Retrieve all trading days since openning PRC stock market (SZ & SH)
print(tradingdays.tail(10))
tradingdays_list = tradingdays['calendarDate'].tolist()

if today in tradingdays['calendarDate'].values:
    today_index  = tradingdays_list.index(today)
    print("today index nb: ", today_index, ", length of tradingdays: ", len(tradingdays_list))
    last_day = tradingdays_list[int(today_index)-30]    # Back 30 days as indicators calculation start day
    print("Case 1: Today: ", today, ", Calculation start date: ", last_day)
else:
    # Since today is not the trading day so just use the last date in trandingdays
    today = tradingdays_list[-1]
    last_day = tradingdays_list[len(tradingdays_list) - 30]    # Specify 20 days back as the start calculation point
    print("Case 2: Today: ", today, ", Calculation start date: ", last_day)

'''

# today = datetime.date.today()
# today = datetime.today() - timedelta(days = 2)
# strDate = today.strftime("%Y-%m-%d")
# print("Today: ", strDate)
Start_date = "20191101"
# End_date = strDate
End_date = today

totalStockListed = pro.daily(trade_date='20191220')
totalStockCodeListed = totalStockListed['ts_code']

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

