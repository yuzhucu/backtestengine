# -*- coding: utf-8 -*-

'''
author:       sjsj
contact:      songjie1217@hotmail.com
file:         getdata.py
time:         2017/8/29 17:07
description:
'''


__author__ = 'sjsj'

import pymongo
import pandas as pd
from backtest.data.dataconfig import *
from backtest.data.iterator import *
from backtest.tools.tools import *


class GetDataMongo(object):

    def __init__(self, symbol, date, column=miniclms, ip=localip):
        self.symbol = symbol
        self.date = date
        self.column = column
        self.ip = ip
        self.code = instidtoprodid(symbol).lower()
        self.client = pymongo.MongoClient(self.ip, port)
        self.db = self.code + '_price'

    def get_tick_data(self):
        # client = pymongo.MongoClient(self.ip, port)
        collection = self.client.futures[self.db]  # different collections
        data = collection.find({"InstrumentID": self.symbol, "TradingDay": self.date}, self.column).sort('levelNo',1)
        return data


class GetSupData(object):
    def __init__(self,symbol, ip=localip):
        self.symbol = symbol
        self.code = instidtoprodid(symbol).lower()
        self.ip = ip
        self.client = pymongo.MongoClient(self.ip, port)
        self.dbsup = 'future_info'

    def get_sup_data(self):   ###取手续费，乘数等相关信息
        collection = self.client.futures[self.dbsup]
        feedata = collection.find({'instrument_code': self.code})
        supdata = list(feedata)[0]
        if supdata['opening_fee_by_num'] == 0.0:
            supdata['commision_type'] = 'byvalue'
        else:
            supdata['commision_type'] = 'byvol'

        return supdata

    def get_tick_size(self):
        return self.get_sup_data()['tick_size']

    def get_contract_size(self):
        return self.get_sup_data()['contract_size']

    def get_margin_ratio(self, type = 'broker'):
        if type == 'broker':
            return self.get_sup_data()['broker_margin']/100
        elif type == 'exch':
            return self.get_sup_data()['exch_margin']/100
        else:
            print('please enter the correct margin type')
            raise ValueError

    def get_commission_type(self):
        if self.get_sup_data()['opening_fee_by_num'] == 0.0:
            return 'value'
        else:
            return 'vol'

    def get_commission(self, offset):
        if offset == 'open':
            return max(self.get_sup_data()['opening_fee_by_num'], self.get_sup_data()['opening_fee_by_value'])
        elif offset == 'closeT':
            return max(self.get_sup_data()['closing_today_fee_by_num'], self.get_sup_data()['closing_today_fee_by_value'])
        elif offset == 'closeY':
            return max(self.get_sup_data()['closing_fee_by_num'], self.get_sup_data()['closing_fee_by_value'])


class GetDataCSV(object):
    def __init__(self,filename,location=''):
        self.filename = filename
        self.location = location

    def get_tick(self):
        df = pd.read_csv(self.filename)
        return PandasDFTickEventIterator(df)


class GetTradeDates(object):
    def __init__(self,ip = localip):
        self.ip = ip
        self.db = pymongo.MongoClient(self.ip, port).futures['trade_date']

    def is_trading_day(self,tradeday):
        if list(self.db.find({'cur_trade_date':tradeday})):
            return True
        else:
            return False

    def get_next_trading_day(self,curday):
        while self.is_trading_day(curday):
            return self.db.find_one({'cur_trade_date':curday})['next_trade_date']
        curday += 1

    def __get_date_range(self, start, end):
        datestart = datetime.datetime.strptime(str(start), '%Y%m%d')
        dateend = datetime.datetime.strptime(str(end), '%Y%m%d')
        datelist = [start]
        while datestart < dateend:
            datestart += datetime.timedelta(days=1)
            datelist.append(int(datestart.strftime('%Y%m%d')))
        return datelist

    def get_date_list(self,start,end):
        datelist = []
        daterange = self.__get_date_range(start,end)
        # print(daterange)
        data = self.db.find({'cur_trade_date':{"$in":daterange}})
        for row in data:
            # print(row)
            datelist.append(row['cur_trade_date'])
        return sorted(datelist,reverse=False)


s = ['rb1801','ag1801']

def get_tick(date, symbol):
    tick = GetDataMongo(symbol=symbol, date=date).get_tick_data()  # 数据库取某天的tick
    return tick

def get_ticks_dict(date,symbols):
    ticks = {}
    for symbol in symbols:
        ticks[symbol] = get_tick(date,symbol)
    return ticks

# # for row in get_tick(20170511,'rb1801'):
# #     print(row)
# #     break
# #
#
# a = get_ticks_dict(20170511, s)
# time1 = datetime.datetime.now()
# # tick = {}
# # for symbol in s:
# #     tick[symbol] = a[symbol].next()
# # for symbol in s:
# #     tick[symbol] = a[symbol].next()
# # for symbol in s:
# #     tick[symbol] = a[symbol].next()
# # for symbol in s:
# #     tick[symbol] = a[symbol].next()
# # for symbol in s:
# #     tick[symbol] = a[symbol].next()
# # for symbol in s:
# #     tick[symbol] = a[symbol].next()
# # for symbol in s:
# #     tick[symbol] = a[symbol].next()
# # for symbol in s:
# #     tick[symbol] = a[symbol].next()
# # for symbol in s:
# #     tick[symbol] = a[symbol].next()
# # for symbol in s:
# #     tick[symbol] = a[symbol].next()
#
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
# a['ag1801'].next()
#
# time2 = datetime.datetime.now()
# # print(tick)
#
# print(time2-time1)
#
# # print(a)