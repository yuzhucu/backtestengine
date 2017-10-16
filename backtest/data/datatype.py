# encoding: utf-8


"""
@version: python3.6
@author: ‘sj‘
@contact: songjie1217@hotmail.com
@file: datatype.py
@time: 9/28/17 6:33 PM
"""

class Bar(object):
    def __init__(self,h,l,o,c,v,cv):
        self.high = h
        self.low = l
        self.open = o
        self.close = c
        self.vol = v
        self.curvol = cv

