# -*- coding: utf-8 -*-

'''
author:       sjsj
contact:      songjie1217@hotmail.com
file:         position.py
time:         2017/9/11 11:18
description:

'''

__author__ = 'sjsj'

from backtest.data.getdata import *

class BasePosition(object):
    def __init__(self, symbol, direction, init_vol, init_price, marginratio):
        """
        记录每个资产持仓情况，并随tick更新净值
        """
        self.symbol = symbol  # 合约id
        self.direction = direction  # long or short
        self.vol = init_vol  # volume held
        self.cost = init_price * self.vol  # initial value
        self.avg_cost_per_unit = init_price  # average cost per unit
        self.price = init_price  # latest price
        self.value = self.price * self.vol  # latest value
        self.marginratio = marginratio  # latest margin ratio
        self.marginreq = self.value * self.marginratio  # latest margin requirement
        self.upnl = (self.value - self.cost) if self.direction == 'long' else (self.cost - self.value)  # unrealized gain/loss



    def update_value(self, price):
        self.price = price
        self.value = self.price*self.vol
        self.marginreq = self.value * self.marginratio
        self.upnl = (self.value - self.cost) if self.direction == 'long' else (self.cost - self.value)


    def close_position(self, vol):
        self.vol -= vol
        self.value = self.price*self.vol
        self.marginreq = self.value * self.marginratio
        self.cost = self.avg_cost_per_unit * vol
        self.upnl = (self.value - self.cost) if self.direction == 'long' else (self.cost - self.value)


    def add_position(self, vol, price):
        self.vol += vol
        self.cost += vol * price
        self.avg_cost_per_unit = self.cost/self.vol
        self.value = self.price * self.vol

    def get_position_info(self):
        info = {'symbol': self.symbol, 'direction': self.direction, 'price': self.price, 'vol':self.vol,
                'value': self.value, 'cost': self.cost, 'avg_cost_per_unit': self.avg_cost_per_unit,
                'marginreq':self.marginreq, 'marginratio':self.marginratio, 'unpl': self.upnl}
        return info


def combine_positions(position1, position2):
    if position1.direction == position2.direction:
        position = BasePosition(symbol=position1.symbol,
                                direction=position1.direction,
                                init_vol=position1.vol + position2.vol,
                                init_price=position1.price,
                                marginratio=position1.marginratio)

        position.cost = position1.cost + position2.cost
        position.avg_cost_per_unit = position.cost / position.vol
        position.marginreq = position.value * position.marginratio
        position.upnl = position1.upnl + position2.upnl
        return position

    else:
        print('position must be of the same direction')
        raise ValueError


class Position(object):
    def __init__(self, symbol):
        self.symbol = symbol
        # self.marginratio = marginratio
        self.long_t = BasePosition(symbol=symbol, direction='long', init_price=0, init_vol=0, marginratio=0)
        self.long_y = BasePosition(symbol=symbol, direction='long', init_price=0, init_vol=0, marginratio=0)
        self.short_t = BasePosition(symbol=symbol, direction='short', init_price=0, init_vol=0, marginratio=0)
        self.short_y= BasePosition(symbol=symbol, direction='short', init_price=0, init_vol=0, marginratio=0)
        self.vol = 0
        self.voldetail = {'long': 0, 'short': 0}
        self.price = 0
        self.value = 0
        self.valuedetail = {'long': 0, 'short': 0}
        self.marginreq = 0
        self.marginreqdetail = {'long': 0,
                                'short': 0}
        self.upnl =0
        self.upnldetail = {'long': 0, 'short': 0}
        self.pnl = 0
        # self.type = 'closed' if self.vol == 0 else 'open'

    def update_value_bar(self, price):
        self.BuyT.update_value(price)
        self.BuyY.update_value(price)
        self.SellT.update_value(price)
        self.SellY.update_value(price)

    def _combine_position(self, position1, position2):  # combine position 2 to position 1
        position1.vol += position2.vol
        position1.cost += position2.cost
        position1.upnl += position2.upnl

    def update_position_dayend(self):
        self._combine_position(self.BuyY, self.BuyT)
        self._combine_position(self.SellY, self.SellT)


if __name__ == '__main__':
    a = BasePosition('aaa', 'long',init_price=100,init_vol=100,marginratio=0.1)
    # b = BasePositionBar('aaa', 'buy',100,50,0.1)
    # print(a.get_position_info())
    a.add_position(price=120, vol=40)
    # print(a.get_position_info())
    a.close_position(70)
    # print(a.get_position_info())
    price = 170
    a.update_value(price)
    print(a.get_position_info())



    b = BasePosition('aaa', 'long',init_price=80,init_vol=80,marginratio=0.1)
    # b = BasePositionBar('aaa', 'buy',100,50,0.1)
    # print(a.get_position_info())
    b.add_position(price=100, vol=30)
    # print(a.get_position_info())
    b.close_position(20)
    # print(a.get_position_info())
    b.update_value(price)
    print(b.get_position_info())

    c = combine_positions(a,b)
    print(c.get_position_info())


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











































































































































