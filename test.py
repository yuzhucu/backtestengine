# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         test.py
time:         2017/9/9 10:36
description:  

'''

__author__ = 'Jimmy'


from datetime import datetime

# date = str(datetime.now()).split(' ')
# print(date[0])
# print(date[1])


# print(date.second)
# print(date.microsecond)



def getTime():
    date = str(datetime.now()).split(' ')
    t = date[-1].split('.')
    return [date[0], t[0], t[-1]]


t = getTime()
print(t)

