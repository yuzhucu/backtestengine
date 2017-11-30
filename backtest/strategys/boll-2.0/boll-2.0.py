# -*- coding: utf-8 -*-

'''
author:       sj
contact:      songjie1217@hotmail.com
description:
'''

__author__ = 'sj'

from backtest.core.backteststrategy import *
from backtest.optimizer.optimizer import *
from backtest.tools.ta import *
from datetime import datetime as dtL

class BollStrategyReverse(BacktestStrategy):
    def initialize(self):
        self.context.universe = ['SR801']
        self.context.run_info.strategy_name = 'bollReversePro30s-sr_main'
        self.context.run_info.feed_frequency = '30s'

        self.context.run_info.start_date = '2017-09-01'
        self.context.run_info.end_date = '2017-09-28'
        self.context.run_info.ip = localip
        self.context.run_info.main_contract = True

        self.context.init_cash = 1000000

        self.context.boll = Boll()
        self.context.cash = 1000000  # 初始资金
        self.context.cash_rate = 0.8  # 资金利用率
        # self.context.future_info = ts.get_future_info(self.context.universe[0]) # 获取合约属性
        self.context.slippage = 0  # 开仓价 变化幅度 2 个变动单位

        self.context.direction = ''
        self.context.open_vol = 0  # 当前开仓手数
        self.context.open_flag = False  # false表示没有开仓 true表示已经开仓了
        self.context.can_open_flag = True  # true 表示能继续开仓 false 表示已经开足仓了
        self.context.close_count = 0  # 平仓计数器
        self.context.open_price = 0
        self.context.max_dev = 0
        self.context.hold_flag = False
        self.context.temp_price = 0


    def order_change(self,order):
        print('update unit %s:' % datetime.datetime.now(),5)
        # print(self.context.open_vol)
        # print(order['vol'])
        # self.context.last_price = data['limit_price']
        if order['offset'] == OPEN:  # 开
            self.context.open_vol += order['vol']
        elif order['offset'] == CLOSE:  # 平今
            self.context.open_vol -= order['vol']

        print(self.context.open_vol)
        if self.context.open_vol > 0:
            self.context.open_flag = True
        else:
            self.context.open_flag = False
            self.context.direction = ''
        print(self.context.open_flag)

    def handle_data(self, data):
        boll = self.context.boll.compute(data)

        if boll is not None:
            print('date%d,time:%s, barclose:%d,up:%d,dn:.%d,mb:%d'%(self.context.date,self.context.current_bar.end_time,data.close,boll.up,boll.dn,boll.mb))
            print(self.context.open_price, self.context.instmt_info['tick_size'])
            print(data.close, self.context.open_price)
            print(self.context.open_flag, self.context.can_open_flag, self.context.direction)
            if not self.context.open_flag:
                if data.close > boll.up and self.context.direction == '':
                    # print('时间:%s 突破上轨' % datetime.now())
                    self.context.direction = BUY
                    print('change to buy')
                elif data.close < boll.dn and self.context.direction == '':
                    # print('时间:%s 突破下轨' % datetime.now())
                    self.context.direction = SELL
                    print('change to sell')

            if self.context.hold_flag:
                if data.close >= data.open and self.context.direction == SELL:
                    self._close_hold(data)
                elif data.close <= data.open and self.context.direction == BUY:
                    self._close_hold(data)
                else:
                    pass

            if self.context.open_flag and self.context.direction == BUY:
                cur_dev = self.context.open_price - data.low
                max_dev = self.context.max_dev
                self.context.max_dev = max(cur_dev, max_dev)

            if self.context.open_flag and self.context.direction == SELL:
                cur_dev = data.high - self.context.open_price
                max_dev = self.context.max_dev
                self.context.max_dev = max(cur_dev, max_dev)

            # 突破上轨后跌破中轨多单
            if data.close < boll.mb and self.context.direction == BUY and self.context.can_open_flag and not self.context.hold_flag:
                self._open(data)

            # 突破下轨后涨破中轨开空单
            if data.close > boll.mb and self.context.direction == SELL and self.context.can_open_flag and not self.context.hold_flag:
                self._open(data)

            # 开过多单后 收盘价超过中轨 平仓计数器 + 1 超过3次平仓
            if data.close > boll.mb and self.context.direction == BUY and self.context.open_flag and not self.context.hold_flag:
                self._close(data)

            # 开过空单后 收盘价跌破中轨 平仓计数器 + 1 超过3次平仓
            if data.close < boll.mb and self.context.direction == SELL and self.context.open_flag and not self.context.hold_flag:
                self._close(data)

            # if data.close < (self.context.open_price - 15 * self.context.instmt_info['tick_size']) and self.context.direction == BUY and self.context.open_flag:
            #     print('多单止损', self.context.open_price, data.close)
            #     self.context.close_count = 3
            #     self._close(data,type='stoploss')
            #
            # if data.close > (self.context.open_price + 15 * self.context.instmt_info['tick_size']) and self.context.direction == SELL and self.context.open_flag:
            #     print('空单止损', self.context.open_price, data.close)
            #     self.context.close_count = 3
            #     self._close(data,type='stoploss')

    def _open(self, bar):
        # 开空
        open_price = bar.close - self.context.slippage
        if self.context.direction == BUY:
            # 开多
            open_price = bar.close + self.context.slippage

        self.context.open_price = open_price
        # 计算当前bar的close价下最多能开多少手
        # 开仓手数 = (总资金 * 资金利用率）/(开仓价 * 保证金比例 * 每手吨数）
        open_vol = int((self.context.portfolio.avail_cash * self.context.cash_rate) / (open_price * self.context.instmt_info['broker_margin'] * 0.01 * self.context.instmt_info['contract_size']))
        # 部分成交情况下 满足布林开仓条件继续开仓
        available_open_vol = open_vol - self.context.open_vol

        if available_open_vol > 0:
            # print('时间:%s 开:%s 手' % (datetime.now(), available_open_vol))
            print('时间:%d %s 开:%s手' % (self.context.date, self.context.current_bar.end_time,available_open_vol))
            self.order(self.context.current_contract[0], self.context.direction, OPEN, available_open_vol, limit_price=open_price)
            self.context.can_open_flag = False
        # else:
        #     # 开足仓位
        #     self.context.can_open_flag = False


    def _close(self, bar, type=''):
        self.context.close_count += 1

        if self.context.close_count >= 3:
            if bar.close >= self.context.open_price and bar.close >= bar.open and self.context.direction == BUY:
                self.context.hold_flag = True
                self.context.temp_price = bar.close
            elif bar.close <= self.context.open_price and bar.close <= bar.open and self.context.direction == SELL:
                self.context.hold_flag = True
                self.context.temp_price = bar.close
            else:
                open_price = bar.close + self.context.slippage
                direction = BUY
                if self.context.direction == BUY:
                    # 平多
                    open_price = bar.close - self.context.slippage
                    direction = SELL

                if self.context.open_vol > 0:
                    # print('时间:%s 平今:%s 手' % (datetime.now(), self.context.open_vol))
                    print('时间:%d %s 平:%s 手' % (self.context.date, self.context.current_bar.end_time, self.context.open_vol))
                    self.order(self.context.current_contract[0], direction, CLOSE, self.context.open_vol, limit_price=open_price)
                    self.context.can_open_flag = True
                    self.context.open_flag = False
                    self.context.close_count = 0
                # else:
                    # 平光了又能开仓了
                    # self.context.can_open_flag = True
                    # self.context.close_count = 0

    def _close_hold(self,bar):
        open_price = bar.close + self.context.slippage
        direction = BUY
        diff_this_trans = (self.context.temp_price - bar.close) * self.context.open_vol*self.context.instmt_info['contract_size']
        if self.context.direction == BUY:
            # 平多
            open_price = bar.close - self.context.slippage
            direction = SELL
            diff_this_trans = (bar.close-self.context.temp_price) * self.context.open_vol * self.context.instmt_info[
                'contract_size']
        print('diff',diff_this_trans)
        if self.context.open_vol > 0:
            # print('时间:%s 平今:%s 手' % (datetime.now(), self.context.open_vol))
            print('时间:%d %s 平:%s 手' % (self.context.date, self.context.current_bar.end_time, self.context.open_vol))
            self.order(self.context.current_contract[0], direction, CLOSE, self.context.open_vol,
                       limit_price=open_price, diff = diff_this_trans)
            self.context.can_open_flag = True
            self.context.open_flag = False
            self.context.hold_flag = False
            self.context.close_count = 0


if __name__ == '__main__':
    t = BollStrategyReverse()
    t.run()