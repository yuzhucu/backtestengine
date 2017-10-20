# encoding: utf-8


"""
@version: python3.6
@author: ‘sj‘
@contact: songjie1217@hotmail.com
@file: riskmanagement.py
@time: 9/28/17 11:00 AM
"""

from backtest.context import *

class Risk(object):
    def __init__(self):
        self.a = 1
        self.v = 2
        self.context = Context()

    def init(self):
        pass

    def run(self):
        self.init()
        print(self.context.init_cash)



class Oner(Risk):
    def init(self):
        self.context.init_cash = 1



r = Oner()

r.run()