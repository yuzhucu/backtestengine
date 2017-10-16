# # encoding: UTF-8
# """
# CTP的底层接口来自'HaiFeng'-PY-AT
# 简化封装采用VN.PY的结构
# """
# from engine.threadEventEngine import  *
# from engine.eventType import  *
# from ctp.ctp_struct import *
# from ctp.quote import Quote
# from ctp.trade import Trade
# import time
# import pandas as pd
# import datetime
# import random
# ########################################################################
# class MdApi:
#     """
#     Demo中的行情API封装
#     封装后所有数据自动推送到事件驱动引擎中，由其负责推送到各个监听该事件的回调函数上
#
#     对用户暴露的主动函数包括:
#     登陆 login
#     订阅合约 subscribe
#     """
#     #----------------------------------------------------------------------
#     def __init__(self, eventEngine):
#         """
#         API对象的初始化函数
#         """
#         # 事件引擎，所有数据都推送到其中，再由事件引擎进行分发
#         self.__eventEngine = eventEngine
#         self.q = Quote()
#
#         # 请求编号，由api负责管理
#         self.__reqid = 0
#
#         # 以下变量用于实现连接和重连后的自动登陆
#         self.__userid = '008105'
#         self.__password = '1'
#         self.__brokerid = '9999'
#
#     def login(self):
#         api = self.q.CreateApi()
#         spi = self.q.CreateSpi()
#         self.q.RegisterSpi(spi)
#         self.q.OnFrontConnected = self.onFrontConnected  # 交易服务器登陆相应
#         self.q.OnRspUserLogin = self.onRspUserLogin  # 用户登陆
#         self.q.OnFrontDisconnected = self.onFrontDisconnected
#         self.q.OnRspError = self.onRspError
#         self.q.OnRspSubMarketData = self.OnRspSubMarketData
#         self.q.OnRtnDepthMarketData = self.onRtnDepthMarketData
#
#         self.q.RegCB()
#         self.q.RegisterFront('tcp://180.168.146.187:10010')
#         self.q.Init()
#         # self.q.Join()
#
#     def put_log_event(self, log):  # log事件注册
#         event = Event(type=EVENT_LOG)
#         event.dict['log'] = log
#         self.__eventEngine.sendEvent(event)
#
#     def onFrontConnected(self):
#         """服务器连接"""
#         print('---行情服务器连接成功')
#         self.put_log_event('行情服务器连接成功')
#         self.q.ReqUserLogin(BrokerID=self.__brokerid, UserID=self.__userid, Password=self.__password)
#
#     def onFrontDisconnected(self, n):
#         """服务器断开"""
#         self.put_log_event('行情服务器连接断开')
#
#     def onRspError(self, error, n, last):
#         """错误回报"""
#         log = '行情错误回报，错误代码：' + str(error.__dict___['ErrorID']) + '错误信息：' + + str(error.__dict___['ErrorMsg'])
#         self.put_log_event(log)
#
#     def onRspUserLogin(self, data, error, n, last):
#         """登陆回报"""
#         print('---行情服务器登陆成功')
#         if error.__dict__['ErrorID'] == 0:
#             log =  '行情服务器登陆成功'
#         else:
#             log = '登陆回报，错误代码：' + str(error.__dict__['ErrorID']) + ',   错误信息：' + str(error.__dict__['ErrorMsg'])
#         self.put_log_event(log)
#
#     def OnRspSubMarketData(self, data, info, n, last):
#         pass
#
#     def onRtnDepthMarketData(self, data):
#         """行情推送"""
#         # 特定合约行情事件
#         event2 = Event(type=(EVENT_MARKETDATA_CONTRACT + data.__dict__['InstrumentID']))
#         event2.dict['data'] = data.__dict__
#         self.__eventEngine.put(event2)
#
#     # ----------------------------------------------------------------------
#     def subscribe(self, instrumentid):
#         """订阅合约"""
#         self.q.SubscribeMarketData(pInstrumentID=instrumentid)
#
#     def unsubscribe(self, instrumentid):
#         """退订合约"""
#         self.q.UnSubscribeMarketData(pInstrumentID=instrumentid)
#
# ########################################################################
# class TdApi:
#     """
#     Demo中的交易API封装
#     主动函数包括：
#     login 登陆
#     getInstrument 查询合约信息
#     getAccount 查询账号资金
#     getInvestor 查询投资者
#     getPosition 查询持仓
#     sendOrder 发单
#     cancelOrder 撤单
#     """
#
#     #----------------------------------------------------------------------
#     def __init__(self, eventEngine):
#         """API对象的初始化函数"""
#         # 事件引擎，所有数据都推送到其中，再由事件引擎进行分发
#         self.__eventEngine = eventEngine
#         self.t = Trade()
#
#         # 请求编号，由api负责管理
#         self.__reqid = 0
#
#         # 报单编号，由api负责管理
#         self.__orderref = random.randrange(start=1000,stop=9000,step=random.randint(10,100)  )
#
#         # 以下变量用于实现连接和重连后的自动登陆
#         self.__userid = '008105'
#         self.__password = '1'
#         self.__brokerid = '9999'
#
#     def login(self):
#         api = self.t.CreateApi()
#         spi = self.t.CreateSpi()
#         self.t.RegisterSpi(spi)
#         self.t.OnFrontConnected = self.onFrontConnected  # 交易服务器登陆相应
#         self.t.OnRspUserLogin = self.onRspUserLogin  # 用户登陆
#         self.t.OnRtnInstrumentStatus = self.OnRtnInstrumentStatus
#         self.t.OnRspSettlementInfoConfirm = self.onRspSettlementInfoConfirm  # 结算单确认
#         self.t.OnRspQryInstrument = self.onRspQryInstrument  # 查询全部交易合约
#         self.t.OnRspQryDepthMarketData = self.onRspQryDepthMarketData  # tick截面数据
#         self.t.OnRspQryInvestorPosition = self.onRspQryInvestorPosition#查询持仓
#         self.t.OnRspQryTradingAccount = self.onRspQryTradingAccount#查询账户
#         self.t.OnRtnOrder = self.onRtnOrder#报单
#         self.t.OnRtnTrade = self.onRtnTrade#成交
#         #——————错误事件
#         self.t.OnRspOrderInsert = self.onRspOrderInsert
#         self.t.OnRspOrderAction =self.onRspOrderAction
#         self.t.OnRspError = self.onRspError
#
#         self.t.RegCB()
#         self.t.RegisterFront('tcp://180.168.146.187:10000')
#         self.t.Init()
#         # self.t.Join()
#
#     def put_log_event(self, log):  # log事件注册
#         event = Event(type=EVENT_LOG)
#         event.dict['log'] = log
#         self.__eventEngine.sendEvent(event)
#
#     def onFrontConnected(self):
#         """服务器连接"""
#         print('---交易服务器连接成功')
#         self.put_log_event('交易服务器连接成功')
#         self.t.ReqUserLogin(BrokerID=self.__brokerid, UserID=self.__userid, Password=self.__password)
#
#     def OnRtnInstrumentStatus(self, data):
#         pass
#
#     def onRspUserLogin(self, data, error, n, last):
#         """登陆回报"""
#         print('---交易服务器登陆成功')
#         if error.__dict__['ErrorID'] == 0:
#             self.Investor = data.__dict__['UserID']
#             self.BrokerID = data.__dict__['BrokerID']
#             log = data.__dict__['UserID'] + '交易服务器登陆成功'
#             self.t.ReqSettlementInfoConfirm(self.BrokerID, self.Investor)  # 对账单确认
#         else:
#             log = '登陆回报，错误代码：' + str(error.__dict__['ErrorID']) + ',   错误信息：' + str(error.__dict__['ErrorMsg'])
#         self.put_log_event(log)
#
#     def onRspSettlementInfoConfirm(self, data, error, n, last):
#         """确认结算信息回报"""
#         log = '结算信息确认完成'
#         self.put_log_event(log)
#         time.sleep(1)
#         self.getInstrument()  # 查询合约资料
#
#     def onRspQryInstrument(self, data, error, n, last):
#         """
#         合约查询回报
#         由于该回报的推送速度极快，因此不适合全部存入队列中处理，
#         选择先储存在一个本地字典中，全部收集完毕后再推送到队列中
#         （由于耗时过长目前使用其他进程读取）
#         """
#         if error.__dict__['ErrorID'] == 0:
#             event = Event(type=EVENT_INSTRUMENT)
#             event.dict['data'] = data.__dict__
#             event.dict['last'] = last
#             self.__eventEngine.sendEvent(event)
#             if last == True:
#                 time.sleep(2)
#                 self.t.ReqQryDepthMarketData()  # 查询合约截面数据
#         else:
#             log = '合约投资者回报，错误代码：' + str(error.__dict__['ErrorID']) + ',   错误信息：' + str(error.__dict__['ErrorMsg'])
#             self.put_log_event(log)
#
#     def onRspQryDepthMarketData(self, data, error, n, last):
#         # 常规行情事件
#         event = Event(type=EVENT_MARKETDATA)
#         event.dict['data'] = data.__dict__
#         event.dict['last'] = last
#         self.__eventEngine.sendEvent(event)
#
#     def onRspQryInvestorPosition(self, data, error, n, last):
#         """持仓查询回报"""
#         if error.__dict__['ErrorID'] == 0:
#             event = Event(type=EVENT_POSITION)
#             event.dict['data'] = data.__dict__
#             event.dict['last'] = last
#             self.__eventEngine.sendEvent(event)
#         else:
#             log = ('持仓查询回报，错误代码：'  +str(error.__dict__['ErrorID']) + ',   错误信息：' +str(error.__dict__['ErrorMsg']))
#             self.put_log_event(log)
#
#     # ----------------------------------------------------------------------
#     def onRspQryTradingAccount(self, data, error, n, last):
#         """资金账户查询回报"""
#         if error.__dict__['ErrorID'] == 0:
#             event = Event(type=EVENT_ACCOUNT)
#             event.dict['data'] = data.__dict__
#             self.__eventEngine.sendEvent(event)
#         else:
#             log = ('账户查询回报，错误代码：' +str(error.__dict__['ErrorID']) + ',   错误信息：' +str(error.__dict__['ErrorMsg']))
#             self.put_log_event(log)
#
#     def onRtnTrade(self, data):
#         """成交回报"""
#         # 常规成交事件
#         event1 = Event(type=EVENT_TRADE)
#         event1.dict['data'] = data.__dict__
#         self.__eventEngine.put(event1)
#
#     def onRtnOrder(self, data):
#         """报单回报"""
#         # 更新最大报单编号
#         newref = data.__dict__['OrderRef']
#         self.__orderref = max(self.__orderref, int(newref))
#         # 常规报单事件
#         event1 = Event(type=EVENT_ORDER)
#         event1.dict['data'] = data.__dict__
#         self.__eventEngine.put(event1)
#
#     def onRspOrderInsert(self, data, error, n, last):
#         """发单错误（柜台）"""
#         log = data.__dict__['InstrumentID'] + ' 发单错误回报，错误代码：' + str(error.__dict__['ErrorID']) + ',   错误信息：' + str(
#             error.__dict__['ErrorMsg'])
#         self.put_log_event(log)
#
#     def onErrRtnOrderInsert(self, data, error):
#         """发单错误回报（交易所）"""
#         log = data.__dict__['InstrumentID'] + '发单错误回报，错误代码：' + str(error.__dict__['ErrorID']) + ',   错误信息：' + str(
#             error.__dict__['ErrorMsg'])
#         self.put_log_event(log)
#
#     def onRspError(self, error, n, last):
#         """错误回报"""
#         log = '交易错误回报，错误代码：' + str(error.__dict__['ErrorID']) + ',   错误信息：' + str(error.__dict__['ErrorMsg'])
#         self.put_log_event(log)
#     # ----------------------------------------------------------------------
#     def onRspOrderAction(self, data, error, n, last):
#         """撤单错误（柜台）"""
#         log = '撤单错误回报，错误代码：' + str(error.__dict__['ErrorID']) + ',   错误信息：' + str(error.__dict__['ErrorMsg'])
#         self.put_log_event(log)
#     # ----------------------------------------------------------------------
#     def onErrRtnOrderAction(self, data, error):
#         """撤单错误回报（交易所）"""
#         event = Event(type=EVENT_LOG)
#         log = data['合约代码'] + '  撤单错误回报，错误代码：' + str(error.__dict__['ErrorID']) + ',   错误信息：' + str(
#             error.__dict__['ErrorMsg'])
#         event.dict['log'] = log
#         self.__eventEngine.sendEvent(event)
#
#     def getInstrument(self):
#         """查询合约"""
#         self.__reqid = self.__reqid + 1
#         self.t.ReqQryInstrument()
#     def getAccount(self):
#         """查询账户"""
#         self.__reqid = self.__reqid + 1
#         self.t.ReqQryTradingAccount(self.__brokerid , self.__userid )
#     # ----------------------------------------------------------------------
#     def getPosition(self):
#         """查询持仓"""
#         self.__reqid = self.__reqid + 1
#         self.t.ReqQryInvestorPosition(self.__brokerid , self.__userid )
#
#     def sendorder(self, instrumentid, price, vol, direction, offset):
#         """发单"""
#         self.__reqid = self.__reqid + 1
#         self.__orderref = self.__orderref + 1
#         # 限价
#         self.t.ReqOrderInsert(BrokerID=self.__brokerid,
#                               InvestorID=self.__userid,
#                               InstrumentID=instrumentid,
#                               OrderRef='{0:>12}'.format(self.__orderref),
#                               UserID=self.__userid,
#                               OrderPriceType=OrderPriceTypeType.LimitPrice,
#                               Direction=direction,
#                               CombOffsetFlag=offset,
#                               CombHedgeFlag=HedgeFlagType.Speculation.__char__(),
#                               LimitPrice=price,
#                               VolumeTotalOriginal=vol,
#                               TimeCondition=TimeConditionType.GFD,
#                               VolumeCondition=VolumeConditionType.AV,
#                               MinVolume=1,
#                               ForceCloseReason=ForceCloseReasonType.NotForceClose,
#                               ContingentCondition=ContingentConditionType.Immediately)
#         return self.__orderref
#         # 返回订单号，便于某些算法进行动态管理
#         # OrderPriceType--LimitPrice 限价单
#         # CombHedgeFlag--投机套保标记，默认投机单Speculation
#         # TimeConditionType是一个有效期类型类型#当日有效--GFD
#         # VolumeConditionType是一个成交量类型类型#任何数量--VolumeConditionType.AV
#         # ContingentConditionType是一个触发条件类型，#立即ContingentConditionType.Immediately
#
#     def buy(self, symbol, price, vol):  # 买开多开
#         direction = DirectionType.Buy
#         offset = OffsetFlagType.Open.__char__()
#         self.sendorder(symbol, price, vol, direction, offset)
#
#     def sell(self, symbol, price, vol):  # 多平
#         direction = DirectionType.Sell
#         offset = OffsetFlagType.Close.__char__()
#         self.sendorder(symbol, price, vol, direction, offset)
#
#     def selltoday(self, symbol, price, vol):  # 平今多
#         direction = DirectionType.Sell
#         offset = OffsetFlagType.CloseToday.__char__()
#         self.sendorder(symbol, price, vol, direction, offset)
#
#     def short(self, symbol, price, vol):  # 卖开空开
#         direction = DirectionType.Sell
#         offset = OffsetFlagType.Open.__char__()
#         self.sendorder(symbol, price, vol, direction, offset)
#
#     def cover(self, symbol, price, vol):  # 空平
#         direction = DirectionType.Buy
#         offset = OffsetFlagType.Close.__char__()
#         self.sendorder(symbol, price, vol, direction, offset)
#
#     def covertoday(self, symbol, price, vol):  # 平今空
#         direction = DirectionType.Buy
#         offset = OffsetFlagType.CloseToday.__char__()
#         self.sendorder(symbol, price, vol, direction, offset)
#
#     # ----------------------------------------------------------------------
#     def cancelOrder(self, order):
#         """撤单"""
#         # print(order)
#         self.__reqid = self.__reqid + 1
#         self.t.ReqOrderAction(BrokerID=self.__brokerid,
#                               InvestorID=self.__userid,
#                               OrderRef=order['本地报单编号'],
#                               FrontID=int(order['前置编号']),
#                               SessionID=int(order['会话编号']),
#                               OrderSysID=order['报单编号'],
#                               ActionFlag=ActionFlagType.Delete,
#                               ExchangeID=order["交易所代码"],
#                               InstrumentID=order['合约代码'])
#
#
#
# ########################################################################
# class MainEngine:
#     """主引擎，负责对API的调度"""
#
#     #----------------------------------------------------------------------
#     def __init__(self):
#         """Constructor"""
#         self.ee = EventEngine()         # 创建事件驱动引擎
#         self.md = MdApi(self.ee)    # 创建API接口
#         self.td = TdApi(self.ee)
#         # self.ee.start()                 # 启动事件驱动引擎
#         # self.ee.register(EVENT_LOG, self.p_log)  # 打印测试
#         # self.ee.register(EVENT_INSTRUMENT, self.insertInstrument)
#         # self.list_instrument = []#保存合约资料
#         # self.ee.register(EVENT_MARKETDATA, self.insertMarketData)
#         # self.list_marketdata = []#保存合约资料
#         # # 循环查询持仓和账户相关
#         # self.countGet = 0  # 查询延时计数
#         # self.lastGet = 'Position'  # 上次查询的性质，先查询账户
#         # #持仓和账户
#         # #self.ee.register (EVENT_ACCOUNT,self.account)
#         # #self.ee.register (EVENT_POSITION,self.position)
#         # #持仓和账户数据
#         # self.dictaccount ={}
#         # self.dictposition ={}
#         # # 委托事件
#         # self.ee.register (EVENT_ORDER,self.order)
#         # self.dictorder={}#报单数据
#         # # 成交事件
#         # self.ee.register (EVENT_TRADE,self.trader)
#         # self.dicttrade={}#成交数据
#         # #注册TICK行情
#         # self.ee.register(EVENT_MARKETDATA_CONTRACT + 'rb1705', self.deepdata)
#
#     #----------------------------------------------------------------------
#     def login(self):
#         """登陆"""
#         self.md.login()
#         self.td.login()
#     def p_log(self,event):
#         print(event.dict['log'])
#     def deepdata(self,event):
#         data = self.DepthMarketDataField(event.dict['data'])
#         print(data)
#
#     def DepthMarketDataField(self, var):
#         tmp = {}
#         tmp["交易日"] = var["TradingDay"]
#         tmp["合约代码"] = var["InstrumentID"]
#         tmp["交易所代码"] = var["ExchangeID"]
#         tmp["最新价"] = var["LastPrice"]
#         tmp["昨收盘"] = var["PreClosePrice"]
#         tmp["昨持仓量"] = var["PreOpenInterest"]
#         tmp["今开盘"] = var["OpenPrice"]
#         tmp["最高价"] = var["HighestPrice"]
#         tmp["最低价"] = var["LowestPrice"]
#         tmp["成交量"] = var["Volume"]
#         tmp["成交金额"] = var["Turnover"]
#         tmp["持仓量"] = var["OpenInterest"]
#         tmp["今收盘"] = var["ClosePrice"]
#         tmp["本次结算价"] = var["SettlementPrice"]
#         tmp["时间"] = var["UpdateTime"]
#         tmp["申买价一"] = var["BidPrice1"]
#         tmp["申买量一"] = var["BidVolume1"]
#         tmp["申卖价一"] = var["AskPrice1"]
#         tmp["申卖量一"] = var["AskVolume1"]
#         tmp["当日均价"] = var["AveragePrice"]
#         return tmp
#
#
#     def insertInstrument(self, event):
#         """插入合约对象"""
#         data = event.dict['data']
#         last = event.dict['last']
#         self.list_instrument.append(data)
#         if last:#最后一条数据
#             # 将查询完成的合约信息保存到本地文件，今日登录可直接使用不再查询
#             event = Event(type=EVENT_LOG)
#             log = '合约信息查询完成'
#             event.dict['log'] = log
#             self.ee.sendEvent(event)
#             ret = pd.DataFrame(self.list_instrument)
#             ret = ret.set_index('InstrumentID')
#             ret.to_pickle('Instrument')
#             event = Event(type=EVENT_LOG)
#             log = '合约信息已经保存'
#             event.dict['log'] = log
#             self.ee.sendEvent(event)
#             #print(ret)
#
#     def insertMarketData(self, event):
#         data = event.dict['data']
#         last = event.dict['last']
#         self.list_marketdata.append(data)
#         if last:
#             # 将查询完成的合约信息保存到本地文件，今日登录可直接使用不再查询
#             event = Event(type=EVENT_LOG)
#             log = '合约截面数据查询完成'
#             event.dict['log'] = log
#             self.ee.sendEvent(event)
#             ret = pd.DataFrame(self.list_marketdata)
#             ret = ret.set_index('InstrumentID')
#             ret.to_pickle('MarketData')
#             event = Event(type=EVENT_LOG)
#             log = '合约截面数据已经保存'
#             event.dict['log'] = log
#             self.ee.sendEvent(event)
#             self._zhuli(ret)#计算主力合约
#
#     def _zhuli(self,ret):#计算主力合约，在下单的时候要用，涨跌停板价是市价下单用
#         Instrument = pd.read_pickle('Instrument')
#         Marketdata = ret#从 insertMarketData函数传递过来的数据
#         id_list =['hc','bu','zn','ru','al','cu','rb','ni','sn','p','pp','jd','i','jm','v','l','y','c','m','j','cs','ZC','FG','MA','CF','RM','TA','SR']
#         zhuli = []
#         for ID in id_list :
#             var_I = Instrument.loc[Instrument['ProductID'] == ID]#按合约简称索引
#             #print(var_I )
#             var_M =[]
#             for index in var_I.index:
#                 var_M.append(Marketdata.ix[index])
#             var_M = pd.DataFrame(var_M)#搞到TICK截面
#             #print(var_M )
#             var_M = var_M.sort_values(by='OpenInterest',ascending= False )#持仓降序索引，以持仓为基准，不以成交量为基准
#             #print(var_M )
#             index_1 =var_M.index[0]#连一代码
#             index_2 =var_M.index[1]#连二代码
#             zlinfo = {}
#             zlinfo['合约简称'] =ID
#             zlinfo["合约名称"] =var_I.ix[ index_1]["InstrumentName"]
#             zlinfo['合约代码'] = index_1
#             zlinfo['市场代码'] = var_I.ix[ index_1]['ExchangeID']
#             zlinfo['合约乘数'] = var_I.ix[ index_1]['VolumeMultiple']
#             zlinfo['合约跳价'] =var_I.ix[ index_1]['PriceTick']
#             zlinfo['涨停板价'] = var_M.ix[ index_1]['UpperLimitPrice']
#             zlinfo['跌停板价'] = var_M.ix[ index_1]['LowerLimitPrice']
#             zlinfo['主力持仓'] = var_M.ix[ index_1]['OpenInterest']
#             zlinfo['次月合约'] = index_2
#             zlinfo['次月持仓'] = var_M.ix[ index_2]['OpenInterest']
#             zlinfo['次月涨停'] = var_M.ix[ index_2]['UpperLimitPrice']
#             zlinfo['次月跌停'] = var_M.ix[ index_2]['LowerLimitPrice']
#             #print(zlinfo)
#             zhuli.append(zlinfo)
#         zhuli = pd.DataFrame(zhuli)
#         zhuli.to_pickle('zl')
#         #print(zhuli)
#         self.list_instrument=[]
#         self.list_marketdata=[]#清空数据，没有用了
#         #log事件
#         event = Event(type=EVENT_LOG)
#         log = '主力合约已经保存'
#         event.dict['log'] = log
#         self.ee.sendEvent(event)
#          ##推送主力合约数据，修改py_ctp目录下eventType ,增加EVENT_PRODUCT事件。暂时用不上。后面要用到。
#         event = Event(type=EVENT_PRODUCT)
#         event.dict['data'] = zhuli
#         self.ee.sendEvent(event)
#         # 开始循环查询
#         self.ee.register(EVENT_TIMER, self.getAccountPosition)#定时器事件
#         self.md.subscribe('rb1705')
#
#     def account(self,event):#处理账户事件数据
#         self.dictaccount  = self.TradingAccountField(event.dict['data'])
#         print(self.dictaccount)
#     def TradingAccountField(self,var):
#         tmp = {}
#         tmp["投资者帐号"] = var["AccountID"]
#         tmp["静态权益"] = var["PreBalance"]
#         tmp["上次存款额"] = var["PreDeposit"]
#         tmp["入金金额"] = var["Deposit"]
#         tmp["出金金额"] = var["Withdraw"]
#         tmp["冻结的保证金"] = var["FrozenMargin"]
#         tmp["当前保证金总额"] = var["CurrMargin"]
#         tmp["手续费"] = var["Commission"]
#         tmp["平仓盈亏"] = var["CloseProfit"]
#         tmp["持仓盈亏"] = var["PositionProfit"]
#         tmp["动态权益"] = var["Balance"]
#         tmp["可用资金"] = var["Available"]
#         tmp["可取资金"] = var["WithdrawQuota"]
#         tmp["交易日"] = var["TradingDay"]
#         tmp["时间"] =datetime.datetime.now()
#         return tmp
#     def position(self, event):#处理持仓事件数据
#         data = self.InvestorPositionField(event.dict['data'])
#         last = event.dict['last']
#         index = data['合约代码'] + '.' + data['持仓多空方向']
#         #理论上很少有锁仓
#         self.dictposition[index] =data
#         if last == True :
#             for key in self.dictposition.keys():
#                 print (self.dictposition[key] )
#
#
#
#
#     def InvestorPositionField(self,var):
#         tmp={}
#         tmp["合约代码"]=var["InstrumentID"]
#         tmp["持仓多空方向"]=var["PosiDirection"]
#         tmp["持仓日期"]=var["PositionDate"]
#         tmp["上日持仓"]=var["YdPosition"]
#         tmp["持仓总数"]=var["Position"]
#         tmp["多头冻结"]=var["LongFrozen"]
#         tmp["空头冻结"]=var["ShortFrozen"]
#         tmp["开仓量"]=var["OpenVolume"]
#         tmp["平仓量"]=var["CloseVolume"]
#         tmp["开仓金额"]=var["OpenAmount"]
#         tmp["平仓金额"]=var["CloseAmount"]
#         tmp["持仓成本"]=var["PositionCost"]
#         tmp["平仓盈亏"]=var["CloseProfit"]
#         tmp["持仓盈亏"]=var["PositionProfit"]
#         tmp["上次结算价"]=var["PreSettlementPrice"]
#         tmp["本次结算价"]=var["SettlementPrice"]
#         tmp["交易日"]=var["TradingDay"]
#         tmp["开仓成本"]=var["OpenCost"]
#         tmp["今日持仓"]=var["TodayPosition"]
#         return tmp
#
#
#     def order(self, event):
#         data = self.OrderField( event.dict['data'])
#         index =data["报单引用"]#OrderRef
#         if index not in self.dictorder.keys():
#             self.dictorder[index] = data
#         else:
#             self.dictorder[index] = data
#             print('order:',self.dictorder[index])
#
#
#     def OrderField(self, var):
#         tmp = {}
#         tmp["合约代码"] = var["InstrumentID"]
#         tmp["交易所代码"] = var["ExchangeID"]
#         tmp["报单引用"] = var["OrderRef"]
#         tmp["买卖方向"] = var["Direction"]
#         tmp["组合开平标志"] = var["CombOffsetFlag"]
#         tmp["价格"] = var["LimitPrice"]
#         tmp["数量"] = var["VolumeTotalOriginal"]
#         tmp["请求编号"] = var["RequestID"]
#         tmp["本地报单编号"] = var["OrderLocalID"]
#         tmp["报单编号"] = var["OrderSysID"]
#         tmp["今成交数量"] = var["VolumeTraded"]
#         tmp["剩余数量"] = var["VolumeTotal"]
#         tmp["报单日期"] = var["InsertDate"]
#         tmp["委托时间"] = var["InsertTime"]
#         tmp["前置编号"] = var["FrontID"]
#         tmp["会话编号"] = var["SessionID"]
#         tmp["状态信息"] = var["StatusMsg"]
#         tmp["序号"] = var["SequenceNo"]
#         return tmp
#
#     def trader(self, event):
#         data = self.TradeField(event.dict['data'])
#         index = data["报单引用"]  # OrderRef
#         if index not in self.dicttrade.keys():
#             self.dicttrade[index] = data
#             print('trade',data)
#
#     def TradeField(self, var):
#         tmp = {}
#         tmp["合约代码"] = var["InstrumentID"]
#         tmp["报单引用"] = var["OrderRef"]
#         tmp["交易所代码"] = var["ExchangeID"]
#         tmp["成交编号"] = var["TradeID"]
#         tmp["买卖方向"] = var["Direction"]
#         tmp["报单编号"] = var["OrderSysID"]
#         tmp["合约在交易所的代码"] = var["ExchangeInstID"]
#         tmp["开平标志"] = var["OffsetFlag"]
#         tmp["价格"] = var["Price"]
#         tmp["数量"] = var["Volume"]
#         tmp["成交时期"] = var["TradeDate"]
#         tmp["成交时间"] = var["TradeTime"]
#         tmp["本地报单编号"] = var["OrderLocalID"]
#         tmp["交易日"] = var["TradingDay"]
#         return tmp
#
#     def getAccountPosition(self, event):
#         """循环查询账户和持仓"""
#         self.countGet = self.countGet + 1
#         # 每5秒发一次查询
#         if self.countGet > 5:
#             self.countGet = 0  # 清空计数
#
#             if self.lastGet == 'Account':
#                 self.getPosition()
#                 self.lastGet = 'Position'
#             else:
#                 self.getAccount()
#                 self.lastGet = 'Account'
#     def getAccount(self):
#         """查询账户"""
#         self.td.getAccount()
#     # ----------------------------------------------------------------------
#     def getPosition(self):
#         """查询持仓"""
#         self.td.getPosition()
#
#     def buy(self, symbol, price, vol):  # 买开多开
#         self.td.buy(symbol, price, vol)
#
#     def sell(self, symbol, price, vol):  # 多平
#         self.td.sell(symbol, price, vol)
#
#     def selltoday(self, symbol, price, vol):  # 平今多
#
#         self.td.selltoday(symbol, price, vol)
#
#     def short(self, symbol, price, vol):  # 卖开空开
#
#         self.td.short(symbol, price, vol)
#
#     def cover(self, symbol, price, vol):  # 空平
#
#         self.td.cover(symbol, price, vol)
#
#     def covertoday(self, symbol, price, vol):  # 平今空
#
#         self.td.covertoday(symbol, price, vol)
#
#     def cancelOrder(self, order):#撤单
#
#         self.td.cancelOrder(order)
#
#
#
# # 直接运行脚本可以进行测试
# if __name__ == '__main__':
#     import sys
#     # from PyQt5.QtCore import QCoreApplication
#     # app = QCoreApplication(sys.argv)
#     main = MainEngine()
#     main.login()
#     # app.exec_()