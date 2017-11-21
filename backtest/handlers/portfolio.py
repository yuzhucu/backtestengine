# -*- coding: utf-8 -*-

'''
author:       sjsj
contact:      songjie1217@hotmail.com   
file:         portfolio.py
time:         2017/9/8 10:26
description: 

'''

__author__ = 'sjsj'

from backtest.handlers.position import *
from backtest.handlers.order import *
from backtest.handlers.order_type import *
from backtest.analyzer.analyzer import *


class Portfolio(object):
    def __init__(self,init_cash):
        self.init_cash = init_cash
        self.frozen_cash = 0
        self.avail_cash = init_cash
        self.market_value = 0
        self.total_value = init_cash
        self.dayend_equity = 0
        self.pre_balance = init_cash
        self.dayend_balance = 0
        self.positions = {}
        self.stats = Stats()
        self.netvalue = []
        self.datetime = []
        self.upnl = 0
        self.pnl = 0
        self.dailypnl = 0
        self.marginreq = 0
        self.dailycomm = 0
        self.totalcomm = 0
        self.deposite = 0
        self.withdraw = 0
        self.riskratio = 0
        self.tradecount = 0


    def get_info(self):
        print('upnl:%d mreq:%d cash:%d dcomm:%d tcomm:%d rration:%d' %(self.upnl,self.marginreq,self.avail_cash,self.dailycomm,self.totalcomm,self.riskratio))

    def update_portfolio(self,price,time):
        # print(price)
        for position in self.positions:
            self.positions[position].update_value(price)
            # print(self.positions[position].long_t.upnl,self.positions[position].long_y.upnl,self.positions[position].short_t.upnl,self.positions[position].short_y.upnl)

        self.upnl = self._sum_upnl()
        self.marginreq = self._sum_marginreq()
        self.total_value = self.pre_balance + self.upnl + self.dailypnl - self.dailycomm
        # self.pnl = self._sum_pnl()
        # self.equity = self.init_cash + self.upnl + self.pnl
        # self.avail_cash = self.total_value - self._sum_marginreq()
        self.netvalue.append(self.total_value)
        self.datetime.append(time)

    def combine_portfolio_dayend(self):
        for position in self.positions:
            self.positions[position].combine_position_dayend()

    def dayend_summary(self,date, settlement_price):
        print('before dayend')
        print('upnl:%d mreq:%d cash:%d dcomm:%d tcomm:%d rration:%d' % (
        self.upnl, self.marginreq, self.avail_cash, self.dailycomm, self.totalcomm, self.riskratio))
        print('settlement price:', settlement_price)
        self._update_upnl(settlement_price)
        self.upnl = self._sum_upnl()

        dayend = DailySummary()
        dayend.date = date
        dayend.upnl = self.upnl
        dayend.marginreq = self.marginreq
        dayend.daily_comm = self.dailycomm
        dayend.positions = self.positions
        dayend.balance = self.pre_balance + self.dailypnl - self.dailycomm
        dayend.equity = self.pre_balance + self.dailypnl - self.dailycomm + self.upnl
        dayend.pnl = self.dailypnl
        dayend.cash = self.pre_balance + self.dailypnl - self.dailycomm + self.upnl - self.marginreq
        dayend.riskratio = (self.marginreq)/(self.pre_balance + self.dailypnl - self.dailycomm + self.upnl)

        print(dayend.__dict__)

        # print('upnl:%d mreq:%d cash:%d dcomm:%d tcomm:%d rration:%d' % (
        # self.upnl, self.marginreq, self.avail_cash, self.dailycomm, self.totalcomm, self.riskratio))

        self.stats.dailysummary.append(dayend)

        self.avail_cash = dayend.cash
        self.riskratio = dayend.riskratio
        self.total_value = dayend.equity

        self.pre_balance += self.dailypnl - self.dailycomm
        self.dailypnl = 0
        self.totalcomm += self.dailycomm
        self.dailycomm = 0

        print('after dayend')
        print('upnl:%d mreq:%d cash:%d dcomm:%d tcomm:%d rration:%d' % (
        self.upnl, self.marginreq, self.avail_cash, self.dailycomm, self.totalcomm, self.riskratio))

        self._check_margin()





    # def add_cash(self, cash):
    #     self.init_cash += cash
    #     self.total_value += cash

    def _open_position(self, symbol, direction, vol, price, marginratio, commission, time='9999', date=9999,info=''):
        comm_this_trans = 0
        if symbol in self.positions:  # 持仓中已有该合约
            print('持仓中已有该合约')
            raise ValueError
        else:
            self.positions[symbol] = Position(symbol,info)
            # print('开仓', symbol, direction, vol, price, marginratio)
            if direction == 'long':
                self.positions[symbol].long_t = BasePosition(symbol=symbol, direction=direction, init_vol=vol,
                                                           init_price=price, marginratio=marginratio)
            else:
                self.positions[symbol].short_t = BasePosition(symbol=symbol, direction=direction, init_vol=vol,
                                                           init_price=price, marginratio=marginratio)
            print(self.positions[symbol].info)
            # print(self.positions[symbol].get_margin_req())
            # print('self.positions[symbol].upnl before update')
            # print(self.positions[symbol].upnl)
            self.positions[symbol].marginratio = marginratio
            self.positions[symbol].marginreq = self.positions[symbol].get_margin_req()
            # self.positions[symbol].upnl = self.positions[symbol].get_upnl()
            # print('self.positions[symbol].upnl')
            # print(self.positions[symbol].upnl )
            self.marginreq = self._sum_marginreq()
            self.upnl = self._sum_upnl()
            if self.positions[symbol].info['commission_type']=='value':
                comm_this_trans = vol*price*commission
            elif self.positions[symbol].info['commission_type']=='vol':
                comm_this_trans = vol / self.positions[symbol].info['contract_size'] * commission
            self.avail_cash -= self.positions[symbol].get_margin_req() + comm_this_trans
            self.dailycomm += comm_this_trans
            # print(self.positions[symbol].marginreq)
            # self.positions[symbol].pnl = -commission
            if self.avail_cash < 0:
                print('保证金不足，无法开仓')
                raise ValueError
            self.stats.transactions.append(TransactionRecord(symbol,direction,'open',vol,price,comm_this_trans,time,date,0))

    def _add_position(self, symbol, direction, vol, price, commission, time = '9999',date=9999):
        comm_this_trans = 0
        if symbol not in self.positions:
            print ('持仓中无此合约')
            raise ValueError
        else:
            if direction == 'long':
                if self.positions[symbol].long_t.vol == 0:
                    self.positions[symbol].long_t = BasePosition(symbol=symbol, direction=direction, init_vol=vol,
                                                           init_price=price, marginratio=self.positions[symbol].marginratio)
                    self.positions[symbol].marginreq = self.positions[symbol].get_margin_req()
                    # self.positions[symbol].upnl = self.positions[symbol].get_upnl()
                    # print('self.positions[symbol].upnl')
                    # print(self.positions[symbol].upnl )
                    self.marginreq = self._sum_marginreq()
                    self.upnl = self._sum_upnl()
                    if self.positions[symbol].info['commission_type'] == 'value':
                        comm_this_trans = vol * price * commission
                    elif self.positions[symbol].info['commission_type'] == 'vol':
                        comm_this_trans = vol / self.positions[symbol].info['contract_size'] * commission
                    self.avail_cash -= self.positions[symbol].long_t.marginratio*vol*price + comm_this_trans
                    self.dailycomm += comm_this_trans
                    # print(self.positions[symbol].marginreq)
                    # self.positions[symbol].pnl = -commission
                    if self.avail_cash < 0:
                        print('保证金不足，无法开仓')
                        raise ValueError

                else:
                    self.positions[symbol].long_t.add_position(vol, price)
                    self.positions[symbol].update_value(price)
                    self.marginreq = self._sum_marginreq()
                    self.upnl = self._sum_upnl()
                    if self.positions[symbol].info['commission_type'] == 'value':
                        comm_this_trans = vol * price * commission
                    elif self.positions[symbol].info['commission_type'] == 'vol':
                        comm_this_trans = vol / self.positions[symbol].info['contract_size'] * commission

                    self.dailycomm += comm_this_trans
                    self.avail_cash -= vol*price*self.positions[symbol].long_t.marginratio + comm_this_trans
            else: # direction = short
                if self.positions[symbol].short_t.vol == 0:
                    self.positions[symbol].short_t = BasePosition(symbol=symbol, direction=direction, init_vol=vol,
                                                           init_price=price, marginratio=self.positions[symbol].marginratio)
                    self.positions[symbol].marginreq = self.positions[symbol].get_margin_req()
                    # self.positions[symbol].upnl = self.positions[symbol].get_upnl()
                    # print('self.positions[symbol].upnl')
                    # print(self.positions[symbol].upnl )
                    self.marginreq = self._sum_marginreq()
                    self.upnl = self._sum_upnl()
                    if self.positions[symbol].info['commission_type'] == 'value':
                        comm_this_trans = vol * price * commission
                    elif self.positions[symbol].info['commission_type'] == 'vol':
                        comm_this_trans = vol / self.positions[symbol].info['contract_size'] * commission
                    self.avail_cash -= self.positions[symbol].short_t.marginratio*vol*price + comm_this_trans
                    self.dailycomm += comm_this_trans
                    # print(self.positions[symbol].marginreq)
                    # self.positions[symbol].pnl = -commission
                    if self.avail_cash < 0:
                        print('保证金不足，无法开仓')
                        raise ValueError
                else:
                    self.positions[symbol].short_t.add_position(vol, price)
                    self.positions[symbol].update_value(price)
                    self.marginreq = self._sum_marginreq()
                    self.upnl = self._sum_upnl()
                    if self.positions[symbol].info['commission_type'] == 'value':
                        comm_this_trans = vol * price * commission
                    elif self.positions[symbol].info['commission_type'] == 'vol':
                        comm_this_trans = vol / self.positions[symbol].info['contract_size'] * commission

                    self.dailycomm += comm_this_trans
                    self.avail_cash -= vol * price * self.positions[symbol].long_t.marginratio + comm_this_trans

            if self.avail_cash <0:
                print('保证金%d' % self.avail_cash)
                print('保证金不足，无法加仓')
                raise ValueError

            print("commthistrans", comm_this_trans)
            self.stats.transactions.append(
                TransactionRecord(symbol, direction, 'open', vol, price, comm_this_trans, time, date, 0))

    def _close_position_t(self, symbol, direction, vol, price, commission =0, time='9999',date=9999,type='',max_dev = 0):  # 平今仓
        comm_this_trans = 0
        if symbol not in self.positions:  # 持仓中无该合约
            print('持仓中无该合约')
            raise ValueError
        else:  # 持仓中有该合约
            if direction == 'long':  # 平多单
                if self.positions[symbol].long_t.vol < vol:
                    # print(vol)
                    print ('持今仓量不足')
                    raise ValueError
                else:
                    pnl_this_trans = (price - self.positions[symbol].long_t.avg_cost_per_unit)*vol
                    if self.positions[symbol].info['commission_type'] == 'value':
                        comm_this_trans = vol * price * commission
                    elif self.positions[symbol].info['commission_type'] == 'vol':
                        comm_this_trans = vol / self.positions[symbol].info['contract_size'] * commission
                    self.avail_cash += self.positions[symbol].long_t.init_marginreq + pnl_this_trans + comm_this_trans
                    # print(self.positions[symbol].long_t.upnl, self.positions[symbol].long_y.upnl,
                    #       self.positions[symbol].short_t.upnl, self.positions[symbol].short_y.upnl)
                    self.positions[symbol].long_t.close_position(vol=vol)
                    self.positions[symbol].update_value(price)
                    # print(self.positions[symbol].long_t.upnl,self.positions[symbol].long_y.upnl,self.positions[symbol].short_t.upnl,self.positions[symbol].short_y.upnl)
                    self.marginreq = self._sum_marginreq()
                    self.upnl = self._sum_upnl()
                    # print(self.marginreq,self.upnl)
                    self.dailypnl += pnl_this_trans
                    self.dailycomm += comm_this_trans


            else: # short
                if self.positions[symbol].short_t.vol < vol:
                    # print(vol)
                    print ('持今仓量不足')
                    raise ValueError
                else:
                    pnl_this_trans = (self.positions[symbol].short_t.avg_cost_per_unit-price)*vol
                    if self.positions[symbol].info['commission_type'] == 'value':
                        comm_this_trans = vol * price * commission
                    elif self.positions[symbol].info['commission_type'] == 'vol':
                        comm_this_trans = vol / self.positions[symbol].info['contract_size'] * commission
                    self.avail_cash += self.positions[symbol].short_t.init_marginreq + pnl_this_trans + comm_this_trans
                    self.positions[symbol].short_t.close_position(vol=vol)
                    self.positions[symbol].update_value(price)
                    self.marginreq = self._sum_marginreq()
                    self.upnl = self._sum_upnl()
                    self.dailypnl += pnl_this_trans
                    self.dailycomm += comm_this_trans


            self.stats.transactions.append(TransactionRecord(symbol, direction, 'closeT', vol, price, comm_this_trans, time, date,pnl_this_trans,type,max_dev))

    def _close_position_y(self, symbol, direction, vol, price, commission=0, time = '9999',date=9999,type='',max_dev = 0):  # 平昨仓
        comm_this_trans = 0
        if symbol not in self.positions:  # 持仓中无该合约
            print('持仓中无该合约')
            raise ValueError
        else:  # 持仓中有该合约
            if direction == 'long':  # 平多单
                if self.positions[symbol].long_y.vol < vol:
                    print('持昨仓量不足')
                    raise ValueError
                else:
                    pnl_this_trans = (price - self.positions[symbol].long_y.avg_cost_per_unit)*vol
                    # comm_this_trans = 0
                    if self.positions[symbol].info['commission_type'] == 'value':
                        comm_this_trans = vol * price * commission
                    elif self.positions[symbol].info['commission_type'] == 'vol':
                        comm_this_trans = vol / self.positions[symbol].info['contract_size'] * commission
                    self.avail_cash += self.positions[symbol].long_y.init_marginreq + pnl_this_trans + comm_this_trans
                    self.positions[symbol].long_y.close_position(vol=vol)
                    self.positions[symbol].update_value(price)
                    self.marginreq = self._sum_marginreq()
                    self.upnl = self._sum_upnl()
                    self.dailypnl += pnl_this_trans
                    self.dailycomm += comm_this_trans


            else: # short
                if self.positions[symbol].short_y.vol < vol:
                    print('持昨仓量不足')
                    raise ValueError
                else:
                    pnl_this_trans = (self.positions[symbol].short_y.avg_cost_per_unit-price)*vol
                    # comm_this_trans = 0
                    if self.positions[symbol].info['commission_type'] == 'value':
                        comm_this_trans = vol * price * commission
                    elif self.positions[symbol].info['commission_type'] == 'vol':
                        comm_this_trans = vol / self.positions[symbol].info['contract_size'] * commission
                    self.avail_cash += self.positions[symbol].short_y.init_marginreq + pnl_this_trans + comm_this_trans
                    self.positions[symbol].short_y.close_position(vol=vol)
                    self.positions[symbol].update_value(price)
                    self.marginreq = self._sum_marginreq()
                    self.upnl = self._sum_upnl()
                    self.dailypnl += pnl_this_trans
                    self.dailycomm += comm_this_trans

            self.stats.transactions.append(TransactionRecord(symbol, direction, 'closeY', vol, price, comm_this_trans, time,date, pnl_this_trans,type,max_dev))

    def _close_position(self, symbol, direction, vol, price, commission_t=0,commission_y=0,time='9999',date=9999, exch_code='',type='',max_dev = 0):  # 先平今再平昨
        # print(self.positions[symbol].long_t.vol)
        if symbol not in self.positions:  # 持仓中无该合约
            print('持仓中无该合约')
            raise ValueError
        else:  # 持仓中有该合约
            if direction == 'long':  # 平多单
                if self.positions[symbol].long_t.vol >= vol:
                    self._close_position_t(symbol,direction, vol, price, commission_t, time, date,type,max_dev)
                else:
                    vol_t = self.positions[symbol].long_t.vol
                    vol_y = vol-self.positions[symbol].long_t.vol
                    self._close_position_t(symbol, direction, vol_t, price, commission_y, time, date,type,max_dev)
                    self._close_position_y(symbol, direction, vol_y, price, commission_y, time, date,type,max_dev)

            else: # sell
                if self.positions[symbol].short_t.vol >= vol:
                    self._close_position_t(symbol,direction, vol, price, commission_t, time, date,type,max_dev)
                else:
                    vol_t = self.positions[symbol].short_t.vol
                    vol_y = vol-self.positions[symbol].short_t.vol
                    self._close_position_t(symbol, direction, vol_t, price, commission_y, time, date,type,max_dev)
                    self._close_position_y(symbol, direction, vol_y, price, commission_y, time, date,type,max_dev)

    def modify_position(self, symbol, direction, offset, vol, price, marginratio=0, comm_t=0, comm_y=0, comm_o=0, time ='9999', date=9999, exch_code='',info={},type='',max_dev=0):
        print('modify direction:%s offset:%s vol:%d price:%d date:%d time:%s now:%s' % (direction, offset, vol, price, date, time, datetime.datetime.now()))
        print("comm", comm_o,comm_t,comm_y)
        print('available cash:', self.avail_cash)
        print('modify portfolio %s:' % datetime.datetime.now(), 4)
        # print('before trade')
        # print(self.positions[symbol].long_t.upnl,self.positions[symbol].long_y.upnl,self.positions[symbol].short_t.upnl,self.positions[symbol].short_y.upnl)
        # print(exch_code)
        self.tradecount += 1
        if offset == 'open':
            if symbol in self.positions:
                self._add_position(symbol=symbol, direction=direction, vol=vol, price=price, commission=comm_o, time=time, date=date)
            else: # open new position
                self._open_position(symbol=symbol, direction=direction, vol=vol, price=price, marginratio=marginratio, commission=comm_o, time=time, date=date,info=info)

        elif offset == 'close_t':
            if exch_code == 'CZCE' or exch_code == 'DCE':
                self._close_position(symbol=symbol, direction=direction, vol=vol, price=price, commission_t=comm_t, commission_y=comm_y, time=time, date=date,type=type,max_dev=max_dev)
            elif exch_code == 'SHFE':
                self._close_position_t(symbol=symbol, direction=direction, vol=vol, price=price, commission=comm_t, time=time, date=date,type=type,max_dev=max_dev)
            else:
                print('please enter correct exchange code')
                raise ValueError

        elif offset == 'close_y':
            if exch_code == 'CZCE' or exch_code == 'DCE':
                self._close_position(symbol=symbol, direction=direction, vol=vol, price=price, commission_t=comm_t, commission_y=comm_y, time=time,date=date,type=type,max_dev=max_dev)
            elif exch_code == 'SHFE':
                self._close_position_y(symbol=symbol, direction=direction, vol=vol, price=price, commission=comm_y, time=time, date=date,type=type,max_dev=max_dev)
            else:
                print('please enter correct exchange code')
                raise ValueError

        elif offset == 'close':
            if exch_code == 'CZCE' or exch_code == 'DCE':
                self._close_position(symbol=symbol, direction=direction, vol=vol, price=price, commission_t=comm_t, commission_y=comm_y, time=time,date=date,type=type,max_dev=max_dev)
            elif exch_code == 'SHFE':
                self._close_position_y(symbol=symbol, direction=direction, vol=vol, price=price, commission=comm_y, time=time, date=date,type=type,max_dev=max_dev)
            else:
                print('please enter correct exchange code')
                raise ValueError
        else:
            pass
        print('after trade')
        print(self.positions[symbol].long_t.upnl, self.positions[symbol].long_y.upnl,
              self.positions[symbol].short_t.upnl, self.positions[symbol].short_y.upnl)

    def _sum_upnl(self):
        upnl = 0
        for position in self.positions:
            # print('upnl:')
            # print(position)
            # print(self.positions[position].upnl)
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
            # print(self.positions[position].marginreq)
            marginreq += self.positions[position].marginreq
        return marginreq

    def _sum_value(self):
        totalvalue = 0
        for position in self.positions:
            totalvalue += self.positions[position].value
        return totalvalue

    def _update_upnl(self,price):
        for position in self.positions:
            self.positions[position].update_upnl(price)

    def _check_margin(self):
        if self.riskratio > 1.25:
            print('期货有风险，您已出局')
            raise ValueError
        else:
            pass









