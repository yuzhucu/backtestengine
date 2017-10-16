# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         mainEngine.py
time:         2017/8/30 下午2:02
description: 

'''

__author__ = 'Jimmy'

#
#
# class MainEngine(object):
#     def __init__(self, env):
#         self.__eventEngine = EventEngine()
#         self.__eventEngine.start()
#         # 全局环境
#         self.__env = env
#         self.__env.mainEngine = self.__eventEngine
#
#     def initStrategys(self, position):
#         modules = loadStrategys('strategys')
#         for strategy, exec_str in modules[0].items():
#             self.__env.strategy_name = strategy
#             self.__env.strategy_id = '000001'
#             exec(exec_str, globals()) # from strategys import xxx as xxx
#             context = Context()
#             eval(strategy).initialize(context)
#             context.run_info.name = strategy
#             self.__eventEngine.register(EVENT_ON_TICK, self._sendHandlerTickEvent)
#             self.__env.context = context
#
#     def login(self):
#         self.__md = MApi(self.__eventEngine)
#         self.__td = TApi(self.__eventEngine)
#         self.__td.login()
#         # 确认结算之后才能进行交易...
#         while 1:
#             if self.__env.settlementInfo_confirm_flag:
#                 self.__md.login()
#                 break
#
#     # tick事件处理转发给策略的handler
#     def _sendHandlerTickEvent(self,event):
#         eval(self.__env.strategy_name).handleData(self.__env.context, event.dict)
#
#
# if __name__ == '__main__':
#     config = {
#         'userID':'00305188',
#         'brokerID':'6000',
#         'password':'Jinmi123',
#         'marketFront':'tcp://180.168.146.187:10010',
#         'tradeFront':'tcp://101.231.162.58:41205'
#     }

    # config = {
    #     'userID': '008105',
    #     'brokerID': '9999',
    #     'password': '1',
    #     'marketFront': 'tcp://180.168.146.187:10010',
    #     'tradeFront': 'tcp://180.168.146.187:10000'
    # }
    # env = Environment(config)
    #
    # me = MainEngine(env)
    # me.initStrategys(1000000)
    #
    # me.login()

    # print(globals())





    # def initStrategys(self, positions):
    #     position_sum = np.sum(positions)
    #     if position_sum > 1 or position_sum <= 0:
    #         print('仓位分配错误')
    #     else:
    #         modules = loadStrategys('strategys')
    #
    #         modules_length = len(modules)
    #         positions_length = len(positions)
    #
    #         if modules_length != positions_length:
    #             print('仓位资金分配数量与策略数量不对等')
    #         else:
    #             for index in range(0, modules_length):
    #                 for strategy, exec_str in modules[index].items():
    #                     self.__env.strategy = strategy
    #
    #                     exec(exec_str, globals())
    #
    #                     context = Context()
    #                     eval(strategy).initialize(context)
    #
    #                     self.__eventEngine.register(EVENT_ONTICK, eval(strategy).handleData)
    #
    #                     self.__env.context = context