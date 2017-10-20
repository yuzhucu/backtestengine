# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         processEventEngine.py
time:         2017/8/25 上午10:06
description:  多线程异步事件驱动引擎

'''

__author__ = 'Jimmy'


from threading import Thread
from queue import Queue
from time import sleep

from backtest.tools.tools import *
from backtest.eventengine.eventType import *





class EventEngine(object):
    # 初始化事件事件驱动引擎
    # 默认 stop_times = ['15:20', '23:50']
    def __init__(self, stop_times=''):
        #保存事件列表
        self.__eventQueue = Queue()
        #引擎开关
        self.__active = False
        #事件处理字典{'event1': [handler1,handler2] , 'event2':[handler3, ...,handler4]}
        self.__handlers = {}
        #保存事件处理线程池
        self.__threadPool = []
        #事件引擎主进程
        self.__mainThread = Thread(target=self.__run)
        # 停止时间
        self.__stoptimes = convert_time(stop_times)

        # 计时器，用于触发计时器事件
        self.__timer = Thread(target=self.__runTimer)
        self.__timerActive = False  # 计时器工作状态
        self.__timerSleep = 1  # 计时器触发间隔（默认1秒)
        self.__switchFlag = 0
        self.__switchHandlers = []


    def emptyqueue(self):
        return self.__eventQueue.empty()

    #执行事件循环
    def __run(self):
        if len(self.__stoptimes) != 2:
            while self.__active:
                # 事件队列非空
                # print(self.__handlers)
                if not self.__eventQueue.empty():
                    # 获取队列中的事件 超时1秒
                    event = self.__eventQueue.get(block=True, timeout=1)
                    # 执行事件
                    self.__process(event)
                else:
                    # print('无任何事件')
                    pass
        else:
            while self.__active and calculate_stop(self.__stoptimes):
                # 事件队列非空
                # print(self.__handlers)
                if not self.__eventQueue.empty():
                    # 获取队列中的事件 超时1秒
                    event = self.__eventQueue.get(block=True, timeout=1)
                    # 执行事件
                    self.__process(event)
                else:
                    # print('无任何事件')
                    pass


    #执行事件
    def __process(self, event):
        if event.type in self.__handlers:
            for handler in self.__handlers[event.type]:
                if event.sync_flag:
                    handler(event)
                else:
                    #   开一个进程去异步处理
                    p = Thread(target=handler, args=(event, ))
                    #保存到进程池
                    self.__threadPool.append(p)
                    p.start()


    #开启事件引擎
    def start(self, timer = True):
        self.__active = True
        self.__mainThread.start()
        # 启动计时器，计时器事件间隔默认设定为1秒
        if timer:
            self.__timerActive = True
            self.__timer.start()


    #暂停事件引擎
    def stop(self):
        # 将事件管理器设为停止
        self.__active = False
        # # 等待事件处理进程退出
        self.__timerActive = False
        self.__timer.join()

        for p in self.__threadPool:
            p.join()
        self.__mainThread.join()

    #注册事件
    def register(self, type, handler):
        """注册事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无则创建
        try:
            handlerList = self.__handlers[type]
        except KeyError:
            handlerList = []
            self.__handlers[type] = handlerList

        # 若要注册的处理器不在该事件的处理器列表中，则注册该事件
        if handler not in handlerList:
            handlerList.append(handler)


    def unregister(self, type, handler):
        """注销事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无则忽略该次注销请求
        try:
            handlerList = self.__handlers[type]

            # 如果该函数存在于列表中，则移除
            if handler in handlerList:
                handlerList.remove(handler)

            # 如果函数列表为空，则从引擎中移除该事件类型
            if not handlerList:
                del self.__handlers[type]
        except KeyError:
            pass


    def sendEvent(self, event):
        #发送事件 像队列里存入事件
        self.__eventQueue.put(event)


    def __runTimer(self):
        """运行在计时器线程中的循环函数"""
        while self.__timerActive:

            if len(self.__switchHandlers) == 2:
                if self.__switchFlag == 0:
                    self.unregister(EVENT_TIMER, self.__switchHandlers[1])
                    self.register(EVENT_TIMER, self.__switchHandlers[0])
                    self.__switchFlag = 1
                else:
                    self.unregister(EVENT_TIMER, self.__switchHandlers[0])
                    self.register(EVENT_TIMER, self.__switchHandlers[1])
                    self.__switchFlag = 0

            # 创建计时器事件
            event = Event(type=EVENT_TIMER)
            # 向队列中存入计时器事件
            self.sendEvent(event)
            # 等待
            sleep(self.__timerSleep)


    def registerSwicthHandlers(self, handlers):
        self.__switchHandlers = handlers


class Event(object):
    #事件对象
    def __init__(self, type =None):
        self.type = type
        self.dict = {}
        self.sync_flag = True #是否同步




