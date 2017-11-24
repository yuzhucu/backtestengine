# encoding: utf-8


"""
@version: python3.6
@author: ‘sj‘
@contact: songjie1217@hotmail.com
@file: boll.py
@time: 10/24/17 5:23 PM
"""
from backtest.core.backteststrategy import *
from backtest.optimizer.optimizer import *
from backtest.tools.ta import *
from datetime import datetime as dt

class BollStrategy(BacktestStrategy):
    def initialize(self):
        self.context.universe = ['SR801']
        self.context.run_info.strategy_name = 'boll15m-sr-main-stoploss'
        self.context.run_info.feed_frequency = '15m'

        self.context.run_info.start_date = '2017-01-10'
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

    def order_change(self, order):
        print('update unit %s:' % datetime.datetime.now(),5)
        print(self.context.open_vol)
        print(order['vol'])
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
        # print(data.__dict__)
        boll = self.context.boll.compute(data)

        # print('时间:%s 收到bar数据：bar: %s ; boll: %s' % (datetime.now(), data, boll))

        # 下单前先撤销所有未成交的单
        # for k, v in self.context.orders.items():
        #     self.cancel_order(v)

        # 如果没有开过仓

        # print('openflag:%s,direction:%s,canflag:%s,openvol:%d,date:%d,time:%s'
        #       %(self.context.open_flag,self.context.direction,self.context.can_open_flag,self.context.open_vol,self.context.date,self.context.current_bar.end_time))

        # print('before trade: curprice:%d,total:%d, marginreq:%d, avalcash:%d,upnl:%d,daypnl:%d,daycomm:%d,prebalance:%d' % (self.context.current_bar.close,
        # self.context.portfolio.total_value, self.context.portfolio.marginreq, self.context.portfolio.avail_cash, self.context.portfolio.upnl,
        #                                                                                                       self.context.portfolio.dailypnl,
        #                                                                                                       self.context.portfolio.dailycomm,
        #                                                                                                       self.context.portfolio.pre_balance))
        if boll is not None:
            print('date%d,time:%s, barclose:%d,up:%d,dn:.%d,mb:%d'%(self.context.date,self.context.current_bar.end_time,data.close,boll.up,boll.dn,boll.mb))
            print(self.context.open_flag)
            print(self.context.can_open_flag)
            if not self.context.open_flag:
                if data.close > boll.up and self.context.direction == '':
                    # print('时间:%s 突破上轨' % datetime.now())
                    self.context.direction = SELL
                    print('change to sell')
                elif data.close < boll.dn and self.context.direction == '':
                    # print('时间:%s 突破下轨' % datetime.now())
                    self.context.direction = BUY
                    print('change to buy')

            # 突破上轨后跌破中轨开空单
            if data.close < boll.mb and self.context.direction == SELL and self.context.can_open_flag:
                self._open(data)

            # 突破下轨后涨破中轨开多单
            if data.close > boll.mb and self.context.direction == BUY and self.context.can_open_flag:
                self._open(data)

            # 开过空单后 收盘价超过中轨 平仓计数器 + 1 超过3次平仓
            if data.close > boll.mb and self.context.direction == SELL and self.context.open_flag:
                self._close(data)

            # 开过多单后 收盘价跌破中轨 平仓计数器 + 1 超过3次平仓
            if data.close < boll.mb and self.context.direction == BUY and self.context.open_flag:
                self._close(data)

            if data.close < (self.context.open_price - 15 * self.context.instmt_info['tick_size']) and self.context.direction == BUY and self.context.open_flag:
                print('多单止损', self.context.open_price, data.close)
                self.context.close_count = 3
                self._close(data)

            if data.close > (self.context.open_price + 15 * self.context.instmt_info['tick_size']) and self.context.direction == SELL and self.context.open_flag:
                print('空单止损', self.context.open_price, data.close)
                self.context.close_count = 3
                self._close(data)

    def _open(self, bar):
        # 开空
        open_price = bar.close - self.context.slippage
        if self.context.direction == BUY:
            # 开多
            open_price = bar.close + self.context.slippage

        # 计算当前bar的close价下最多能开多少手
        # 开仓手数 = (总资金 * 资金利用率）/(开仓价 * 保证金比例 * 每手吨数）
        open_vol = int((self.context.portfolio.avail_cash * self.context.cash_rate) / (open_price * self.context.instmt_info['broker_margin'] * 0.01 * self.context.instmt_info['contract_size']))
        # 部分成交情况下 满足布林开仓条件继续开仓
        available_open_vol = open_vol - self.context.open_vol

        if available_open_vol > 0:
            # print('时间:%s 开:%s 手' % (datetime.now(), available_open_vol))
            print('时间:%d %s 开:%s手' % (self.context.date, self.context.current_bar.end_time, available_open_vol))
            self.order(self.context.current_contract[0], self.context.direction, OPEN, available_open_vol, limit_price= open_price)
            print('开单成功')
            self.context.can_open_flag = False
            self.context.open_price = open_price
        # else:
        #     # 开足仓位
        #     self.context.can_open_flag = False


    def _close(self, bar):
        self.context.close_count += 1
        print('close count', self.context.close_count)

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
                print(self.context.open_vol)
                print('时间:%d %s 平:%s 手' % (self.context.date, self.context.current_bar.end_time, self.context.open_vol))
                self.order(self.context.current_contract[0], direction, CLOSE, self.context.open_vol, limit_price=open_price)
                self.context.can_open_flag = True
                self.context.open_flag = False
                self.context.close_count = 0
            # else:
                # 平光了又能开仓了
                # self.context.can_open_flag = True
                # self.context.close_count = 0


if __name__ == '__main__':
    t = BollStrategy()
    t.run()