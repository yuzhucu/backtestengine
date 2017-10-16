# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         turtle_strategy.py
time:         2017/9/13 上午11:04
description: 

'''

__author__ = 'Jimmy'
from trade.tradeStrategy import *
from utils.ta import *
import threading

class Turtle(TradeStrategy):


    def initialize(self):
        self.context.universe = ['rb1801']
        self.context.run_info.run_id = 'Jimmy_000001'
        self.context.run_info.name = '海龟策略'
        self.context.run_info.frequency = 'HM'

        self.context.user_id = '100867'
        self.context.password = '1'
        self.context.broker_id = '9999'


        self._lock = threading.Lock()

        self.atr = ATR(1000000, cycle=10,coe=0.15)
        self.bl = BreakLimit(cycle=10)
        self.sl = StopLimit(cycle=3)

        self.open_direction = ''
        self.unit_count = 0
        self.unit = 0
        self.last_price = 0
        self.slippage = 2


    # def order_change(self,order):
    #     self._lock.acquire()
    #
    #     print('报单变化 %s' % order)
    #     if order['OrderStatus'] == 'AllTraded':
    #         if order['CombOffsetFlag'] == '0':# 开
    #             self.unit_count = self.unit_count + int(order['VolumeTotalOriginal']/self.unit)
    #         elif order['CombOffsetFlag'] == '3': # 平今
    #             self.unit_count = self.unit_count - int(order['VolumeTotalOriginal']/self.unit)
    #     elif order['OrderStatus'] == 'Canceled':
    #         pass
    #     print('当前unit: %d %d ' % (self.unit, self.unit_count))
    #     self._lock.release()



    def handle_data(self, data):
        # self._lock.acquire()

        open_signal = self.bl.compute(data)
        atr = self.atr.compute(data)
        sl = self.sl.compute(data)
        print('收到bar数据：bar: %s ; atr: %s ; signal:%s-%s ' % (data, atr, self.open_direction, self.last_price))

        # 下单前先撤销所有未成交的单
        for k, v in self.context.orders.items():
            self.cancel_order(v)


        # 止盈止损
        if self.unit > 0 and self.unit_count > 0:
            high_bound = self.last_price + 2 * atr.n
            low_bound = self.last_price - 2 * atr.n
            if self.open_direction == BUY:
                if data.close < low_bound or sl == 'BUY_STOP':
                    print('多单止损止盈')
                    self._order(SELL, CLOSE_T, self.unit * self.unit_count, data.close, -self.slippage)
            if self.open_direction == SELL:
                if data.close > high_bound or sl == 'SELL_STOP':
                    print('空单止损止盈')
                    self._order(BUY, CLOSE_T, self.unit * self.unit_count, data.close, +self.slippage)


        # 开仓
        # 有开仓信号 且 当前无持仓 且unit 至少为1手
        if open_signal is not None and self.unit_count == 0 and atr.unit > 0:
            # 开仓 一个unit手 市价单
            self.open_direction = open_signal.direction
            self.unit = atr.unit

            if self.open_direction == BUY:
                self._order(self.open_direction, OPEN, self.unit, open_signal.price, self.slippage)
            else:
                self._order(self.open_direction, OPEN, self.unit, open_signal.price, -self.slippage)

        # 加仓减仓
        # 0 < 当前持仓计数器 < 4 ，开仓unit至少为1手
        if self.unit_count < 4 and self.unit_count > 0 and self.unit > 0:
            high_bound = self.last_price + 0.5 * atr.n
            low_bound = self.last_price - 0.5 * atr.n
            # 如果第一个unit开仓是多单
            if self.open_direction == BUY:
                if data.close > high_bound:
                    print('多开一个unit')
                    # 当前bar.close > 开仓价+1/2 * N，则多开一个unit
                    self._order(BUY, OPEN, self.unit, high_bound, self.slippage)
                elif data.close < low_bound:
                    print('多平一个unit')
                    # 当前bar.close < 开仓价-1/2 * N，则多平一个unit
                    self._order(SELL, CLOSE_T, self.unit, low_bound,-self.slippage)
            else:
                # 当前bar.close > 开仓价+1/2 * N，则卖平一个unit
                if data.close > high_bound:
                    print('卖平一个unit')
                    self._order(BUY, CLOSE_T, self.unit, high_bound,self.slippage)
                # 当前bar.close < 开仓价-1/2 * N，则卖开一个unit
                elif data.close < low_bound:
                    print('卖开一个unit')
                    self._order(SELL, OPEN, self.unit, low_bound, -self.slippage)

        self._lock.release()


    def _order(self, direction, offset, unit, last_price, slippage):
        self.order(self.context.universe[0], direction, offset, unit,limit_price= int(last_price + slippage))
        self.last_price = last_price


if __name__ == '__main__':
    t = Turtle()
    t.run()