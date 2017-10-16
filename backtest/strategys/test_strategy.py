# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         test_strategy.py
time:         2017/9/7 上午11:04
description: 

'''

__author__ = 'Jimmy'

from backtest.strategy import *
import datetime

class test_strategy(Strategy):

    def initialize(self):
        self.context.universe = ['rb1801']
        self.context.run_info.start_date = "2017-05-19"
        self.context.run_info.end_date = '2017-05-19'
        self.context.datatype = 'csv'
        self.portfolio = Portfolio(10000)

    def handle_data(self, tick):
        if tick['Close'] > 400:
            # print(tick['Open'], tick['Close'])
            self.order('rb1801','buy','open',10,0)



if __name__ == '__main__':
    s = test_strategy()
    s.run()


