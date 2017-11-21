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
        self.init_marginreq = self.value * self.marginratio  # init margin requirement
        self.marginreq = self.init_marginreq  # latest margin requirement
        self.upnl = (self.value - self.cost) if self.direction == 'long' else (self.cost - self.value)  # unrealized gain/loss
        self.upnl_dayend = 0

    def clear_position(self):
        self.vol = 0
        self.cost = 0
        self.avg_cost_per_unit = 0
        self.value = 0
        self.marginreq = 0
        self.upnl = 0

    def update_value(self, price):
        self.price = price
        self.value = self.price*self.vol
        self.marginreq = self.value * self.marginratio
        self.upnl = (self.value - self.cost) if self.direction == 'long' else (self.cost - self.value)
        # print(self.price,self.vol,self.value,self.marginreq,self.marginratio,self.cost,self.upnl)

    def update_upnl(self, price):
        self.upnl = (self.vol*price - self.cost) if self.direction == 'long' else (self.cost - self.vol*price)
        # print('position update upnl')
        # print(self.upnl)

    def close_position(self, vol):
        # print('before close')
        # print(self.vol,self.price,self.vol,self.marginreq,self.cost,self.upnl)
        # print(vol)
        self.vol -= vol
        # print(self.vol)
        self.value = self.price*self.vol
        # print(self.value)
        self.marginreq = self.value * self.marginratio
        # print(self.marginreq)
        self.cost = self.avg_cost_per_unit * self.vol
        # print(self.cost)

        self.upnl = (self.value - self.cost) if self.direction == 'long' else (self.cost - self.value)
        # print(self.upnl)
        # print('after close')
        # print(self.vol,self.price,self.vol,self.marginreq,self.cost,self.upnl)

    def add_position(self, vol, price):
        # print('before add')
        # print(self.vol,self.price,self.vol,self.marginreq,self.cost,self.avg_cost_per_unit,self.upnl)
        self.vol += vol
        self.cost += vol * price
        self.avg_cost_per_unit = self.cost/self.vol
        self.value = self.price * self.vol
        self.init_marginreq += vol*price*self.marginratio
        # print('after add')
        # print(self.vol,self.price,self.vol,self.marginreq,self.cost,self.avg_cost_per_unit,self.upnl)

    def get_position_info(self):
        info = {'symbol': self.symbol, 'direction': self.direction, 'price': self.price, 'vol':self.vol,
                'value': self.value, 'cost': self.cost, 'avg_cost_per_unit': self.avg_cost_per_unit,
                'marginreq':self.marginreq, 'marginratio':self.marginratio, 'unpl': self.upnl}
        return info


class Position(object):
    def __init__(self, symbol,info):
        self.symbol = symbol
        # self.marginratio = marginratio
        self.long_t = BasePosition(symbol=symbol, direction='long', init_price=0, init_vol=0, marginratio=0)
        self.long_y = BasePosition(symbol=symbol, direction='long', init_price=0, init_vol=0, marginratio=0)
        self.short_t = BasePosition(symbol=symbol, direction='short', init_price=0, init_vol=0, marginratio=0)
        self.short_y = BasePosition(symbol=symbol, direction='short', init_price=0, init_vol=0, marginratio=0)
        self.vol_long = 0
        self.vol_short = 0
        self.price = 0
        self.cost_long = 0
        self.cost_short = 0
        self.avg_cost_long = 0
        self.avg_cost_short = 0
        self.value = 0
        self.init_marginreq = 0
        self.marginreq = 0
        self.marginratio = 0
        self.upnl = 0
        self.pnl = 0
        self.info = info
        # self.type = 'closed' if self.vol == 0 else 'open'

    def get_margin_req(self):
        # print(self.long_t.value,self.short_t.marginreq,self.long_y.marginreq,self.short_y.marginreq)
        return self.long_t.marginreq+self.short_t.marginreq+self.long_y.marginreq+self.short_y.marginreq

    def update_value(self, price):
        # print('beforeupdate')
        # print(self.long_t.upnl,self.long_y.upnl,self.short_t.upnl,self.short_y.upnl)
        self.long_t.update_value(price)
        self.long_y.update_value(price)
        self.short_t.update_value(price)
        self.short_y.update_value(price)
        self.price = price
        self.value = self.long_t.value+self.short_t.value+self.long_y.value+self.short_y.value
        self.init_marginreq = self.long_t.init_marginreq +self.short_t.init_marginreq+self.long_y.init_marginreq+self.short_y.init_marginreq
        self.marginreq = self.long_t.marginreq+self.short_t.marginreq+self.long_y.marginreq+self.short_y.marginreq
        self.upnl = self.long_t.upnl+self.short_t.upnl+self.long_y.upnl+self.short_y.upnl
        # print('afterupdate')
        # print(self.long_t.upnl, self.long_y.upnl, self.short_t.upnl, self.short_y.upnl)
    def update_upnl(self,price):
        self.long_t.update_upnl(price)
        self.long_y.update_upnl(price)
        self.short_t.update_upnl(price)
        self.short_y.update_upnl(price)
        self.upnl = self.long_t.upnl+self.long_y.upnl+self.short_t.upnl+self.short_y.upnl

    def get_upnl(self):
        return self.long_t.upnl + self.short_t.upnl + self.long_y.upnl + self.short_y.upnl

    def combine_position_dayend(self):
        self._combine_position(self.long_y, self.long_t)
        self._combine_position(self.short_y, self.short_t)

    def _combine_position(self, position1, position2):  # combine position 2 to position 1
        print('beforecombine')
        print(position1.symbol,position1.avg_cost_per_unit, position2.avg_cost_per_unit)
        print(position1.vol, position1.cost, position1.upnl)
        position1.vol += position2.vol
        position1.cost += position2.cost
        position1.upnl += position2.upnl
        position1.marginratio = position2.marginratio

        if position1.vol == 0:
            pass
        else:
            position1.avg_cost_per_unit = position1.cost / position1.vol
        position1.marginreq = position1.price*position1.vol * position1.marginratio
        print('aftercombine')
        print(position1.avg_cost_per_unit, position2.avg_cost_per_unit)
        print(position1.vol, position1.cost, position1.upnl)

        position2.clear_position()


def combine_positions(position1, position2):  #combine to a new position
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











































































































































