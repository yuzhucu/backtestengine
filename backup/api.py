#
# # -*- coding: utf-8 -*-
#
# '''
# author:       Jimmy
# contact:      234390130@qq.com
# file:         objects.py
# time:         2017/8/30 下午2:44
# description:  策略可直接调用的接口
#
# '''
#
# import datetime
#
# from ctp.api import *
# from engine.eventType import *
#
#
# # 市价order
# def anyBuy(symbol, vol):  # 买开多开
#     direction = DirectionType.Buy
#     offset = OffsetFlagType.Open.__char__()
#     _sendOrder(symbol,vol,0,direction,offset)
#
#
# def anySell(symbol, vol):  # 多平
#     direction = DirectionType.Sell
#     offset = OffsetFlagType.Close.__char__()
#     _sendOrder(symbol,vol,0,direction,offset)
#
#
# def anySellToday(symbol, vol):  # 平今多
#     direction = DirectionType.Sell
#     offset = OffsetFlagType.CloseToday.__char__()
#     _sendOrder(symbol,vol,0,direction,offset)
#
#
# def anyShort(symbol, vol):  # 卖开空开
#     direction = DirectionType.Sell
#     offset = OffsetFlagType.Open.__char__()
#     _sendOrder(symbol,vol,0,direction,offset)
#
#
# def anyCover(symbol, vol):  # 空平
#     direction = DirectionType.Buy
#     offset = OffsetFlagType.Close.__char__()
#     _sendOrder(symbol,vol,0,direction,offset)
#
#
# def anyCoverToday(symbol, vol):  # 平今空
#     direction = DirectionType.Buy
#     offset = OffsetFlagType.CloseToday.__char__()
#     _sendOrder(symbol,vol,0,direction,offset)
#
# # 限价order
# def limitBuy(symbol, price, vol):  # 买开多开
#     direction = DirectionType.Buy
#     offset = OffsetFlagType.Open.__char__()
#     _sendOrder(symbol,vol,price,direction,offset)
#
# def limitSell(symbol, price, vol):  # 多平
#     direction = DirectionType.Sell
#     offset = OffsetFlagType.Close.__char__()
#     _sendOrder(symbol,vol,price,direction,offset)
#
# def limitSellToday(symbol, price, vol):  # 平今多
#     direction = DirectionType.Sell
#     offset = OffsetFlagType.CloseToday.__char__()
#     _sendOrder(symbol,vol,price,direction,offset)
#
# def limitShort(symbol, price, vol):  # 卖开空开
#     direction = DirectionType.Sell
#     offset = OffsetFlagType.Open.__char__()
#     _sendOrder(symbol,vol,price,direction,offset)
#
# def limitCover(symbol, price, vol):  # 空平
#     direction = DirectionType.Buy
#     offset = OffsetFlagType.Close.__char__()
#     _sendOrder(symbol,vol,price,direction,offset)
#
# def limitCoverToday(symbol, price, vol):  # 平今空
#     direction = DirectionType.Buy
#     offset = OffsetFlagType.CloseToday.__char__()
#     _sendOrder(symbol,vol,price,direction,offset)
#
# # 发送下单事件
# def _sendOrder(symbol,vol,price,direction,offset):
#     event = Event(EVENT_ORDER)
#     env = Environment.getInstance()
#     date = str(datetime.datetime.now()).split(' ')
#     # 加入了策略名称 id 报单日期 时间
#     event.dict = {
#         'symbol': symbol,
#         'vol': vol,
#         'price': price,
#         'direction': direction,
#         'offset': offset,
#         'strategy_name':env.strategy_name,
#         'strategy_id':env.strategy_id,
#         'send_date':date[0],
#         'send_time':date[-1]
#     }
#     event.sync_flag = False
#     env.mainEngine.sendEvent(event)
#
# # 撤单 order
# def cancelOrder(order):
#     event = Event(EVENT_CANCEL)
#     event.dict = order
#     event.sync_flag = False
#     Environment.getInstance().mainEngine.sendEvent(event)
#
#
# # direction = str(DirectionType.Buy).split('.')[-1]
# # print(direction)