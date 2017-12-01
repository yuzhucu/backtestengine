# encoding: utf-8


"""
@version: python3.6
@author: ‘sj‘
@contact: songjie1217@hotmail.com
@file: boll-stoploss.py
@time: 11/6/17 1:59 PM
"""


from backtest.core.backteststrategy_test import *
from backtest.optimizer.optimizer import *
from backtest.tools.ta import *
from datetime import datetime as dtL

class BollStrategyNew(BacktestStrategyTest):
    def initialize(self):
        self.context.universe = ['SR801']
        self.context.run_info.strategy_name = 'boll2.0-sr_main-3m-closesettle'
        self.context.run_info.feed_frequency = '3m'

        self.context.run_info.start_date = '2017-10-01'
        self.context.run_info.end_date = '2017-10-27'
        self.context.run_info.ip = localip
        self.context.run_info.main_contract = True

        self.context.init_cash = 1000000

        self.context.boll = Boll()
        self.context.cash_rate = 0.8  # cash usage
        self.context.slippage = 0

        self.context.direction = ''
        self.context.open_vol = 0
        self.context.open_flag = False
        self.context.close_flag = False
        self.context.reverse_flag = False
        self.context.close_count = 0
        self.context.reverse_count = 0
        self.context.open_price = 0
        self.context.open_bar_open = 0
        self.context.max_dev = 0
        self.context.hold_flag = False
        self.context.temp_price = 0

    def order_change(self,order):
        pass

    def handle_data(self, data):
        boll = self.context.boll.compute(data)

        if boll is not None:
            # print('date%d,time:%s, barclose:%d,up:%d,dn:.%d,mb:%d'%(self.context.date,self.context.current_bar.end_time,data.close,boll.up,boll.dn,boll.mb))
            # print(self.context.open_price, self.context.instmt_info['tick_size'])
            # print(data.close, self.context.open_price)
            # print(self.context.open_flag, self.context.can_open_flag, self.context.direction)
            print(self.context.open_bar_open, data.close)
            if not self.context.open_flag:
                if data.close > boll.up:
                    # print('时间:%s 突破上轨' % datetime.now())
                    self.context.direction = SHORT
                    print('change to short')
                elif data.close < boll.dn:
                    # print('时间:%s 突破下轨' % datetime.now())
                    self.context.direction = LONG
                    print('change to long')

            # prerequisites for opening positions
            preq_one = False
            if (boll.up - boll.dn)/boll.mb > 0.006:
                preq_one = True

            preq_two = False
            if abs((data.close - data.open)/boll.mb) <= 0.01:
                preq_two = True


            # open long position
            if boll.dn < data.close < boll.mb and data.close > data.open and preq_one and preq_two and self.context.direction == LONG and not self.context.open_flag:
                self._open(data,'signal_open')

            # open short position
            if boll.up > data.close > boll.mb and data.close < data.open and preq_one and preq_two and self.context.direction == SHORT and not self.context.open_flag:
                self._open(data,'signal_open')

            # prerequisites for close long position, barK.close > mb
            if data.close > boll.mb and self.context.direction == LONG and self.context.open_flag and not self.context.reverse_flag:
                self.context.close_flag = True

            # prerequisites for close short position, barK.close < mb
            if data.close < boll.mb and self.context.direction == SHORT and self.context.open_flag and not self.context.reverse_flag:
                self.context.close_flag = True

            # prerequisites for close reverse long position, barK.close > mb
            if data.close < boll.mb and self.context.direction == LONG and self.context.open_flag and self.context.reverse_flag:
                self.context.close_flag = True

            # prerequisites for close reverse short position, barK.close < mb
            if data.close > boll.mb and self.context.direction == SHORT and self.context.open_flag and self.context.reverse_flag:
                self.context.close_flag = True

            # close long position, close count + 1
            if data.close < boll.mb and data.close < data.open and self.context.direction == LONG and self.context.close_flag and not self.context.reverse_flag:
                self._close(data, 'signal close')

            # close short position, close count + 1
            if data.close > boll.mb and data.close > data.open and self.context.direction == SHORT and self.context.close_flag and not self.context.reverse_flag:
                self._close(data, 'signal close')

            # close reverse long position, close count + 1
            if data.close > boll.mb and data.close > data.open and self.context.direction == LONG and self.context.close_flag and self.context.reverse_flag:
                self._close(data, 'reverse close')

            # close reverse short position, close count + 1
            if data.close < boll.mb and data.close < data.open and self.context.direction == SHORT and self.context.close_flag and self.context.reverse_flag:
                self._close(data, 'reverse close')

            # stoploss long position:
            if (self.context.open_price - data.close) > boll.mb * 0.006 and self.context.direction == LONG and self.context.open_flag:
                self._close(data, 'stoploss close')

            # stoploss short position:
            if (data.close - self.context.open_price) > boll.mb * 0.006 and self.context.direction == SHORT and self.context.open_flag:
                self._close(data, 'stoploss close')

            # stoploss-reverse long position:
            if data.close < data.open and data.close < self.context.open_bar_open and self.context.direction == LONG and self.context.open_flag and not self.context.reverse_flag:
                self._reverse(data, boll)

            # stoploss-reverse short position:
            if data.close > data.open and data.close > self.context.open_bar_open and self.context.direction == SHORT and self.context.open_flag and not self.context.reverse_flag:
                self._reverse(data, boll)

    def _reverse(self, bar, boll):
        self.context.reverse_count += 1
        if self.context.reverse_count >= 2:
            # print('reverse signal')
            print(self.context.open_flag)
            # print('reverse stoploss')
            self._close(bar, type = 'reverse stoploss')
            # print('reverse stoploss finish')
            self.context.direction = LONG
            if bar.close < self.context.open_bar_open:
                self.context.direction = SHORT
            self._open(bar, type = 'reverse open')

    def _open(self, bar, type = ''):
        # 开空
        open_price = bar.close - self.context.slippage
        if self.context.direction == LONG:
            # 开多
            open_price = bar.close + self.context.slippage

        self.context.open_price = open_price
        self.context.open_bar_open = bar.open
        # 计算当前bar的close价下最多能开多少手
        # 开仓手数 = (总资金 * 资金利用率）/(开仓价 * 保证金比例 * 每手吨数）
        open_vol = int((self.context.portfolio.avail_cash * self.context.cash_rate) / (open_price * self.context.instmt_info['broker_margin'] * 0.01 * self.context.instmt_info['contract_size']))
        print('时间:%d %s 开:%s手 类型:%s' % (self.context.date, self.context.current_bar.end_time,open_vol,type))
        self.order(self.context.current_contract[0], self.context.direction, OPEN, open_vol, limit_price=open_price, type = type)
        self.context.open_flag = True
        self.context.open_vol = open_vol
        self.context.open_price = open_price
        if type == 'reverse open':
            self.context.reverse_flag = True


    def _close(self, bar, type=''):
        print('close type', type)
        if type == 'signal close' or type == 'reverse close':
            print('type 1')
            self.context.close_count += 1
            if self.context.close_count >= 3:
                self.__close_base(bar, type)

        elif type == 'reverse stoploss' or type == 'stoploss close':
            print('type 2 ')
            self.__close_base(bar, type)


    def __close_base(self, bar,type=''):
        close_price = bar.close + self.context.slippage
        direction = SHORT
        if self.context.direction == LONG:
            # 平多
            close_price = bar.close - self.context.slippage
            direction = LONG

        if self.context.open_flag:
            print('时间:%d %s 平:%s 手 类型:%s' % (self.context.date, self.context.current_bar.end_time, self.context.open_vol,type))
            self.order(self.context.current_contract[0], direction, CLOSE, self.context.open_vol,
                       limit_price=close_price, type=type)
            self.context.open_flag = False
            self.context.close_flag = False
            self.context.reverse_flag =False
            self.context.open_vol = 0
            self.context.close_count = 0
            self.context.open_price = 0
            self.context.direction = ''
            self.context.reverse_count = 0


if __name__ == '__main__':
    t = BollStrategyNew()
    t.run()