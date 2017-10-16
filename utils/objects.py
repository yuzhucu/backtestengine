# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         objects.py
time:         2017/8/30 下午2:44
description: 

'''

__author__ = 'Jimmy'


class Context(object):
    def __init__(self):
        self.portfolio = ''
        self.account = ''
        self.run_info = RunInfo()
        self.universe = []

        # 账户信息
        self.user_id = '008105'
        self.password = '1'
        self.broker_id = '9999'
        self.trade_front = 'tcp://180.168.146.187:10000'

        # self.user_id = '00305188'
        # self.password = 'Jinmi123'
        # self.broker_id = '6000'
        self.market_front = 'tcp://180.168.146.187:10010'
        # self.trade_front = 'tcp://101.231.162.58:41205'

        self.settlementInfo_confirm_flag = False
        # {
        #     'OrderSysID':{
        #         'OrderSysID':'  7152513',
        #         'OrderStatus':'AllTraded',
        #         'OrderRef':'2',
        #         'FrontID':'1',
        #         'SessionID':'1116479594',
        #         'ExchangeID':'SHFE',
        #         'InstrumentID':'rb1801'
        # }
        # }
        # 保存当前下的单 orderStatusType：AllTraded全部成交，Canceled取消时删除
        self.orders = {}

class RunInfo(object):
    def __init__(self):
        self.name = ''
        self.run_id = ''# 标识策略每次运行的唯一id
        self.run_type = '' # RUN_TYPE.BACKTEST表示当前策略在进行回测，RUN_TYPE.PAPER_TRADING表示当前策略在进行实盘模拟
        self.stop_times = ['15:20','23:50']
        self.start_date = ''# 策略的开始日期
        self.end_date = '' # datetime.date    策略的结束日期
        self.frequency = '1T'#策略频率，'1T' 1M' '3M' '5M' 'HM'
        self.starting_cash = 0 # 期货账户初始资金
        self.slippage = 0 # 滑点水平
        self.margin_multiplier = 0 # 保证金倍率
        self.commission_multiplier = 0 # 佣金倍率
        self.benchmark = '' # 基准合约代码
        self.matching_typ = '' # 撮合方式，MATCHING_TYPE.NEXT_BAR_OPEN代表以下一bar开盘价撮合，MATCHING_TYPE.CURRENT_BAR_CLOSE代表以当前bar收盘价撮合

class Portfolios(object):
    def __init__(self):
        self.cash = 0 # 可用资金，为子账户可用资金的加总
        self.frozen_cash = 0 # 冻结资金，为子账户冻结资金加总
        self.total_returns = 0 # 投资组合至今的累积收益率
        self.daily_returns = 0 # 投资组合每日收益率
        self.daily_pnl = 0 # 当日盈亏，子账户当日盈亏的加总
        self.market_value = 0 # 投资组合当前的市场价值，为子账户市场价值的加总
        self.total_value = 0 # 总权益，为子账户总权益加总
        self.units = 0 # 份额。在没有出入金的情况下，策略的初始资金
        self.unit_net_value = 0 # 单位净值
        self.static_unit_net_value = 0 # 静态单位权益
        self.transaction_cost = 0 # 当日费用
        self.pnl = 0 # 当前投资组合的累计盈亏
        self.start_date = '' # 策略投资组合的回测 / 实时模拟交易的开始日期
        self.annualized_returns = 0 # 投资组合的年化收益率
        self.positions = 0 # 一个包含所有仓位的字典，以order_book_id作为键，position对象作为值，关于position的更多的信息可以在下面的部分找到。

class Account(object):
    def __init__(self):
        self.cash = 0 # 可用资金
        self.frozen_cash = 0 # 冻结资金
        self.market_value = 0 # 持仓市值
        self.daily_pnl = 0 # 当日盈亏= 浮动盈亏+平仓盈亏-费用
        self.realized_pnl = 0 # 平仓盈亏
        self.holding_pnl = 0 # 浮动盈亏
        self.total_value = 0 # 总权益
        self.transaction_cost = 0 # 手续费
        self.positions = {} # 持仓字典
        self.margin = 0 # 已占用保证金
        self.buy_margin = 0 # 多头保证金
        self.sell_margin = 0 # 空头保证金


class Positiona(object):
    def __init__(self):
        self.instrument_id = '' #合约代码
        self.pnl = 0 # 累计盈亏
        self.daily_pnl = 0 # 当日盈亏
        self.holding_pnl = 0 # 持仓盈亏
        self.realized_pnl = 0 # 平仓盈亏
        self.transaction_cost = 0 #交易费用
        self.margin = 0 #仓位总保证金
        self.market_value = 0 #当前仓位的名义价值。如果当前净持仓为空方向持仓，则名义价值为负
        self.buy_daily_pnl = 0 #多头仓位当日盈亏
        self.buy_pnl = 0 #多头仓位累计盈亏
        self.buy_transaction_cost = 0 #多头费用
        self.closable_buy_quantity = 0 #可平多头持仓
        self.buy_margin = 0#多头持仓占用保证金
        self.buy_today_quantity = 0 # 多头今仓
        self.buy_quantity = 0 # 多头持仓
        self.buy_avg_open_price = 0 # 多头开仓均价
        self.buy_avg_holding_price = 0 # 多头持仓均价
        self.sell_daily_pnl = 0 # 空头仓位当日盈亏
        self.sell_pnl = 0 # 空头仓位累计盈亏
        self.sell_transaction_cost = 0 # 空头费用
        self.closable_sell_quantity = 0 # 可平空头持仓
        self.sell_margin = 0 # 空头持仓占用保证金
        self.sell_today_quantity = 0 # 空头今仓
        self.sell_quantity = 0 # 空头持仓
        self.sell_avg_open_price = 0 # 空头开仓均价
        self.sell_avg_holding_price = 0 # 空头持仓均价

class Instrument(object):
    def __init__(self):
        self.instrument_id = '' # 期货代码
        self.symbol = '' # 期货的简称，例如
        self.margin_rate = 0 # 期货合约最低保证金率
        self.abbrev_symbol = '' # 期货的名称缩写
        self.listed_date = '' # 期货的上市日期。主力连续合约与指数连续合约都为 '0000-00-00'
        self.contract_multiplier = 0 # 合约乘数，例如沪深300股指期货的乘数为300.0
        self.underlying_symbol = '' # 合约标的名称，例如IF1005的合约标的名称为'IF'
        self.maturity_date = '' # 期货到期日。主力连续合约与指数连续合约都为'0000-00-00'
        self.settlement_method = '' # 交割方式，'CashSettlementRequired' - 现金交割, 'PhysicalSettlementRequired' - 实物交割
        self.product = '' # 产品类型，'Index' - 股指期货, 'Commodity' - 商品期货, 'Government' - 国债期货
        self.exchange = '' # 交易所，'DCE' - 大连商品交易所, 'SHFE' - 上海期货交易所，'CFFEX' - 中国金融期货交易所, 'CZCE' - 郑州商品交易所



class Bar(object):
    def __init__(self,op,cl,high,low):
        self.open = op
        self.close = cl
        self.high = high
        self.low = low


    def __str__(self):
        return 'open: %.2f, close: %.2f, high: %.2f, low: %.2f' %(self.open, self.close, self.high, self.low)


# atr 计算结果
class AtrR(object):
    def __init__(self, unit, n):
        self.unit = unit
        self.n = n

    def __str__(self):
        return 'unit: %d, n: %.2f' %(self.unit, self.n)
# 均线突破结果
class BlR(object):
    def __init__(self, direction, price):
        self.direction = direction
        self.price = price

    def __str__(self):
        return 'direction: %d, price: %.2f' %(self.direction, self.price)

if __name__ == '__main__':
    pass

