# encoding: utf-8


"""
@version: python3.6
@author: ‘sj‘
@contact: songjie1217@hotmail.com
@file: datatype.py
@time: 9/28/17 6:33 PM
"""

class Bar(object):
    def __init__(self):
        self.symbol = ''
        self.open = 0
        self.close = 0
        self.high = 0
        self.low = 0
        self.trading_day = 0
        self.begin_time = ''
        self.end_time = ''
        self.vol = 0
        self.tick_counter = 0
        self.freq = ''

    def __str__(self):
        return 'symbol:%s, open: %.2f, close: %.2f, high: %.2f, low: %.2f, vol:%d, tick_counter:%d ' \
               'trading_day:%s, begin_time:%s, end_time:%s' \
               %(self.symbol,self.open, self.close, self.high, self.low, self.vol,
                 self.tick_counter, self.trading_day, self.begin_time, self.end_time)


class InstmtInfo(object):
    def __init__(self):
        self.symbol = ''
        self.exch_code = ''
        self.tick_size = 0
        self.contract_size = 0
        self.exch_margin = 0
        self.broker_margin = 0
        self.comm_open = 0
        self.comm_close_y = 0
        self.comm_close_t = 0
        self.comm_type = ''



