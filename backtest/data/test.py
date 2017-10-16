from backtest.data.getdata import *
import pymongo
import pandas as pd
import numpy as np
from backtest.data.dataconfig import *
from backtest.data.iterator import *
import datetime
from backtest.tools.tools import *
from backtest.context import *

# data = GetDataMongo('TA801',20170512,ip=localip).get_tick_data()
#
# print(list(data))

data = pymongo.MongoClient(remoteip, port).futures['rb_price'].find_one()
# print(type(data['TradingDay']))
print(data)
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


# a = GetSupData(symbol='rb1801')
# print(a.get_sup_data())