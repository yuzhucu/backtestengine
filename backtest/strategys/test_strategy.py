# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         turtle_strategy.py
time:         2017/9/13 上午11:04
description:

'''

__author__ = 'Jimmy'
from utils.ta import *
from datetime import datetime
from backtest.strategy import *

class test(BacktestStrategy):

    def initialize(self):
        self.context.universe = ['j1801']
        self.context.run_info.run_id = 'turtle_1h'
        self.context.run_info.strategy_name = '海龟策略'
        self.context.run_info.feed_frequency = '60m'
        self.context.run_info.start_date = '2017-07-24'
        self.context.run_info.end_date = '2017-07-25'
        self.context.portfolio = PortfolioBar()
        self.context.portfolio.init_cash = 1000000

        self.context.atr = ATR(1000000, cycle=20, dpp=50, coe=0.3)
        self.context.bl = BreakLimit(cycle=20)
        self.context.sl = StopLimit(cycle=10)

        self.context.open_direction = ''
        self.context.unit_count = 0
        self.context.unit = 0
        self.context.last_price = 0
        self.context.slippage = 0

        # self._lock = threading.Lock()


    def handle_data(self, data):
        if data['ClosePrice'] > 1800:
            self.order(instrument_id='j1801',direction='buy',offset='open',vol=1000,limit_price=data['ClosePrice'])

if __name__ == '__main__':
    t = test()
    t.run()