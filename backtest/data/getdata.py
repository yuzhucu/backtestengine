# -*- coding: utf-8 -*-

'''
author:       sjsj
contact:      songjie1217@hotmail.com
file:         getdata.py
time:         2017/8/29 17:07
description:
'''


__author__ = 'sjsj'


from backtest.data.dataconfig import *
from backtest.data.datatype import *
from backtest.data.iterator import *
from backtest.tools.tools import *

import pymongo
import pandas as pd

class TradeDataMongo(object):

    def __init__(self, symbol, date, column=miniclms, ip=remoteip):
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
        tickdata = collection.find({"InstrumentID": self.symbol, "TradingDay": self.date}, self.column).sort('levelNo', 1)
        return tickdata

    def get_bar_data(self, freq = '1m'):
        collection = self.client.futures['history_bar']
        bardata = collection.find({"InstrumentID": self.symbol, "TradingDay": self.date, 'type': freq}).sort('levelNo', 1)
        return bardata

    def __get_pre_settlement_price(self):
        collection = self.client.futures[self.db]  # different collections
        price = collection.find({"InstrumentID": self.symbol, "TradingDay": self.date}, ['PreSettlementPrice'])
        return list(price)[-1]['PreSettlementPrice']

    def get_settlement_price(self):
        next_day = GetTradeDates(ip=self.ip).get_next_trading_day(self.date)
        collection = self.client.futures[self.db]  # different collections
        price = collection.find({"InstrumentID": self.symbol, "TradingDay": next_day}, ['PreSettlementPrice'])
        return list(price)[-1]['PreSettlementPrice']


class InstmtInfoMongo(object):
    def __init__(self, symbol, ip=remoteip):
        self.symbol = symbol
        self.code = instidtoprodid(symbol).lower()
        self.ip = ip
        self.client = pymongo.MongoClient(self.ip, port)
        self.dbsup = 'future_info'

    def get_instmt_info(self):   ###取手续费，乘数等相关信息
        collection = self.client.futures[self.dbsup]
        feedata = collection.find({'instrument_code': self.code})
        supdata = list(feedata)[0]
        if supdata['opening_fee_by_num'] == 0.0:
            supdata['commission_type'] = 'value'
        else:
            supdata['commission_type'] = 'vol'

        return supdata

    def get_tick_size(self):
        return self.get_instmt_info()['tick_size']

    def get_contract_size(self):
        return self.get_instmt_info()['contract_size']

    def get_margin_ratio(self, margin_type='broker'):
        if margin_type == 'broker':
            return self.get_instmt_info()['broker_margin']/100
        elif margin_type == 'exch':
            return self.get_instmt_info()['exch_margin']/100
        else:
            print('please enter the correct margin type')
            raise ValueError

    def get_commission_type(self):
        if self.get_instmt_info()['opening_fee_by_num'] == 0.0:
            return 'value'
        else:
            return 'vol'

    def get_commission(self, offset):
        if offset == 'open':
            return max(self.get_instmt_info()['opening_fee_by_num'], self.get_instmt_info()['opening_fee_by_value'])
        elif offset == 'closeT':
            return max(self.get_instmt_info()['closing_today_fee_by_num'], self.get_instmt_info()['closing_today_fee_by_value'])
        elif offset == 'closeY':
            return max(self.get_instmt_info()['closing_fee_by_num'], self.get_instmt_info()['closing_fee_by_value'])


class GetDataCSV(object):
    def __init__(self, filename, location=''):
        self.filename = filename
        self.location = location

    def get_tick(self):
        # df = pd.read_csv(self.filename)
        # return PandasDFTickEventIterator(df)
        pass

class GetTradeDates(object):
    def __init__(self, ip=remoteip):
        self.ip = ip
        self.db = pymongo.MongoClient(self.ip, port).futures['trade_date']

    def is_trading_day(self, tradeday):
        if list(self.db.find({'cur_trade_date': tradeday})):
            return True
        else:
            return False

    def get_next_trading_day(self, curday):
        while self.is_trading_day(curday):
            return self.db.find_one({'cur_trade_date': curday})['next_trade_date']
        curday += 1

    def __get_date_range(self, start, end):
        datestart = datetime.datetime.strptime(str(start), '%Y%m%d')
        dateend = datetime.datetime.strptime(str(end), '%Y%m%d')
        datelist = [start]
        while datestart < dateend:
            datestart += datetime.timedelta(days=1)
            datelist.append(int(datestart.strftime('%Y%m%d')))
        return datelist

    def get_date_list(self, start, end):
        datelist = []
        daterange = self.__get_date_range(start, end)
        # print(daterange)
        data = self.db.find({'cur_trade_date': {"$in": daterange}})
        for row in data:
            # print(row)
            datelist.append(row['cur_trade_date'])
        return sorted(datelist, reverse=False)


# def get_settlement_price(symbol,date,ip=remoteip):
    # data = pymongo.MongoClient(ip=ip, port=27017).collection.find({"InstrumentID": symbol, "TradingDay": date}, ['SettlementPrice'])
    # return list(data[-1])


# a = TradeDataMongo('j1801',20170724).get_settlement_price()
# print(a)