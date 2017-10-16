# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         strategy_test.py
time:         2017/8/28 上午11:43
description: 

'''

__author__ = 'Jimmy'

from trade.tradeStrategy import *

class test_strategy(TradeStrategy):

    def initialize(self):
        self.context.universe = ['rb1801']
        self.context.run_info.run_id = '000001'
        self.context.run_info.name = '测试'
        self.context.run_info.frequency = '1M'

        # 自定义了一些变量
        self.flag = True
        self.cancel_flag = True
        self.count = 0

    def handle_data(self, data):
        print('[%s] handle tick of %s => %s' % (self.context.run_info.name, self.context.universe[0], data))

        # if self.flag:
        #     self.flag = False
        #     print('==================================')
        #     print('==========策略触发限价交易==========')
        #     self.order(self.context.universe[0], BUY, OPEN, 1)


if __name__ == '__main__':
    t = test_strategy()
    t.run()