# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         tools.py
time:         2017/9/7 下午5:16
description: 

'''

__author__ = 'Jimmy'
from datetime import datetime


def convert_time(stoptimes):
    if len(stoptimes) != 2:
        return []
    else:
        st_day = int(stoptimes[0].split(':')[0]) * 60 + int(stoptimes[0].split(':')[-1])
        st_night = int(stoptimes[-1].split(':')[0]) * 60 + int(stoptimes[-1].split(':')[-1])
        return [st_day, st_night]

def calculate_stop(stoptimes):
    flag = False
    now = datetime.now()
    time_now = now.hour * 60 + now.minute

    st_day = stoptimes[0]
    st_night = stoptimes[-1]

    if st_day < st_night:
        if 500 <= time_now and time_now <= st_day:
            flag = True
        elif 1220 <= time_now and time_now <= st_night:
            flag = True
    else:
        if 500 <= time_now and time_now <= st_day:
            flag = True
        elif 1220 <= time_now and time_now <= 1439:  # 20:30 ~ 23:59
            flag = True
        elif 0 <= time_now and time_now <= st_night:  # 00:00 ~
            flag = True
    return flag


def getTime():
    date = str(datetime.now()).split(' ')
    t = date[-1].split('.')
    return [date[0], t[0], t[-1]]


if __name__ == '__main__':
    import time
    # begin = datetime.now()
    stoptimes = ['15:20', '23:50']
    stoptimes = convert_time(stoptimes)
    print(stoptimes)
    flag = calculate_stop(stoptimes)
    print(flag)
    # end = datetime.now()
    # t = end - begin
    # print(t)