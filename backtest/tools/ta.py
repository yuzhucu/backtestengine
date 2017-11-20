__author__ = 'Jimmy'
import numpy as np
from backtest.handlers.order_type import *

#计算unit N
#计算unit N
class ATR(object):
    def __init__(self, account, cycle=20, dpp=50, coe=0.2):
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
            return AtrR(0, 0)
        else:
            arr = np.array([bar.high - bar.low, bar.high - self.bar.close, self.bar.close - bar.low])
            tr = arr.max()
            # print(tr)

            if self.count < self.cycle + 1:
                self.n = (self.n * self.count + tr) / (self.count + 1)
            else:
                self.n = (self.n * (self.cycle - 1) + tr) / self.cycle

            dv = self.n * self.dpp
            # print(dv)
            unit = int((0.01 * self.coe * self.account)/dv)
            # print(unit)
            self.bar = bar
            self.count += 1
            out = AtrR(unit, self.n)

            return out

# 计算n日突破信号
class BreakLimit(object):
    def __init__(self, cycle=20):
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

            # print('时间:%s BreakLimit=>max - min : %d - %d' % (dt.now(), max, min))

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

            # print('时间:%s StopLimit=>max - min : %d - %d' % (dt.now(), max, min))

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


class Boll(object):
    def __init__(self, cycle = 26, k=2):
        self._cycle = cycle
        self._k = k
        self._close_prices=[]


    def compute(self, bar):
        bar_length = len(self._close_prices)
        if bar_length < self._cycle - 1:
            self._close_prices.append(bar.close)
            return None
        else:
            # 计算n-1个bar的close均值 即中轨
            temp1 = np.array(self._close_prices)
            mb = temp1.mean()

            self._close_prices.append(bar.close)
            temp2 = np.array(self._close_prices)
            # n个bar的标准差
            md = temp2.std()
            up = mb + self._k * md  # 上轨 = 中轨 + k * n个bar标准差
            dn = mb - self._k * md  # 下轨 = 中轨 - k * n个bar标准差
            bollR = BollR(up,mb,dn)
            del self._close_prices[0]
            return bollR

class BollR(object):
    def __init__(self, up, mb, dn):
        self.up = up
        self.mb = mb
        self.dn = dn

    def __str__(self):
        return 'Boll: up %.2f, mb: %.2f, dn: %.2f' %(self.up, self.mb, self.dn)


class KDJ(object):
    def __init__(self, k1, d1, cyclenum,a = 1/3, b=1/3, ):
        self.a = a
        self.b = b
        # self.k1 = k1
        # self.d1 = d1
        self.cyclenum = cyclenum
        self.barlow = []
        self.barhigh = []

    def compute(self,bar,k1,d1):
        self.barlow.append(bar.low)
        self.barhigh.append(bar.high)
        # print(self.barlow)
        # print(self.barhigh)
        bar_len = len(self.barlow)
        if bar_len < self.cyclenum:
            return None
        else:
            high = max(self.barhigh)
            low = min(self.barlow)
            close = bar.close
            if high != low:
                rsv = 100 * (close - low)/(high - low)
            else:
                rsv = 50
            k2 = (1 - self.a) * k1 + self.a * rsv
            d2 = (1 - self.b) * d1 + self.b * k2
            j2 = 3*k2 - 2*d2
            kdjout = KDJOut(k1=k1,d1=d1,k2=k2,d2=d2,j2=j2)
            del self.barhigh[0]
            del self.barlow[0]
            return kdjout


class KDJOut(object):
    def __init__(self, k1, d1, k2,d2,j2):
        self.k1 = k1
        self.k2 = k2
        self.d1 = d1
        self.d2 = d2
        self.j2 = j2

    def __str__(self):
        return 'KDJ: k1 %.2f, d1: %.2f, k2: %.2f, d2: %.2f, j1: %.2f' %(self.k1, self.d1, self.k2, self.d2, self.j2)


if __name__ == '__main__':
    print(ATR(1000000, cycle=20, dpp=50, coe=0.3))
    print(BreakLimit(cycle=20))
    print(StopLimit(cycle=10))