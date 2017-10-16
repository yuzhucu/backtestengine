# -*- coding: utf-8 -*-

'''
author:       Jimmy & sjsj
contact:      234390130@qq.com
file:         mainEngine.py
time:         2017/9/7 上午午9:02
description:

'''

from engine.eventEngine import *
from engine.eventType import *
from backtest.context import *
from backtest.data.getdata import *
from backtest.position import *
from backtest.portfolio import *
from utils.objects import *
from datetime import datetime

from backtest.tools.tools import *


class Strategy(object):
    def __init__(self):
        self._engine = EventEngine()
        self._engine.register(EVENT_ON_TICK, self._handle_data)  # 处理tick事件
        # self._engine.register(EVENT_ON_TICK, self._check_unfilled_orders)  # 检查挂单
        self._engine.register(EVENT_ORDER, self._execute)  # 执行order事件
        self._engine.register(EVENT_FILL, self._fill)  # 更新账户持仓...
        self._engine.register(EVENT_NEXT_TICK, self._next_tick)

        # context里保存所有需要的信息
        self.context = Context()
        self.portfolio = Portfolio(self.context.init_cash)

    def initialize(self):
        print('you must initilize account')
        raise NotImplementedError


    def handle_data(self, data):
        print('you must write a strategy')
        raise NotImplementedError

    def order(self, instrument_id, direction, offset, vol, limit_price=0, stop_price=0, contingent_condition='immediately'):

        '''
        下单
        :param instrument_id:           合约id: 如'rb1801'
        :param direction:               DirectionType.买:Buy  卖:Sell
        :param offset:                  OffsetFlagType.开:Open.__char__() 平:Close.__char__() 平今:CloseToday.__char__() 平昨:CloseYesterday__char__()
        :param vol:                     数量
        :param limit_price:             限价为0则为市价单 不为0则为限价单
        :param stop_price:              止损价为0则挂单条件为立即触发
        :param contingent_condition:    触发条件 默认立即 可设置stop条件
        :return:
        '''

        price_type = 'limit'
        if limit_price == 0:
            price_type = 'any'

        event = Event(EVENT_ORDER)

        # 加入了策略名称 id 报单日期 时间 用户名 broker名
        event.dict = {
            # 'tick':self.context.current_tick,
            'symbol': instrument_id,
            'vol': vol,
            'limit_price': limit_price,
            'pricetype': price_type,
            'direction': direction,
            'offset': offset,
            'stop_price': stop_price,
            'contingent_condition': contingent_condition,
            # 'order_time': ordertime,
            'strategy_name': self.context.run_info.name,
            'strategy_id': self.context.run_info.run_id,
            'cancel_flag': False
        }
        # print(event.dict)
        self._engine.sendEvent(event)

    def cancel_order(self, order):
        order = Order()
        order.cancel_flag = True

        # 发送执行order事件
        event = Event(EVENT_FILL)
        event.dict = order
        self._engine.sendEvent(event)

    def run(self):
        self._engine.start()
        timestart = datetime.datetime.now()
        self.initialize()
        date_start_int = datestrtoint(self.context.run_info.start_date)
        date_end_int = datestrtoint(self.context.run_info.end_date)
        datelist = GetTradeDates().get_date_list(date_start_int, date_end_int)
        # print(datelist)
        trade_days = len(datelist)
        print('交易日共 %d 天' % trade_days)
        for date in datelist:
            if self.context.feed_frequency == 'tick':
                data_ticks = self.__get_ticks_dict(date, self.context.universe) ## ticks dict
                tick = {}
                for symbol in self.context.universe:
                    tick[symbol] = data_ticks[symbol].next()

                event = Event(EVENT_ON_TICK)
                event.dict = tick

            # date = self.context.run_info.start_date + day  # 遍历所有交易日
            for symbol in self.context.universe:
                # print(symbol)
                ticks = self.__get_tick(date, symbol)
                # print(ticks)
                for row in ticks:
                    # print(row)
                    # 发送tick事件
                    # if self._engine.emptyqueue():
                        bar = Bar(op = row.Open, cl=row.Close, high=row.High, low= row.Low)
                        event = Event(EVENT_ON_TICK)
                        event.dict = bar
                        # print(event.dict)
                        self._engine.sendEvent(event)
                        # sleep(0.5)

        timeend = datetime.datetime.now()
        timespend = timeend - timestart
        print('回测共耗时%s' % timespend)

        self._engine.stop()



    def stop(self):
        self._engine.stop()

    # 获取tick
    def __get_tick(self, date, symbol):
        if self.context.datasource == 'mongo':
            tick = GetDataMongo(symbol=symbol, date=date).get_tick_data()  # 数据库取某天的tick
        elif self.context.datasource == 'csv':
            tick = GetDataCSV(symbol+'-'+date+'.csv').get_tick()
        return tick

    def __get_ticks_dict(self,date,symbols):
        ticks = {}
        for symbol in symbols:
            ticks[symbol] = self.__get_tick(date,symbol)
        return ticks

    def __get_sup_dict(self,symbols):
        sups = {}
        for symbol in symbols:
            sups[symbol] = GetSupData(symbol).get_sup_data()
        return sups


    # private
    def _handle_data(self, event):
        # 保存当前tick
        self.context.current_tick = event.dict
        self.handle_data(event.dict)
        self.portfolio.update_portfolio_tick(event.dict)
        # if self.portfolio.positions.get('rb1801') == None:
        #     pass
        # else:
        #     print(self.portfolio.positions.get('rb1801').vol)
        # print(self.portfolio.equity)

    # 检查挂单
    # def _check_unfilled_orders(self, event):
    #     tick = event.dict
    #     unfilled_orders = self.context.unfilled_orders
    #     for order in unfilled_orders:
    #         # 如果订单有滑点
    #         if order.slippage_flag :
    #             # if 滑点计数器 == 滑点tick数 发送成交事件 更新账户持仓...
    #             if order.slippage_count == order.slippage_tick:
    #                 # 进行成交
    #                 order.order_status = 1
    #                 _event = Event(EVENT_PORTFOLIO)
    #                 _event.dict = order
    #                 self._engine.sendEvent(_event)
    #             else:
    #                 # 不成交滑点计数器+1
    #                 order.slippage_count += 1
    #         else:
    #             # 如果没有滑点且当前tick的最新价 == 订单价 则成交 否则不处理 等待下一个tick事件轮回
    #             if tick.lastprice == order.price:
    #                 # 进行成交
    #                 order.order_status = 1
    #                 _event = Event(EVENT_PORTFOLIO)
    #                 _event.dict = order
    #                 self._engine.sendEvent(_event)

    # 执行
    def _execute(self, event):
        # 事件传递过来的下单
        order = event.dict
        # print(order['symbol']+order['direction']+order['offset'])
        # # 如果是撤单 就从挂单中删除
        # if order.cancel_flag:
        #     order.order_status = -1
        #     self.context.unfilled_orders.remove(order)
        # # 否则开始计算滑点
        # else:
        #     slippage_tick = self._generate_slippage()
        #     # 如果不需要滑点 并且当前tick最新价与订单价相同 直接发送成交事件 更新账户持仓...
        #     if slippage_tick == 0 and self.context.current_tick.lastprice == order.price:
        #         order.order_status = 1
        #     else:
        #         # 否则生产一个的订单 并添加到未成交挂单中 (有可能带滑点)
        #         if slippage_tick != 0:
        #             order.slippage_flag = True
        #             order.slippage_tick = slippage_tick
        #         self.context.unfilled_orders.append(order)

        _event = Event(EVENT_FILL)
        _event.dict = order
        self._engine.sendEvent(_event)

    def _fill(self, event):
        pass

    def _next_tick(self, event):
        pass

    # 更新持仓。。。
    def _portfolio(self, event):
        order = event.dict
        # print('下单')
        # if order.order_status == 0:
        #     # 未成交
        #     print('订单未成交')
        # elif order.order_status == 1:
        #     # 成交
        #     print('orderorder')
        self.portfolio.modify_position(symbol=order['symbol'], direction=order['direction'], offset=order['offset'],
                                       vol=order['vol'], price=order['limit_price'], marginratio=0.15)
        # else:
        #     # 撤单
        #     pass


    # 生成滑点
    def _generate_slippage(self):
        slippage_tick = 2 # 随机生产滑点所需tick
        return slippage_tick


# symbol = 'rb1801'
# date = [20170601, 20170602]
#
# for i in date:
#     ticks = GetDataMongo(symbol=symbol, date=i).get_tick()
#     print(ticks)
#     # for row in ticks:
#     #     print(row)