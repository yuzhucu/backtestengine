import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import pylab as pl
import xlwt
import datetime
from backtest.analyzer.output_config import *

class Stats(object):
    def __init__(self):
        self.backtestid = ''
        self.nv = np.array([])
        self.datetime = []
        self.dates = []
        self.transactions = []
        self.dailysummary = []
        self.tradecount = 0


    def maxdd(self):
        max_draw_down = 0
        temp_max_value = 0
        for i in range(1, len(self.nv)):
            temp_max_value = max(temp_max_value, self.nv[i - 1])
            max_draw_down = min(max_draw_down, self.nv[i] / temp_max_value - 1)
        return max_draw_down

    def returns(self, ret_type='log', freq='def'):
        if ret_type == 'simple':
            if freq == 'def':
                return self.__ret()
            elif freq == 'annual':
                return (self.__ret()/len(self.nv))*252
            elif freq == 'daily':
                return self.__ret()/len(self.nv)
            elif freq == 'month':
                return (self.__ret()/len(self.nv))*21
            else:
                print('please type in correct time frequency')
                raise ValueError

        elif ret_type == 'log':
            if freq == 'def':
                return self.__logret()
            elif freq == 'annual':
                return (self.__logret()/len(self.nv))*252
            elif freq == 'daily':
                return self.__logret()/len(self.nv)
            elif freq == 'month':
                return (self.__logret()/len(self.nv))*21
            else:
                print('please type in correct time frequency')
                raise ValueError
        else:
            print('please type in correct return type')
            raise ValueError

    def volatility(self, ret_type='log', freq='daily'):
        if ret_type == 'simple':
            if freq == 'daily':
                return self.__voli()
            elif freq == 'annual':
                return self.__voli() * math.sqrt(252)
            elif freq == 'month':
                return self.__voli() * math.sqrt(21)
            else:
                print('please type in correct time frequency')
                raise ValueError

        elif ret_type == 'log':
            if freq == 'daily':
                return self.__logvoli()
            elif freq == 'annual':
                return self.__logvoli() * math.sqrt(252)
            elif freq == 'month':
                return self.__logvoli() * math.sqrt(21)
            else:
                print('please type in correct time frequency')
                raise ValueError

        else:
            print('please type in correct return type')
            raise ValueError

    def sharpe(self, ret_type='log', freq='annual'):
        if ret_type == 'simple':
            if freq == 'annual':
                return ((self.__ret() / len(self.nv)) * 252) / self.__voli() * math.sqrt(252)
            elif freq == 'month':
                return ((self.__ret() / len(self.nv)) * 21) / self.__voli() * math.sqrt(21)
            else:
                print('please type in correct time frequency')
                raise ValueError

        elif ret_type == 'log':
            if freq == 'annual':
                return ((self.__logret() / len(self.nv)) * 252) / self.__logvoli() * math.sqrt(252)
            elif freq == 'month':
                return ((self.__logret() / len(self.nv)) * 21) / self.__logvoli() * math.sqrt(21)
            else:
                print('please type in correct time frequency')
                raise ValueError

        else:
            print('please type in correct return type')
            raise ValueError

    def total_commission(self):
        total_commission = 0
        for trans in self.transactions:
            total_commission += trans.commission

    def winratio(self):
        win = 0
        lose = 0
        for trans in self.transactions:
            if trans.pnl > 0:
                win += 1
            elif trans.pnl < 0:
                lose += 1
            else:
                pass
        return win

    def ptolratio(self):
        profit = 0
        loss = 0
        for trans in self.transactions:
            if trans.pnl > 0:
                profit += trans.pnl
            elif trans.pnl < 0:
                loss += trans.pnl
            else:
                pass
        return profit

    def nvplot(self):
        pl.plot(self.dates,self.nv)
        pl.show()

    def output(self, ret_type='simple', voli_freq='annual', sharpe_freq='annual', output_type='excel'):
        if output_type == 'excel':
            outputwb = xlwt.Workbook()
            overview = outputwb.add_sheet('overview')
            transdetail = outputwb.add_sheet('transactions')
            dailysummary = outputwb.add_sheet('daily_summary')
            netvalue = outputwb.add_sheet('net_value')

            overview.write(0, 0, 'true_return')
            overview.write(0, 1, self.returns(ret_type=ret_type, freq='def'))
            overview.write(1, 0, 'annual_return')
            overview.write(1, 1, self.returns(ret_type=ret_type, freq='annual'))
            overview.write(2, 0, 'volatility')
            overview.write(2, 1, self.volatility(ret_type=ret_type, freq=voli_freq))
            overview.write(3, 0, 'sharpe')
            overview.write(3, 1, self.volatility(ret_type=ret_type, freq=sharpe_freq))
            overview.write(4, 0, 'max_drawdown')
            overview.write(4, 1, self.maxdd())
            overview.write(5, 0, 'profit_to_loss ratio')
            overview.write(5, 1, self.ptolratio())
            overview.write(6, 0, 'win_ratio')
            overview.write(6, 1, self.winratio())
            overview.write(7, 0, 'total_commission')
            overview.write(7, 1, self.total_commission())
            overview.write(0, 3, 'initial_cash')
            overview.write(0, 4, float(self.nv[0]))
            overview.write(1, 3, 'final_value')
            overview.write(1, 4, float(self.nv[-1]))
            # overview.write(0, 6, self.nvplot())

            transdetail.write(0, 0, 'date')
            transdetail.write(0, 1, 'time')
            transdetail.write(0, 2, 'symbol')
            transdetail.write(0, 3, 'direction')
            transdetail.write(0, 4, 'offset')
            transdetail.write(0, 5, 'price')
            transdetail.write(0, 6, 'volume')
            transdetail.write(0, 7, 'commission')
            transdetail.write(0, 8, 'realized gain/loss')

            for i in range(0, len(self.transactions)):
                trans = self.transactions[i]
                transdetail.write(i+1, 0, trans.date)
                transdetail.write(i+1, 1, trans.time)
                transdetail.write(i+1, 2, trans.symbol)
                transdetail.write(i+1, 3, trans.direction)
                transdetail.write(i+1, 4, trans.offset)
                transdetail.write(i+1, 5, trans.price)
                transdetail.write(i+1, 6, trans.vol)
                transdetail.write(i+1, 7, trans.commission)
                transdetail.write(i+1, 8, trans.pnl)

            dailysummary.write(0, 0, 'date')
            dailysummary.write(0, 1, 'total_equity')
            dailysummary.write(0, 2, 'cash_available')
            dailysummary.write(0, 3, 'unrealized gain/loss')
            dailysummary.write(0, 4, 'realized gain/loss')
            dailysummary.write(0, 5, 'margin_req')
            dailysummary.write(0, 6, 'daily_comm')
            dailysummary.write(0, 7, 'risk_ratio')


            for j in range(0, len(self.dates)):
                daily = self.dailysummary[j]
                dailysummary.write(j+1, 0, daily.date)
                dailysummary.write(j+1, 1, daily.equity)
                dailysummary.write(j+1, 2, daily.cash)
                dailysummary.write(j+1, 3, daily.upnl)
                dailysummary.write(j+1, 4, daily.pnl)
                dailysummary.write(j+1, 5, daily.marginreq)
                dailysummary.write(j+1, 6, daily.daily_comm)
                dailysummary.write(j+1, 7, daily.riskratio)

            netvalue.write(0, 0, 'time')
            netvalue.write(0, 1, 'net_value')
            for i in range(0,len(self.datetime)):
                netvalue.write(i+1,0,self.datetime[i])
                netvalue.write(i+1,1,self.nv[i])


            outputwb.save('backtest-'+str(self.dates[0])+'-'+str(self.dates[-1])+'-'+self.backtestid+'.xls')

    def __ret(self):
        ret = self.nv[-1]/self.nv[0] - 1
        return ret

    def __logret(self):
        logret = math.log(self.nv[-1]/self.nv[0])
        return logret

    def __retls(self):
        retls = []
        i = 1
        while i < len(self.nv):
            retls.append(self.nv[i]/self.nv[i-1]-1)
            i += 1
        return np.array(retls)

    def __logretls(self):
        logretls = []
        i = 1
        while i < len(self.nv):
            logretls.append(math.log(self.nv[i]/self.nv[i-1]))
            i += 1
        return np.array(logretls)

    def __voli(self):
        voli = self.__retls().std(ddof=1)
        return voli

    def __logvoli(self):
        logvoli = self.__logretls().std(ddof=1)
        return logvoli




if __name__ == '__main__':
    out = Stats()
    ls = np.array([1,2,3,4,5,2,3,5,1,6,2,3,5,6])
    x = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
    out.nv = ls
    out.dates = x
    out.output()

