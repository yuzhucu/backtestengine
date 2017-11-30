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
        self.stop_type = 'immediately'
        self.status = 0
        self.slippage = 0
        self.type = ''



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
    def __init__(self, symbol, direction, offset, vol, deal_price, commission, transtime, date, pnl, type = '', max_dev = 0,diff = 0):
        self.symbol = symbol
        self.date = date
        self.time = transtime
        self.direction = direction
        self.offset = offset
        self.price = deal_price
        self.vol = vol
        self.commission = commission
        self.pnl = pnl
        self.type = type
        self.max_dev = max_dev
        self.diff = diff

class DailySummary(object):
    def __init__(self):
        self.date = ''
        self.balance = 0
        self.equity = 0
        self.cash = 0
        self.marginreq = 0
        self.daily_comm = 0
        self.positions = []
        self.upnl = 0
        self.pnl = 0
        self.riskratio = 0


