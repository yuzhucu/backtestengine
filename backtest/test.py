# -*- coding: utf-8 -*-

'''
author:       sjsj
contact:      songjie1217@hotmail.com   
file:         test.py
time:         2017/9/8 14:33
description: 

'''
from backtest.tools.tools import *
from engine.eventType import *
from engine.eventEngine import *
from backtest.position import *
# from backtest.portfolio import *

__author__ = 'sjsj'

# EventType = Enum("EventType", "TICK BAR SIGNAL ORDER FILL SENTIMENT")
#
#
# class Event(object):
#     """
#     Event is base class providing an interface for all subsequent
#     (inherited) events, that will trigger further events in the
#     trading infrastructure.
#     """
#     @property
#     def typename(self):
#         return self.type.name
#
#
# class TickEvent(Event):
#     """
#     Handles the event of receiving a new market update tick,
#     which is defined as a ticker symbol and associated best
#     bid and ask from the top of the order book.
#     """
#     def __init__(self, ticker, time, bid, ask):
#         """
#         Initialises the TickEvent.
#
#         Parameters:
#         ticker - The ticker symbol, e.g. 'GOOG'.
#         time - The timestamp of the tick
#         bid - The best bid price at the time of the tick.
#         ask - The best ask price at the time of the tick.
#         """
#         self.type = EventType.TICK
#         self.ticker = ticker
#         self.time = time
#         self.bid = bid
#         self.ask = ask
#
#     def __str__(self):
#         return "Type: %s, Ticker: %s, Time: %s, Bid: %s, Ask: %s" % (
#             str(self.type), str(self.ticker),
#             str(self.time), str(self.bid), str(self.ask)
#         )
#
#     def __repr__(self):
#         return str(self)

# end_date = '2017-05-11'
# start_date = '2017-05-05'
#
# trade_days = (strtodate(end_date) - strtodate(start_date)).days
#
# print(trade_days)


# aaa = 'aaa.event'
# a = Event(aaa)
#
# print(a.type)

# positions = {}
# s = 'aaa'
# positions[s] = Position('aaa','buy','close',30,20,0.01)
#
# print(positions[s].marginvalue)


for i in range(1,2):
    print(i)