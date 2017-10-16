import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import pylab as pl
import xlwt

class Stats(object):
    def __init__(self):
        self.nv = np.array([])
        self.date = []
        self.transactions = []

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
        pl.plot(self.date,self.nv)
        pl.show()

    def output(self, ret_type='log', voli_freq='annual', sharpe_freq='annual', output_type='excel'):
        if output_type == 'excel':
            outputwb = xlwt.Workbook()
            overview = outputwb.add_sheet('overview')
            transdetail = outputwb.add_sheet('transactions')
            dailysummary = outputwb.add_sheet('daily_summary')
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
            overview.write(1, 3, 'final_cash')
            overview.write(1, 4, float(self.nv[-1]))
            
            outputwb.save('save.xls')

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





out = Stats()
ls = np.array([1,2,3,4,5,2,3,5,1,6,2,3,5,6])
x = [1,2,3,4,5,2,3,5,1,6,2,3,5,6]
out.nv = ls
out.date = x
out.output()

