# -*- coding: utf-8 -*-

'''
author:       sjsj
contact:      songjie1217@hotmail.com
file:         position.py
time:         2017/9/11 11:18
description:

'''

__author__ = 'sjsj'


class BasePosition(object):
    def __init__(self, symbol, direction, init_vol, init_price, marginratio):
        """
        记录每个资产持仓情况，并随tick更新净值
        """
        self.symbol = symbol   # 合约id
        self.direction = direction   # buy or sell
        self.vol = init_vol      # volume held
        self.avg_cost = init_price * self.vol  # initial value
        self.avg_cost_per_unit = self.avg_cost/self.vol if self.vol != 0 else 0  # average cost per unit
        self.price = init_price  # latest price
        self.value = self.price * self.vol  # latest value
        self.marginratio = marginratio   # latest margin ratio
        self.marginreq = self.value * self.marginratio   # latest margin requirement
        self.upnl = (self.value - self.avg_cost) if self.direction == 'buy' else (self.avg_cost - self.value)  # unrealized gain/loss
        self.type = 'empty' if self.vol == 0 else 'not empty'  # open or closed

    def update_value_tick(self, tick):
        self.price = tick.close

    def close_position(self, vol):
        self.vol -= vol

    def add_position(self,vol,price):
        self.vol += vol
        self.avg_cost += vol*price


class Position(object):
    def __init__(self, symbol, marginratio):
        self.symbol = symbol
        self.marginratio = marginratio
        self.BuyT = BasePosition(symbol=symbol, direction='buy', init_price=0, init_vol=0, marginratio=marginratio)
        self.BuyY = BasePosition(symbol=symbol, direction='buy', init_price=0, init_vol=0, marginratio=marginratio)
        self.SellT = BasePosition(symbol=symbol, direction='sell', init_price=0, init_vol=0, marginratio=marginratio)
        self.SellY = BasePosition(symbol=symbol, direction='sell', init_price=0, init_vol=0, marginratio=marginratio)
        self.vol = self.BuyT.vol + self.BuyY.vol + self.SellT.vol + self.SellY.vol
        self.voldetail = {'buy': self.BuyT.vol + self.BuyY.vol, 'sell': self.SellT.vol + self.SellY.vol}
        self.price = self.BuyT.price
        self.value = self.BuyT.value + self.BuyY.value + self.SellT.value + self.SellY.value
        self.valuedetail = {'buy': self.BuyT.value + self.BuyY.value, 'sell': self.SellT.value + self.SellY.value}
        self.marginreq = self.BuyT.marginreq + self.BuyY.marginreq + self.SellT.marginreq + self.SellY.marginreq
        self.marginreqdetail = {'buy': self.BuyT.marginreq + self.BuyY.marginreq, 'sell': self.SellT.marginreq + self.SellY.marginreq}
        self.upnl = self.BuyT.upnl + self.BuyY.upnl + self.SellT.upnl + self.SellY.upnl
        self.upnldetail = {'buy': self.BuyT.upnl + self.BuyY.upnl, 'sell': self.SellT.upnl + self.SellY.upnl}
        self.pnl = 0
        self.type = 'closed' if self.vol == 0 else 'open'

    def update_value_tick(self, tick):
        self.BuyT.update_value_tick(tick)
        self.BuyY.update_value_tick(tick)
        self.SellT.update_value_tick(tick)
        self.SellY.update_value_tick(tick)

    def _combine_position(self,position1, position2):      # combine position 2 to position 1
        position1.vol += position2.vol
        position1.avg_cost += position2.avg_cost
        position1.upnl += position2.upnl

    def update_position_dayend(self):
        self._combine_position(self.BuyY, self.BuyT)
        self._combine_position(self.SellY, self.SellT)




# a = BasePosition('aaa','buy',100,100,0.1)
# b = BasePosition('aaa','buy',100,50,0.1)
#
# c = Position('aaa')
# c.BuyT = BasePosition('aaa','buy',100,100,0.1)
#
# # print(c.BuyT.direction)
#
#
# p = {}
# p['aaa'] = Position('aaa')
# p['aaa'].BuyT = BasePosition('aaa','buy',100,100,0.1)
#
# print(p['aaa'].BuyT.value)











































































































































