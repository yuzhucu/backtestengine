# -*- coding: utf-8 -*-

'''
author:       sjsj
contact:      songjie1217@hotmail.com   
file:         portfolio.py
time:         2017/9/8 10:26
description: 

'''

__author__ = 'sjsj'

from backtest.position import *
from backtest.analyzer import *

class TransactionRecord(object):
    def __init__(self, symbol, direction, offset, vol, deal_price, commission, transtime, avg_cost=0):
        self.symbol = symbol
        self.direction = direction
        self.offset = offset
        self.vol = vol
        self.deal_price = deal_price
        self.commission = commission
        self.transtime = transtime
        self.pnl = 0


class Portfolio(object):
    def __init__(self, init_cash):

        self.init_cash = init_cash
        self.avail_cash = init_cash
        self.equity = init_cash
        self.positions = {}
        self.transrecord = {}
        self.closedpositions = {}
        self.stats = Stats()
        self.upnl = 0
        self.pnl = 0
        self.netvalue=[]


    def update_portfolio_tick(self,tick):
        for position in self.positions:
            self.positions[position].update_value_tick(tick)
        self.upnl = self._sum_upnl()
        self.pnl = self._sum_pnl()
        self.equity = self.init_cash + self.upnl + self.pnl
        self.avail_cash = self.equity - self._sum_marginreq()
        self.netvalue.append(self.equity)
        self._check_margin()

    def update_portfolio_dayend(self):
        for position in self.positions:
            self.positions[position].update_position_dayend()


    def add_cash(self, cash):
        self.init_cash = self.init_cash + cash

    def _open_position(self, symbol, direction, vol, price, marginratio, commission, time = '9999'):
        if symbol in self.positions:  # 持仓中已有该合约
            print('持仓中已有该合约')
            raise ValueError
        else:
            self.positions[symbol] = Position(symbol, marginratio)
            print('开仓')
            print(symbol, direction, vol, price, marginratio)
            if direction == 'buy':
                self.positions[symbol].BuyT = BasePosition(symbol=symbol, direction=direction, init_vol=vol,
                                                           init_price=price, marginratio=marginratio)
            else:
                self.positions[symbol].SellT = BasePosition(symbol=symbol, direction=direction, init_vol=vol,
                                                           init_price=price, marginratio=marginratio)

            self.avail_cash = self.avail_cash - self.positions[symbol].marginreq - commission
            print(self.positions[symbol].marginreq)
            self.positions[symbol].pnl = -commission
            if self.avail_cash < 0:
                print('保证金不足，无法开仓')
                raise ValueError
            self.transrecord[symbol + direction + 'open'+ time] = TransactionRecord(symbol, direction,'open',
                                                                                    vol, price, commission,time)

    def _close_position_T(self, symbol, direction, vol, price, commission =0, time = '9999'):  # 平今仓
        if symbol not in self.positions:  # 持仓中无该合约
            print('持仓中无该合约')
            raise ValueError
        else:  # 持仓中有该合约
            if direction == 'buy':  # 平多单
                if self.positions[symbol].BuyT.vol < vol:
                    print ('持仓量不足')
                    raise ValueError
                else:
                    self.positions[symbol].BuyT.close_position(vol=vol)
                    pnl_this_trans = (price - self.positions[symbol].BuyT.avg_cost_per_unit)*vol - commission
                    self.positions[symbol].pnl += pnl_this_trans

            else: # sell
                if self.positions[symbol].SellT.vol < vol:
                    print ('持仓量不足')
                    raise ValueError
                else:
                    self.positions[symbol].SellT.close_position(vol=vol)
                    pnl_this_trans = (self.positions[symbol].BuyT.avg_cost_per_unit-price)*vol - commission
                    self.positions[symbol].pnl += pnl_this_trans

            self.transrecord[symbol + direction + 'open' + time] = TransactionRecord(symbol, direction, 'close',
                                                                                     vol, price, commission,
                                                                                     time, pnl_this_trans)

    def _close_position_Y(self, symbol, direction, vol, price, commission=0, time = '9999'):  # 平昨仓
        if symbol not in self.positions:  # 持仓中无该合约
            print('持仓中无该合约')
            raise ValueError
        else:  # 持仓中有该合约
            if direction == 'buy':  # 平多单
                if self.positions[symbol].BuyY.vol < vol:
                    print('持仓量不足')
                    raise ValueError
                else:
                    self.positions[symbol].BuyY.close_position(vol=vol)
                    pnl_this_trans = (price - self.positions[symbol].BuyY.avg_cost_per_unit)*vol - commission
                    self.positions[symbol].pnl += pnl_this_trans

            else: # sell
                if self.positions[symbol].SellY.vol < vol:
                    print('持仓量不足')
                    raise ValueError
                else:
                    self.positions[symbol].SellY.close_position(vol=vol)
                    pnl_this_trans = (self.positions[symbol].SellY.avg_cost_per_unit-price)*vol - commission
                    self.positions[symbol].pnl += pnl_this_trans

            self.transrecord[symbol + direction + 'open' + time] = TransactionRecord(symbol, direction, 'close',
                                                                                     vol, price, commission,
                                                                                     time, pnl_this_trans)

    def _close_position(self, symbol, direction, vol, price, commission=0):  # 先平今再平昨
        pass


    def _add_position(self, symbol, direction, vol, price, commission=0):
        if symbol not in self.positions:
            print ('持仓中无此合约')
            raise ValueError
        else:
            if direction == 'buy':
                self.positions[symbol].BuyT.add_position(vol,price)
                self.positions[symbol].pnl -= commission
                self.avail_cash = vol*price*self.positions[symbol].marginratio
            else: # direction = sell
                self.positions[symbol].SellT.add_position(vol,price)
                self.positions[symbol].pnl -= commission
                self.avail_cash = vol * price * self.positions[symbol].marginratio
            if self.avail_cash <0:
                print('保证金不足，无法加仓')
                raise ValueError

    def modify_position(self, symbol, direction, offset, vol, price, marginratio=0, commissionT = 0, commissionY=0,time ='9999'):
        if offset == 'open':
            if symbol in self.positions:
                self._add_position(symbol=symbol, direction=direction, vol=vol, price=price, commission=commissionY)
            else: # open new position
                self._open_position(symbol=symbol, direction=direction, vol=vol, price=price, marginratio=marginratio, commission=commissionY)
        elif offset == 'CloseT':
            self._close_position_T(symbol=symbol, direction=direction, vol=vol, price=price, commission=commissionT)
        elif offset == 'CloseY':
            self._close_position_T(symbol=symbol, direction=direction, vol=vol, price=price, commission=commissionY)
        else:
            pass

    def _sum_upnl(self):
        upnl = 0
        for position in self.positions:
            upnl += self.positions[position].upnl
        return upnl

    def _sum_pnl(self):
        pnl = 0
        for position in self.positions:
            pnl += self.positions[position].pnl
        return pnl

    def _sum_marginreq(self):
        marginreq = 0
        for position in self.positions:
            marginreq += self.positions[position].marginreq
        return marginreq

    def _check_margin(self):
        if self._sum_marginreq() / self.equity > 1.25:
            print('期货有风险，您已出局')
            raise ValueError
        else:
            pass





# p = Portfolio(10000)
#
# p.add_position('aaa','buy',100,100,0.1)
#
#
# print(p.cash)
# print(p.equity)








