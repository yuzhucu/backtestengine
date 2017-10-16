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
        self.direction = ''
        self.offset = ''
        self.price = ''
        self.vol = 0
        self.commission = 0
        self.pnl = 0




