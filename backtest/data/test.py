from backtest.data.getdata import *
import pymongo
import pandas as pd
import numpy as np
from backtest.data.dataconfig import *
from backtest.data.iterator import *
import datetime
from backtest.tools.tools import *
# from backtest.core.context import *

# data = GetDataMongo('TA801',20170512,ip=localip).get_tick_data()
#
# print(list(data))

# data = pymongo.MongoClient(remoteip, port).futures['rb_price'].find_one()
# # print(type(data['TradingDay']))
# print(data)
#
#
# print(pd.DataFrame(list(data)))
#
#
#
#
# start = '2017-05-11'
# end = '2017-06-11'
#
# # print(datestrtoint(start))
# #
# # datels = [start]
# date = pymongo.MongoClient(localip,port).futures['trade_date'].find({'cur_trade_date':{"$in":[20170924,20170925,20170926]}})
# # # for row in date:
# # #     datels.append(row['cur_trade_date'])
# #
# #
# print(list(date))

# class Strategy(object):
#     def __init__(self):
#
#
#         # context里保存所有需要的信息
#         self.context = Context()
#
#     def initialize(self):
#         print('you must initilize account')
#         raise NotImplementedError
#
#
# class a(Strategy):
#     def initialize(self):
#         self.context.init_cash = 9
#         print(self.context.sup_data)
#
#
# a().initialize()

#
# a = InstmtInfoMongo(symbol='j1801')
# print(a.get_instmt_info())

# datels = GetTradeDates(ip=remoteip).get_date_list(start=20170510,end=20170611)
# print(datels)

# time1 = datetime.datetime.now()
# data = GetDataMongo(date=20170727, symbol='j1801').get_bar_data(freq='1m')
# for row in data:
#     print(row)
#
# print(data.next())
# print(data.next())
# time2 = datetime.datetime.now()
# #
# print(time2-time1)



# data = TradeDataMongo(symbol='rb1801',date=20170511,column=columns,ip=remoteip).get_settlement_price()
# print(data)


# a = np.array([1,2,3])
# np.insert(a,1,1)
# print(a)

# a = [1,2,3]
#
# b = np.array(a)
#
# print(b)

# a = TradeDataMongo(symbol='SR801', date=20170510).get_bar_data(freq='30s')
b = TradeDataMongo(symbol='cs1801', date=20170213, column=['TradingDay','UpdateTime','LastPrice','levelNo']).get_bar_data(freq='30s')
# #
# df = pd.DataFrame(list(a))
# #
df1 = pd.DataFrame(list(b))
# print(df)
print(df1)
# #
# df1.to_csv('SR801-20170509-bar.csv')


# a = np.array([1000])
# np.insert(a,1,1)
#
# print(a)