import pandas as pd
import pymongo
from backtest.data.dataconfig import *
from backtest.data.getdata import *
from backtest.data.iterator import *


def ticktobar (tick):   #takes tick cursor object and transfer it to iter bar event
    templs = []
    timeflag = []
    bardict = {
        'TradingDay':[],
        'CloseTime':[],
        'Open':[],
        'Close':[],
        'High':[],
        'Low':[],
        'Volume':[],
        'curVol':[]
    }
    for row in tick:
        templs.append(row['LastPrice'])
        timeflag.append(row['UpdateTime'][4])
        try:
            if int(timeflag[-1]) != int(timeflag[1]):
                bardict['TradingDay'].append(row['TradingDay'])
                bardict['CloseTime'].append(row['UpdateTime'])
                bardict['Open'].append(templs[0])
                bardict['Close'].append(templs[-1])
                bardict['High'].append(max(templs))
                bardict['Low'].append(min(templs))
                bardict['Volume'].append(row['Volume'])
                templs =[]
                timeflag=[]
            else:
                pass
        except:
            pass

        bardict['curVol'] = bardict['Volume'].copy()
        for i in range(1,len(bardict['Volume'])):
            bardict['curVol'][i] = bardict['Volume'][i] - bardict['Volume'][i-1]

    return bardict

if __name__ == '__main__':
    data = GetDataMongo('rb1801', 20170512).get_tick_data()
    df = pd.DataFrame(ticktobar(data))
    print(df)