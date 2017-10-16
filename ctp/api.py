# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         api.py
time:         2017/8/28 下午2:03
description: 

'''

__author__ = 'Jimmy'


from ctp.ctp_struct import *
from ctp.quote import Quote
from ctp.trade import Trade
from engine.eventEngine import *
from engine.eventType import *
from utils.storage import *
from copy import deepcopy
from utils.objects import *
from datetime import datetime
import threading
from utils.environment import *
from handlers.sender import *
import numpy as np

class MApi:
    '''
    行情API的封装后所有数据自动推送到事件驱动引擎中，由其负责推送到各个监听该事件的回调函数上
    '''
    def __init__(self, eventEngine, context):
        self._eventEngine = eventEngine
        self._context = context

        self._ticks = []
        self._bar_length = self._get_bar_length(context.run_info.frequency)

        # Quote继承CTP的CThostFtdcMdApi
        self._quote = Quote()
        # 请求编号
        self._reqid = 0
        # 默认用户名密码
        self._userid = self._context.user_id
        self._password = self._context.password
        self._brokerid = self._context.broker_id

        #注册事件
        self._eventEngine.register(EVENT_ON_TICK, ws_on_tick)                           # 收到tick
        self._eventEngine.register(EVENT_ON_MARKET_CONNECTED, ws_market_connected)      # 行情服务连接上
        self._eventEngine.register(EVENT_ON_MARKET_LOGIN, ws_market_login)              # 行情服务登录


    def login(self):
        userMApi = self._quote.CreateApi()
        userSApi = self._quote.CreateSpi()
        self._quote.RegisterSpi(userSApi)
        # 连接行情服务器回调
        self._quote.OnFrontConnected = self.onFrontConnected
        self._quote.OnFrontDisconnected = self.onFrontDisconnected
        # 登录回调
        self._quote.OnRspUserLogin = self.onRspUserLogin
        # 订阅行情
        self._quote.OnRspSubMarketData = self.OnRspSubMarketData
        # 订阅数据
        self._quote.OnRtnDepthMarketData = self.onRtnDepthMarketData

        self._quote.RegCB()
        self._quote.RegisterFront(self._context.market_front)
        self._quote.Init()


    def onFrontConnected(self):
        print('行情服务器连接成功')

        event = Event(EVENT_ON_MARKET_CONNECTED)
        event.dict = {'log':'行情服务器连接成功'}
        event.sync_flag = False
        self._eventEngine.sendEvent(event)

        # 登录
        self._quote.ReqUserLogin(BrokerID=self._brokerid, UserID=self._userid,)


    def onFrontDisconnected(self, nReason):
        print('行情服务器连接失败, 原因：%d' % nReason)


    def onRspUserLogin(self, loginField, rspInfo, reqid, isLast):
        if rspInfo.ErrorID == 0:
            print('行情服务器登录成功')

            event = Event(EVENT_ON_MARKET_LOGIN)
            event.dict = {'log':'行情服务器登录成功'}
            event.sync_flag = False
            self._eventEngine.sendEvent(event)

            universe = self._context.universe
            for symbol in universe:
                self.subscribe(symbol)

        else:
            print('行情服务器登录失败[%d]' % self._reqid)
            self._reqid += 1
            self._quote.ReqUserLogin(BrokerID=self._brokerid, UserID=self._userid, )

        print('Rsp行情登录回报：[data] : %s [rsqinfo] : %s [isLast] : %s'% (loginField, rspInfo, isLast))


    def OnRspSubMarketData(self, data, info, n, last):
        if info.ErrorID == 0:
            print('Rsp订阅行情合约成功===')
        pass

    def onRtnDepthMarketData(self, data):
        """行情推送"""
        # print('Rtn订阅行情合约推送: %s' %data)

        if self._bar_length == 1:
            event = Event(EVENT_ON_TICK)
            event.dict = data.__dict__
            event.sync_flag = False
            self._eventEngine.sendEvent(event)
        else:
            bar_len = len(self._ticks)
            if bar_len < self._bar_length - 1:
                self._ticks.append(data.LastPrice)
            elif bar_len == self._bar_length - 1:
                self._ticks.append(data.LastPrice)
                arr = np.array(self._ticks)
                bar = Bar(self._ticks[0], self._ticks[-1], arr.max(), arr.min())
                self._ticks = []

                event = Event(EVENT_ON_TICK)
                event.dict = bar
                event.sync_flag = False
                self._eventEngine.sendEvent(event)


    #----------------------------------------------------
    # 行情主动函数
    #----------------------------------------------------
    def subscribe(self, instrumentid):
        """订阅合约"""
        self._quote.SubscribeMarketData(pInstrumentID=instrumentid)

    def unSubscribe(self, instrumentid):
        """退订合约"""
        self._quote.UnSubscribeMarketData(pInstrumentID=instrumentid)


    # private
    def _get_bar_length(self, fre):
        if fre == '1M':
            return 120
        elif fre == '3M':
            return 360
        elif fre == '5M':
            return 600
        elif fre == 'HM':
            return 60
        else:
            return 1

class TApi:
    '''
    封装交易服务器Api
    '''
    def __init__(self, eventEngine, context):
        self._eventEngine = eventEngine
        self._context = context
        self._trade = Trade()
        self._lock = threading.Lock()
        # 请求编号
        self._reqid = 0
        # 报单编号，由api负责管理
        self._orderRef = getMaxOrderRef()
        # 前置id FrontID
        self._frontID = 0
        # 会话id
        self._sessionID = 0
        # ReqOrderAction 报单操作ref
        self._order_action_ref = getMaxOrderActionRef()
        # 默认用户名密码
        self._userid = self._context.user_id
        self._password = self._context.password
        self._brokerid = self._context.broker_id

        # 注册交易handler
        # 主动
        self._eventEngine.register(EVENT_ORDER, self.sendOrder)                 # 下单
        self._eventEngine.register(EVENT_ORDER_STORAGE, insertSendOrderArgs)    # 保存下单参数
        self._eventEngine.register(EVENT_ORDER_STORAGE, ws_send_order)          # 推送下单参数
        self._eventEngine.register(EVENT_CANCEL, self.cancelOrder)              # 撤单
        self._eventEngine.register(EVENT_CANCEL_STORAGE, insertCancelOrderArgs) # 保存撤单参数
        self._eventEngine.register(EVENT_CANCEL_STORAGE, ws_cancel_order)       # 推送撤单参数

        # 每隔1秒查询持仓/账户
        self._eventEngine.registerSwicthHandlers([self.getPosition,self.getAccount])      # 推送撤单参数


        # 被动
        self._eventEngine.register(EVENT_ON_TRADE_CONNECTED, ws_market_connected)       # 交易服务器连接上
        self._eventEngine.register(EVENT_ON_TRADE_LOGIN, ws_market_login)               # 交易服务器登录
        self._eventEngine.register(EVENT_ON_SETTLEMENT_CONFIRM, ws_settlement_confirm)  # 交易服务器登录


        self._eventEngine.register(EVENT_ON_ORDER, insertRtnOrder)                      # 报单回报
        self._eventEngine.register(EVENT_ON_ORDER, ws_on_order)                         # 报单回报
        # self._eventEngine.register(EVENT_ON_ORDER, self.getAccount)                     # 报单回报后查询账户资金

        self._eventEngine.register(EVENT_ON_INPUT_ORDER, insertRspOrderInsert)          # 报单录入
        self._eventEngine.register(EVENT_ON_INPUT_ORDER, ws_insert_order)               # 报单录入

        self._eventEngine.register(EVENT_ON_INPUT_ORDER_ACTION, insertRspOrderAction)   # 输入报单
        self._eventEngine.register(EVENT_ON_INPUT_ORDER_ACTION, ws_insert_order_action) # 输入报单

        self._eventEngine.register(EVENT_ON_ORDER_ACTION, insertErrRtnOrderAction)      # 报单操作
        self._eventEngine.register(EVENT_ON_ORDER_ACTION, ws_error_order_action)        # 报单操作

        self._eventEngine.register(EVENT_ON_TRADE, insertRtnTrade)                      # 交易回报
        self._eventEngine.register(EVENT_ON_TRADE, ws_trade)                            # 交易回报
        # self._eventEngine.register(EVENT_ON_TRADE, self.getPosition)                    # 交易回报后查询持仓

        # 错误
        self._eventEngine.register(EVENT_ERROR, insertRspError)                         # 请求错误
        self._eventEngine.register(EVENT_ERROR, ws_rsp_error)                           # 请求错误

        # 更新账户&持仓
        self._eventEngine.register(EVENT_ON_ACCOUNT, updateAccount)                      # 更新账户
        self._eventEngine.register(EVENT_ON_POSITION, insertPosition)                    # 更新持仓





    def login(self):
        userTApi = self._trade.CreateApi()
        userSApi = self._trade.CreateSpi()
        self._trade.RegisterSpi(userSApi)
        # 连接交易服务器回调
        self._trade.OnFrontConnected = self.onFrontConnected
        self._trade.OnFrontDisconnected = self.onFrontDisconnected
        # 登录回调
        self._trade.OnRspUserLogin = self.onRspUserLogin
        #
        self._trade.OnRtnInstrumentStatus = self.onRtnInstrumentStatus
        # 结算单确认
        self._trade.OnRspSettlementInfoConfirm = self.onRspSettlementInfoConfirm
        # 查询全部交易合约
        self._trade.OnRspQryInstrument = self.onRspQryInstrument
        # tick截面数据
        self._trade.OnRspQryDepthMarketData = self.onRspQryDepthMarketData
        # 查询持仓
        self._trade.OnRspQryInvestorPosition = self.onRspQryInvestorPosition
        # 查询账户
        self._trade.OnRspQryTradingAccount = self.onRspQryTradingAccount
        # 报单录入
        self._trade.OnRspOrderInsert = self.onRspOrderInsert
        # 报单状态变化
        self._trade.OnRspOrderAction = self.onRspOrderAction
        # 报单状态改变
        self._trade.OnRtnOrder = self.onRtnOrder
        # 报单发生成交
        self._trade.OnRtnTrade = self.onRtnTrade
        # 报单录入错误
        self._trade.OnErrRtnOrderInsert = self.onErrRtnOrderInsert
        # 报价操作错误回报。由交易托管系统主动通知客户端，该方法会被调用。
        self._trade.OnErrRtnOrderAction = self.onErrRtnOrderAction
        # 请求错误
        self._trade.OnRspError = self.onRspError
        # 查询报单
        self._trade.OnRspQryOrder = self.onRspQryOrder


        self._trade.RegCB()
        self._trade.RegisterFront(self._context.trade_front)
        self._trade.SubscribePublicTopic(nResumeType=2)  # 只传送登录后公有流的内容
        self._trade.SubscribePrivateTopic(nResumeType=2)  # 只传送登录后私有流的内容
        self._trade.Init()


    def onFrontConnected(self):
        print('交易服务器连接成功')

        event = Event(EVENT_ON_TRADE_CONNECTED)
        event.dict = {'log': '交易服务器连接成功'}
        event.sync_flag = False
        self._eventEngine.sendEvent(event)

        self._reqid += 1
        self._trade.ReqUserLogin(BrokerID=self._brokerid, UserID=self._userid, Password=self._password)

    def onFrontDisconnected(self, nReason):
        print('交易服务器连接失败, 原因：%d' % nReason)

    def onRspUserLogin(self, loginField, rspInfo, reqid, isLast):
        """登陆回报"""
        if rspInfo.ErrorID == 0:
            print('交易服务器登陆成功')

            event = Event(EVENT_ON_TRADE_LOGIN)
            event.dict = {'log': '交易服务器登陆成功'}
            event.sync_flag = False
            self._eventEngine.sendEvent(event)

            self._frontID = loginField.FrontID
            self._sessionID = loginField.SessionID
            self._orderRef = int(loginField.MaxOrderRef)
            self._reqid += 1
            self._trade.ReqSettlementInfoConfirm(BrokerID=self._brokerid, InvestorID=self._userid)  # 对账单确认
            # self.getOrder()
        else:
            print('交易服务器登录失败 [%d]' % self._reqid)
            self._reqid += 1
            self._trade.ReqUserLogin(BrokerID=self._brokerid, UserID=self._userid, Password=self._password)

        print('Rsp交易登录回报：[data]=%s [rsqinfo] = %s [reqid] = %s [isLast] = %s'% (loginField, rspInfo, reqid,isLast))


    def onRtnInstrumentStatus(self, data):
        pass
        # print('Rtn合约状态：%s '% data.__dict__) # 交易所关闭前会返回数据


    def onRspSettlementInfoConfirm(self, settlementInfoConfirmField, rspInfo, reqid, isLast):
        if rspInfo.ErrorID == 0:
            print('Rsp结算单确认完成：%s' % settlementInfoConfirmField.__dict__)

            event = Event(EVENT_ON_SETTLEMENT_CONFIRM)
            event.dict = settlementInfoConfirmField.__dict__
            event.sync_flag = False
            self._eventEngine.sendEvent(event)

            # 结算确认后开始订阅数据
            self._context.settlementInfo_confirm_flag = True
            # 查询全部合约资料
            # self.getInstrument()
        else:
            print('Rsp结算单确认错误 %s',settlementInfoConfirmField.__dict__)


    def onRspQryInstrument(self, data, error, n, islast):
        """
        合约查询回报
        """
        if error.ErrorID == 0:
            print('RspQry查询所有合约成功: %s' % data.__dict__)
            # self.__instruments.append(data)
            if islast == True:
                print('---查询所有合约完毕---')
                pass
                # ret = pd.DataFrame(self.__instruments)
                # print(ret)
                # ret = ret.set_index('InstrumentID')
                # ret.to_csv('Instrument.csv')


    def onRspQryDepthMarketData(self, data, error, n, last):
        # tick数据回报
        print('RspQry交易tick数据: [%s] [%s]'% (data.__dict__, error))

    def onRspQryInvestorPosition(self, data, error, n, last):
        """持仓查询回报"""
        # print('RspQry查询持仓回报: [%s] [%s]'% (data.__dict__, error))
        if error.ErrorID == 0:
            event = Event(EVENT_ON_POSITION)
            dict = deepcopy(data.__dict__)
            event.dict = dict
            event.sync_flag = False
            self._eventEngine.sendEvent(event)

    # ----------------------------------------------------------------------
    def onRspQryTradingAccount(self, data, error, n, last):
        """资金账户查询回报"""
        # if error.ErrorID == 0:
        # print('RspQry查询账户资金回报: [%s] [%s]'% (data.__dict__, error))
        if error.ErrorID == 0:
            event = Event(EVENT_ON_ACCOUNT)
            dict = deepcopy(data.__dict__)
            event.dict = dict
            event.sync_flag = False
            self._eventEngine.sendEvent(event)


    def onRtnTrade(self, data):
        """
        成交回报。
        当发生成交时交易托管系统会通知客户端，该方法会被调用。 
        """
        print('--------------------------------------------------------')
        print('--------------------------------------------------------')
        print('Rtn成交回报:')
        print(data.__dict__)
        print('--------------------------------------------------------')
        print('--------------------------------------------------------')
        event = Event(EVENT_ON_TRADE)
        dict = deepcopy(data.__dict__)
        event.dict = dict
        event.sync_flag = False
        self._eventEngine.sendEvent(event)

    def onRtnOrder(self, data):
        """
        报单回报.
        当客户端进行报单录入、报单操作及其它原因(如部分成交)导致报单状态发生变化时，交易托管系统会主动通知客户端，该方法会被调用。
        """
        # 更新最大报单编号
        # newref = data.OrderRef
        # self.__orderRef = max(self._orderRef, int(newref))

        print('--------------------------------------------------------')
        print('--------------------------------------------------------')
        print('Rtn报单回报: %s  线程：%s' % (data.__dict__, threading.current_thread().name))
        print('--------------------------------------------------------')
        print('--------------------------------------------------------')

        dict = deepcopy(data.__dict__)
        dict = getStrategyInfo(dict)

        # 更新环境中的挂单
        if data.__dict__['OrderSysID'] is not '':

            if data.__dict__['OrderStatus'] == 'AllTraded' or data.__dict__['OrderStatus'] == 'Canceled':
                del (self._context.orders[data.__dict__['OrderSysID']])
            else:
                self._context.orders[data.__dict__['OrderSysID']] = dict

            print('当前挂单')
            print(self._context.orders)
            print('--------------------------------------------------------')
            print('--------------------------------------------------------')

        # if data.OrderSysID in self.__env.orders.keys():
        #     if data.OrderStatus == 'AllTraded' or data.OrderStatus == 'Canceled':
        #         del(self.__env.orders[data.OrderSysID])
        #     else:
        #         self.__env.orders[data.OrderSysID] = order
        # else:
        #     self.__env.orders[data.OrderSysID] = order

        event = Event(EVENT_ON_ORDER)
        event.dict = dict
        event.sync_flag = False
        self._eventEngine.sendEvent(event)

    def onRspOrderInsert(self, data, error, n, last):
        """
        报单录入应答。
        当客户端发出过报单录入指令后，交易托管系统返回响应时， 该方法会被调用。
        """
        print('--------------------------------------------------------')
        print('--------------------------------------------------------')
        print('Rsp报单录入回报：%s  线程：%s' % (data.__dict__,  threading.current_thread().name))
        print('--------------------------------------------------------')
        print('--------------------------------------------------------')

        if error.ErrorID == 0:
            event = Event(EVENT_ON_INPUT_ORDER)
            dict = deepcopy(data.__dict__)
            event.dict = dict
            event.sync_flag = False
            self._eventEngine.sendEvent(event)



    def onRspOrderAction(self, data, error, n, last):
        """
        报单操作应答。
        报单操作包括报单的撤销、报单的挂起、报单的激活、报单 的修改。当客户端发出过报单操作指令后，交易托管系统返回响应时，该方法会 被调用。 
        """
        print('--------------------------------------------------------')
        print('--------------------------------------------------------')
        print('Rsp报单操作/报单状态改变：%s' % data.__dict__)
        print('--------------------------------------------------------')
        print('--------------------------------------------------------')

        if error.ErrorID == 0:
            event = Event(EVENT_ON_INPUT_ORDER_ACTION)
            dict = deepcopy(data.__dict__)
            event.dict = dict
            event.sync_flag = False
            self._eventEngine.sendEvent(event)


    def onErrRtnOrderInsert(self, data, error):
        """
        报单录入错误回报。由交易托管系统主动通知客户端，该方法会被调用
        """
        print('Rtn报单录入错误回报: %s  线程：%s' % (data.__dict__, error.__dict__) )

        if error.ErrorID == 0:
            event = Event(EVENT_ON_INPUT_ORDER)
            dict = deepcopy(data.__dict__)
            event.dict = dict
            event.sync_flag = False
            self._eventEngine.sendEvent(event)


    def onErrRtnOrderAction(self, data, error):
        '''
        报价操作错误回报。
        由交易托管系统主动通知客户端，该方法会被调用。
        '''
        print('Rtn报价操作错误回报: %s' % data.__dict__)

        event = Event(EVENT_ON_ORDER_ACTION)
        dict = deepcopy(data.__dict__)
        event.dict = dict
        event.sync_flag = False
        self._eventEngine.sendEvent(event)


    def onRspError(self, error, n, last):
        """
        针对用户请求的出错通知。
        """
        print('Rsp行情请求出错: %s' % error.__dict__)

        event = Event(EVENT_ERROR)
        dict = deepcopy(error.__dict__)
        event.dict = dict
        event.sync_flag = False
        self._eventEngine.sendEvent(event)

    def onRspQryOrder(self, data, error, n, last):
        """
        查询Order。
        """
        print('RspQry查询挂单: %s' % error.__dict__)
        # event = Event(EVENT_ERROR)
        # dict = deepcopy(error.__dict__)
        # event.dict = dict
        # event.sync_flag = False
        # self._eventEngine.sendEvent(event)

    #----------------------------------------------------
    # 交易主动函数
    #----------------------------------------------------
    def getInstrument(self):
        """查询全部合约信息"""
        self._reqid += 1
        self._trade.ReqQryInstrument()

    def reqQryDepthMarketData(self, InstrumentID, ExchangeID):
        # 查询合约截面数据
        self._reqid += 1
        self._trade.ReqQryDepthMarketData(InstrumentID=InstrumentID, ExchangeID=ExchangeID)

    # 查询报单
    def getOrder(self):
        self._reqid += 1
        self._trade.ReqQryOrder(BrokerID=self._brokerid, InvestorID = self._userid)


    def getAccount(self, event):
        """查询账户"""
        self._lock.acquire()
        self._reqid += 1
        self._lock.release()
        self._trade.ReqQryTradingAccount(self._brokerid, self._userid)

    def getPosition(self, event):
        """查询持仓"""
        self._lock.acquire()
        self._reqid += 1
        self._lock.release()
        self._trade.ReqQryInvestorPosition(BrokerID=self._brokerid, InvestorID=self._userid)

    def sendOrder(self, event):
        self._lock.acquire()
        self._reqid += 1
        self._orderRef += 1
        self._lock.release()

        instrumentid = event.dict['symbol']
        vol = event.dict['vol']
        limit_price = event.dict['limit_price']
        direction = event.dict['direction']
        offset = event.dict['offset']
        priceType = event.dict['price_type']
        stop_price = event.dict['stop_price']
        contingent_condition = event.dict['contingent_condition']

        event.dict['reqid'] = self._reqid
        event.dict['order_ref'] = self._orderRef

        _event  = Event(EVENT_ORDER_STORAGE)
        _event.dict = event.dict
        _event.sync_flag = False
        self._eventEngine.sendEvent(_event)

        print('--------------------------------------------------------')
        print('--------------------------------------------------------')
        print('发送报单：%s 线程：%s' % (event.dict, threading.current_thread().name))
        print('--------------------------------------------------------')
        print('--------------------------------------------------------')

        self._trade.ReqOrderInsert(BrokerID=self._brokerid,
                                    InvestorID=self._userid,
                                    InstrumentID=instrumentid,
                                    LimitPrice=limit_price,
                                    OrderRef='{0:>12}'.format(self._orderRef),
                                    UserID=self._userid,
                                    OrderPriceType=priceType,
                                    Direction=direction,
                                    CombOffsetFlag=offset,
                                    CombHedgeFlag=HedgeFlagType.Speculation.__char__(),
                                    VolumeTotalOriginal=vol,
                                    TimeCondition=TimeConditionType.GFD,
                                    VolumeCondition=VolumeConditionType.AV,
                                    MinVolume=1,
                                    ForceCloseReason=ForceCloseReasonType.NotForceClose,
                                    ContingentCondition=contingent_condition,
                                    StopPrice=stop_price)
        return self._orderRef

    def cancelOrder(self, event):
        """撤单"""
        order = event.dict
        self._lock.acquire()
        self._reqid = self._reqid + 1
        self._order_action_ref += 1
        self._lock.release()
        event.dict['reqid'] = self._reqid
        event.dict['order_action_ref'] = self._order_action_ref

        _event = Event(EVENT_CANCEL_STORAGE)
        _event.dict = event.dict
        _event.sync_flag = False
        self._eventEngine.sendEvent(_event)

        print('--------------------------------------------------------')
        print('--------------------------------------------------------')
        print('发送撤单：%s  线程：%s' % (event.dict, threading.current_thread().name))
        print('--------------------------------------------------------')
        print('--------------------------------------------------------')

        self._trade.ReqOrderAction(BrokerID=self._brokerid,
                                   OrderActionRef= self._order_action_ref,
                              InvestorID=self._userid,
                              OrderRef=order['OrderRef'],
                              FrontID=int(order['FrontID']),
                              SessionID=int(order['SessionID']),
                              OrderSysID=order['OrderSysID'],
                              ActionFlag=ActionFlagType.Delete,
                              ExchangeID=order['ExchangeID'],
                              InstrumentID=order['InstrumentID'])



