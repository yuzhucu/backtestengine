# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         tradeStrategy.py
time:         2017/9/7 下午1:47
description: 

'''

__author__ = 'Jimmy'


from ctp.api import *
from datetime import datetime
from utils.objects import *
from utils.environment import *
from trade.tradeType import *


class TradeStrategy(object):
    def __init__(self):
        Environment.engine = self
        self.context = Context()

    def initialize(self):
        raise NotImplementedError


    def handle_data(self, data):
        raise NotImplementedError


    def order(self, instrument_id, direction, offset, vol, limit_price = 0, stop_price=0, contingent_condition = ContingentConditionType.Immediately):
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
        price_type = OrderPriceTypeType.LimitPrice
        if limit_price == 0:
            price_type = OrderPriceTypeType.AnyPrice

        event = Event(EVENT_ORDER)

        # 加入了策略名称 id 报单日期 时间 用户名 broker名
        event.dict = {
            'symbol': instrument_id,
            'vol': vol,
            'limit_price': limit_price,
            'direction': direction,
            'offset': offset,
            'price_type':price_type,
            'stop_price':stop_price,
            'contingent_condition':contingent_condition,
            'strategy_name': self.context.run_info.name,
            'strategy_id': self.context.run_info.run_id,
            'user_id':self.context.user_id,
            'broker_id':self.context.broker_id
        }
        print(event.dict)

        event.sync_flag = False
        self._engine.sendEvent(event)

    def cancel_order(self, order):
        event = Event(EVENT_CANCEL)
        event.dict = order
        event.sync_flag = False
        self._engine.sendEvent(event)

    def run(self):
        self._login()

    def stop(self):
        self._engine.stop()

    # private
    def _login(self):
        # 初始化 context参数
        self.initialize()

        # 默认 stop_times = ['15:20', '23:50'] start_time = ['08:20': '20:20']
        self._engine = EventEngine(self.context.run_info.stop_times)
        self._engine.start()

        self._engine.register(EVENT_ON_TICK, self._handle_data)  # 处理tick事件
        self._md = MApi(self._engine, self.context)
        self._td = TApi(self._engine, self.context)
        self._td.login()
        # 确认结算之后才能进行交易...
        while 1:
            if self.context.settlementInfo_confirm_flag:
                self._md.login()
                break

    def _handle_data(self, event):
        # 保存当前tick
        self.handle_data(event.dict)
