# encoding: utf-8


"""
@version: python3.6
@author: ‘sj‘
@contact: songjie1217@hotmail.com
@file: boll-liao.py
@time: 11/14/17 2:57 PM
"""

from backtest.core.backteststrategy import *
from backtest.optimizer.optimizer import *
from backtest.tools.ta import *
from datetime import datetime as dt

class BollStrategyReverse(BacktestStrategy):
    def initialize(self):
        self.context.universe = ['SR801']
        self.context.run_info.strategy_name = 'boll30s-sr_main-liao-3m'
        self.context.run_info.feed_frequency = '3m'

        self.context.run_info.start_date = '2017-09-01'
        self.context.run_info.end_date = '2017-09-28'
        self.context.run_info.ip = localip
        self.context.run_info.main_contract = True

        self.context.init_cash = 1000000

        self.context.boll = Boll()
        self.context.cash = 1000000  # 初始资金
        self.context.cash_rate = 0.3  # 资金利用率
        # self.context.future_info = ts.get_future_info(self.context.universe[0]) # 获取合约属性
        self.context.slippage = 0  # 开仓价 变化幅度 2 个变动单位

        self.context.direction = ''
        self.context.open_vol = 0  # 当前开仓手数
        self.context.open_flag = False  # false表示没有开仓 true表示已经开仓了
        self.context.can_open_flag = True  # true 表示能继续开仓 false 表示已经开足仓了
        self.context.close_count = 0  # 平仓计数器
        self.context.open_price = 0

        self.context.touch_flag = False




    # def order_change(self,order):
    #     print('时间:%s 报单变化 %s' % (datetime.now(), order))
    #     if order['status'] == 'AllTraded':
    #         if order['offset'] == '0':  # 开
    #             self.context.open_vol += order['vol']
    #         elif order['offset'] == '3':  # 平今
    #             self.context.open_vol -= order['vol']
    #
    #     print('时间:%s 当前开仓手数: %d ' % (datetime.now(), self.context.open_vol))
    #
    #     # 成交量> 0 开仓, 成交量 =0 未开仓
    #     if self.context.open_vol > 0:
    #         self.context.open_flag = True
    #     else:
    #         self.context.open_flag = False
    #         self.context.direction = ''

    def order_change(self,order):
        print('update unit %s:' % datetime.datetime.now(),5)
        # print(self.context.open_vol)
        # print(order['vol'])
        # self.context.last_price = data['limit_price']
        if order['offset'] == OPEN:  # 开
            self.context.open_vol += order['vol']
        elif order['offset'] == CLOSE_T:  # 平今
            self.context.open_vol -= order['vol']
            self.context.touch_flag = False

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
                    self.context.direction = SELL
                    print('change to sell')
                elif data.close < boll.dn and self.context.direction == '':
                    # print('时间:%s 突破下轨' % datetime.now())
                    self.context.direction = BUY
                    print('change to buy')

            # 突破上轨后跌破中轨kong单
            if data.close < boll.mb and self.context.direction == SELL and self.context.can_open_flag:
                self._open(data)

            # 突破下轨后涨破中轨开duo单
            if data.close > boll.mb and self.context.direction == BUY and self.context.can_open_flag:
                self._open(data)

            if data.close < boll.dn and self.context.direction == SELL and not self.context.touch_flag:
                self.context.touch_flag = True

            if data.close > boll.up and self.context.direction == BUY and not self.context.touch_flag:
                self.context.touch_flag = True

            # 开过多单后 收盘价超过中轨 平仓计数器 + 1 超过3次平仓
            if data.close > boll.mb and self.context.direction == SELL and self.context.open_flag and not self.context.touch_flag:
                self._close(data)

            # 开过空单后 收盘价跌破中轨 平仓计数器 + 1 超过3次平仓
            if data.close < boll.mb and self.context.direction == BUY and self.context.open_flag and not self.context.touch_flag:
                self._close(data)

            if data.close > boll.mb and self.context.direction == SELL and self.context.open_flag and self.context.touch_flag:
                self.context.close_count = 3
                self._close(data)

            if data.close < boll.mb and self.context.direction == BUY and self.context.open_flag and self.context.touch_flag:
                self.context.close_count = 3
                self._close(data)

            # if data.close < boll.dn and self.context.direction == BUY and self.context.open_flag:
            #     print('stoplosssssssssssssssss',self.context.open_price, data.close)
            #     self.context.close_count = 3
            #     self._close(data)
            #
            # if data.close > boll.up and self.context.direction == SELL and self.context.open_flag:
            #     print('stoplosssssssssssssssss',self.context.open_price, data.close)
            #     self.context.close_count = 3
            #     self._close(data)

    def _open(self, bar):
        # 开空
        open_price = bar.close - self.context.slippage
        if self.context.direction == BUY:
            # 开多
            open_price = bar.close + self.context.slippage

        self.context.open_price = open_price
        # 计算当前bar的close价下最多能开多少手
        # 开仓手数 = (总资金 * 资金利用率）/(开仓价 * 保证金比例 * 每手吨数）
        open_vol = int((self.context.cash * self.context.cash_rate )/ (open_price * self.context.instmt_info['broker_margin'] * 0.01 * self.context.instmt_info['contract_size']))
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


    def _close(self, bar):
        self.context.close_count += 1

        if self.context.close_count >= 3:
            # 平空
            open_price = bar.close + self.context.slippage
            direction = BUY
            if self.context.direction == BUY:
                # 平多
                open_price = bar.close - self.context.slippage
                direction = SELL

            if self.context.open_vol > 0:
                # print('时间:%s 平今:%s 手' % (datetime.now(), self.context.open_vol))
                print('时间:%d %s 平:%s 手' % (self.context.date, self.context.current_bar.end_time, self.context.open_vol))
                self.order(self.context.current_contract[0], direction, CLOSE_T, self.context.open_vol, limit_price=open_price)
                self.context.can_open_flag = True
                self.context.close_count = 0
            # else:
                # 平光了又能开仓了
                # self.context.can_open_flag = True
                # self.context.close_count = 0


if __name__ == '__main__':
    t = BollStrategyReverse()
    t.run()