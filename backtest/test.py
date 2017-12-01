# -*- coding: utf-8 -*-

'''
author:       sjsj
contact:      songjie1217@hotmail.com   
file:         test.py
time:         2017/9/8 14:33
description: 

'''
# from backtest.tools.tools import *
# from engine.eventType import *
# from engine.eventEngine import *
# # from backtest.portfolio import *

__author__ = 'sjsj'


def __reverse_direction(direction):
    if direction == 'long':
        temp_d = 'short'
    else:
        temp_d = 'long'
    return temp_d


print(__reverse_direction('long'))
print(__reverse_direction('short'))