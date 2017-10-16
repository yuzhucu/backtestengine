# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         multiStrategy.py
time:         2017/9/8 下午1:42
description: 

'''

__author__ = 'Jimmy'

class MultiStrategyEngine(object):
    def __init__(self):
        self.strategys = []
        self.subscribes = {}

        # {
        #     'rb1801':[strategy1.handle_data, strategy2.handle_data],
        #     'm1801':[strategy3.handle_data]
        # }

    def run(self):
        pass

    def stop(self):
        pass

    # 转发tick
    def handle_data(self, data):
        if data.InstrumentID in self.subscribes:
            for handler in self.subscribes[data.InstrumentID]:
                handler(data)


    def stop_strategy(self, strategys):
        for strategy in strategys:
            self.strategys.remove(strategy)
            for symbol in strategys.context.universe:
                self._unregister_handle_data(symbol, strategy.handle_data)

    def start_strategy(self, strategys):
        for strategy in strategys:
            self.strategys.append(strategy)
            for symbol in strategys.context.universe:
                self._register_handle_data(symbol, strategy.handle_data)


    # private
    def _register_handle_data(self, symbol, handler):
        try:
            handlerList = self.subscribes[symbol]
        except KeyError:
            handlerList = []
            self.subscribes[symbol] = handlerList
        # 若要注册的处理器不在该事件的处理器列表中，则注册该事件
        if handler not in handlerList:
            handlerList.append(handler)

    def _unregister_handle_data(self, symbol, handler):
        """注销事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无则忽略该次注销请求
        try:
            handlerList = self.subscribes[symbol]
            # 如果该函数存在于列表中，则移除
            if handler in handlerList:
                handlerList.remove(handler)
            # 如果函数列表为空，则移除该订阅
            if not handlerList:
                del self.subscribes[symbol]
        except KeyError:
            pass