# encoding: utf-8


"""
@version: python3.6
@author: ‘sj‘
@contact: songjie1217@hotmail.com
@file: order.py
@time: 9/25/17 9:37 PM
"""

from queue import Queue


class Order(object):
    def __init__(self):
        self.symbol = ''
        self.direction = ''
        self.offset = ''
        self.vol = 0
        self.limit_price = 0
        self.stop_price = 0
        self.stop_type = ''
        self.status = 0
        self.slippage = 0


class Transaction(object):
    def __init__(self):
        self.symbol = ''
        self.date = ''
        self.time = ''
        self.direction = ''
        self.offset = ''
        self.price = ''
        self.vol = 0
        self.commission = 0
        self.pnl = 0

class TransactionRecord(object):
    def __init__(self, symbol, direction, offset, vol, deal_price, commission, transtime, avg_cost=0):
        self.symbol = symbol
        self.direction = direction
        self.offset = offset
        self.vol = vol
        self.deal_price = deal_price
        self.commission = commission
        self.transtime = transtime
        self.pnl = 0


