# encoding: utf-8


"""
@version: python3.6
@author: ‘sj‘
@contact: songjie1217@hotmail.com
@file: kdj2.py
@time: 11/24/17 5:35 PM
"""

# -*- coding: utf-8 -*-

'''
author:       sj
contact:      songjie1217@hotmail.com
description:
'''

__author__ = 'sj'

import math
from backtest.core.backteststrategy import *
from backtest.optimizer.optimizer import *
from backtest.tools.ta import *

class KdjStrategy(BacktestStrategy):
    def initialize(self):
        self.context.universe = ['SR801']
        self.context.run_info.strategy_name = 'kdj2-5m-sr_801'
        self.context.run_info.feed_frequency = '5m'

        self.context.run_info.start_date = '2017-07-26'
        self.context.run_info.end_date = '2017-09-28'
        self.context.run_info.ip = localip
        self.context.run_info.main_contract = False

        self.context.init_cash = 1000000

        self.context.cash = 1000000  # 初始资金
        self.context.cash_rate = 0.8  # 资金利用率
        # self.context.future_info = ts.get_future_info(self.context.universe[0]) # 获取合约属性
        self.context.slippage = 0  # 开仓价 变化幅度 2 个变动单位

        self.context.direction = 'none'
        self.context.open_vol = 0  # 当前开仓手数
        self.context.open_flag = False  # false表示没有开仓 true表示已经开仓了
        self.context.can_open_flag = True  # true 表示能继续开仓 false 表示已经开足仓了
        self.context.close_count = 0  # 平仓计数器
        self.context.open_price = 0
        self.context.max_dev = 0

        self.context.k1 = 53
        self.context.d1 = 47
        self.context.cyclenum = 13

        self.context.kdj = KDJ(k1=self.context.k1, d1=self.context.d1, cyclenum=self.context.cyclenum)
        self.context.kdjls = []

    def order_change(self, order):
        print('update unit %s:' % datetime.datetime.now(), 5)
        # print(self.context.open_vol)
        # print(order['vol'])
        # self.context.last_price = data['limit_price']
        if order['offset'] == OPEN and order['direction'] == BUY:
            self.context.open_vol += order['vol']
            self.context.direction = 'long'
        elif order['offset'] == CLOSE and order['direction'] == BUY:
            self.context.open_vol -= order['vol']
            self.context.direction = 'none'
        elif order['offset'] == OPEN and order['direction'] == SELL:
            self.context.open_vol += order['vol']
            self.context.direction = 'short'
        elif order['offset'] == CLOSE and order['direction'] == SELL:
            self.context.open_vol -= order['vol']
            self.context.direction = 'none'


        # print(self.context.open_vol)
        # if self.context.open_vol > 0:
        #     self.context.open_flag = True
        # else:
        #     self.context.open_flag = False
        # print(self.context.open_flag)



    def handle_data(self, data):
        kdj = self.context.kdj.compute(data,self.context.k1,self.context.d1)
        if kdj is None:
            # print(self.context.k1)
            kdj1 = KDJOut(self.context.k1,self.context.d1,0,0,0)
            self.context.kdjls.append(kdj1)
            # print(self.context.kdjls[-1].__dict__)
            # print('none')

        if kdj is not None:
            # print(kdj.k1, kdj.d1, kdj.k2, kdj.d2, kdj.j2)
            self.context.kdjls.append(kdj)
            if kdj.k1 > kdj.d1 and kdj.k2 < kdj.d2:
                print('signal1', self.context.direction)
                if self.context.direction == 'short':
                    self.order(self.context.current_contract[0], BUY, CLOSE, self.context.open_vol,
                               limit_price=data.close)
                elif self.context.direction == 'none':
                    open_vol = int((self.context.portfolio.avail_cash * self.context.cash_rate) / (data.close * self.context.instmt_info['broker_margin'] * 0.01 * self.context.instmt_info['contract_size']))
                    print("手数", open_vol, "价格,", data.close)
                    self.order(self.context.current_contract[0], BUY, OPEN, open_vol,
                               limit_price=data.close)

            elif kdj.k1 < kdj.d1 and kdj.k2 > kdj.d2:
                print('signal2', self.context.direction)
                if self.context.direction == 'long':
                    self.order(self.context.current_contract[0], SELL, CLOSE, self.context.open_vol,
                               limit_price=data.close)

                elif self.context.direction == 'none':
                    open_vol = int((self.context.portfolio.avail_cash * self.context.cash_rate) / (data.close * self.context.instmt_info['broker_margin'] * 0.01 * self.context.instmt_info['contract_size']))
                    print("手数", open_vol, "价格,", data.close)
                    self.order(self.context.current_contract[0], SELL, OPEN, open_vol,
                               limit_price=data.close)

            self.context.k1 = kdj.k2
            self.context.d1 = kdj.d2


if __name__ == '__main__':
    t = KdjStrategy()
    t.run()






