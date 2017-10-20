__author__ = 'Jimmy'
import numpy as np
from utils.objects import *
from trade.tradeType import *

#计算unit N
#计算unit N
class ATR(object):
    def __init__(self, account, cycle=20, dpp=10, coe=0.2):
        self.account = account
        self.bar = None
        self.cycle = cycle
        self.dpp = dpp
        self.n = 0
        self.count = 0
        self.coe = coe


    def compute(self, bar):
        if self.count == 0:
            self.bar = bar
            self.count += 1
            return AtrR(0,0)
        else:
            arr = np.array([bar.high - bar.low,bar.high - self.bar.close, self.bar.close - bar.low])
            tr = arr.max()

            if self.count < self.cycle + 1:
                self.n = (self.n * self.count + tr) / (self.count + 1)
            else:
                self.n = (self.n * (self.cycle -1) + tr) / self.cycle

            dv = self.n * self.dpp
            unit = int((0.01 * self.coe *self.account)/dv)
            self.bar = bar
            self.count += 1
            out = AtrR(unit,self.n)

            return out

# 计算n日突破信号
class BreakLimit(object):
    def __init__(self, cycle = 20):
        self.cycle = cycle
        self.highs = []
        self.lows = []


    def compute(self, bar):
        high_len = len(self.highs)
        if high_len < self.cycle:
            self._update(bar)
            return None
        elif high_len == self.cycle:
            arr_high = np.array(self.highs)
            arr_low = np.array(self.lows)
            max = arr_high.max()
            min = arr_low.min()
            del self.highs[0]
            del self.lows[0]
            self._update(bar)

            print('时间:%s BreakLimit=>max - min : %d - %d' % (dt.now(), max, min))

            if bar.close > max:
                return BlR(direction=BUY,price=max)
            elif bar.close < min:
                return BlR(direction=SELL,price=min)
            else:
                return None

    def _update(self, bar):
        self.highs.append(bar.high)
        self.lows.append(bar.low)


# 计算n日突破信号
class StopLimit(object):
    def __init__(self, cycle = 10):
        self.cycle = cycle
        self.highs = []
        self.lows = []


    def compute(self, bar):
        high_len = len(self.highs)
        if high_len < self.cycle:
            self._update(bar)
            return None
        elif high_len == self.cycle:
            arr_high = np.array(self.highs)
            arr_low = np.array(self.lows)
            max = arr_high.max()
            min = arr_low.min()
            del self.highs[0]
            del self.lows[0]
            self._update(bar)

            print('时间:%s StopLimit=>max - min : %d - %d' % (dt.now(), max, min))

            if bar.close > max :
                # print('空单止盈')
                return 'SELL_STOP'
            elif bar.close < min:
                # print('多单止盈')
                return 'BUY_STOP'
            else:
                return None

    def _update(self, bar):
        self.highs.append(bar.high)
        self.lows.append(bar.low)


# atr 计算结果
class AtrR(object):
    def __init__(self, unit, n):
        self.unit = unit
        self.n = n

    def __str__(self):
        return 'unit: %d, n: %.2f' %(self.unit, self.n)

# 均线突破结果
class BlR(object):
    def __init__(self, direction, price):
        self.direction = direction
        self.price = price

    def __str__(self):
        return 'direction: %s, price: %.2f' %(self.direction, self.price)


if __name__ == '__main__':
    print(ATR(1000000, cycle=20, dpp=50, coe=0.3))
    print(BreakLimit(cycle=20))
    print(StopLimit(cycle=10))