# encoding: utf-8


"""
@version: python3.6
@author: ‘sj‘
@contact: songjie1217@hotmail.com
@file: tools.py
@time: 10/19/17 9:23 PM
"""
from backtest.data.datatype import *


def create_bar_obj(bar_data):
    bar_object = Bar()
    bar_object.symbol = bar_data['InstrumentID']
    bar_object.open = bar_data['OpenPrice']
    bar_object.close = bar_data['ClosePrice']
    bar_object.high = bar_data['HighPrice']
    bar_object.low = bar_data['LowPrice']
    bar_object.trading_day = bar_data['TradingDay']
    bar_object.begin_time = bar_data['beginTime']
    bar_object.end_time = bar_data['endTime']
    bar_object.vol = bar_data['Volume']
    bar_object.addposition = bar_data['AddedPosition']
    bar_object.freq = bar_data['type']
    return bar_object
