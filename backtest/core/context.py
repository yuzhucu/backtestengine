# -*- coding: utf-8 -*-

'''
author:       sjsj
contact:      234390130@qq.com
file:         mainEngine.py
time:         2017/9/7 上午午9:02
description:

'''

from backtest.handlers.portfolio import *
from backtest.handlers.position import *
from backtest.handlers.order import *
from backtest.analyzer.analyzer import *
from backtest.data.datatype import *

class BacktestContext(object):
    def __init__(self):
        self.unfilled_orders = []
        self.account = Account()
        self.init_cash = 0
        self.positions = []
        self.portfolio = Portfolio(0)
        self.stats = Stats()
        self.run_info = RunInfo()
        self.trade_history = []
        self.universe = []
        self.datasource = 'mongo'
        self.instmt_info = {}
        self.current_tick = {}
        self.current_bar = Bar()
        self.settlement_price = 0
        self.date = ''
        self.data_day = {}
        self.order_flag = False
        self.datelist = {}
        self.timestart=""

class RunInfo(object):
    def __init__(self):
        self.strategy_name = ''
        self.run_id = ''  # 标识策略每次运行的唯一id
        self.run_type = ''  # RUN_TYPE.BACKTEST表示当前策略在进行回测，RUN_TYPE.PAPER_TRADING表示当前策略在进行实盘模拟
        self.start_date = ''  # 策略的开始日期
        self.end_date = ''  # datetime.date    策略的结束日期
        self.feed_frequency = ''  #策略频率，'1d' '1m' '1t
        self.ip = localip
        self.starting_cash = 0 # 期货账户初始资金
        self.slippage = 0  # 滑点水平
        self.benchmark = ''  # 基准合约代码

class Account(object):
    def __init__(self):
        self.cash = 0  # 可用资金
        self.frozen_cash = 0  # 冻结资金
        self.market_value = 0  # 持仓市值
        self.daily_pnl = 0  # 当日盈亏= 浮动盈亏+平仓盈亏-费用
        self.realized_pnl = 0  # 平仓盈亏
        self.holding_pnl = 0  # 浮动盈亏
        self.total_value = 0  # 总权益
        self.transaction_cost = 0  # 手续费
        self.margin = 0  # 已占用保证金
        self.buy_margin = 0  # 多头保证金
        self.sell_margin = 0  # 空头保证金

# class Portfolio(object):
#     def __init__(self):
#         self.cash = 0 # 可用资金，为子账户可用资金的加总
#         self.frozen_cash = 0 # 冻结资金，为子账户冻结资金加总
#         self.total_returns = 0 # 投资组合至今的累积收益率
#         self.daily_returns = 0 # 投资组合每日收益率
#         self.daily_pnl = 0 # 当日盈亏，子账户当日盈亏的加总
#         self.market_value = 0 # 投资组合当前的市场价值，为子账户市场价值的加总
#         self.total_value = 0 # 总权益，为子账户总权益加总
#         self.units = 0 # 份额。在没有出入金的情况下，策略的初始资金
#         self.unit_net_value = 0 # 单位净值
#         self.static_unit_net_value = 0 # 静态单位权益
#         self.transaction_cost = 0 # 当日费用
#         self.pnl = 0 # 当前投资组合的累计盈亏
#         self.start_date = '' # 策略投资组合的回测 / 实时模拟交易的开始日期
#         self.annualized_returns = 0 # 投资组合的年化收益率
#         self.positions = [] # 一个包含所有仓位的字典，以order_book_id作为键，position对象作为值，关于position的更多的信息可以在下面的部分找到。

# class Position(object):
#     def __init__(self):
#         self.instrument_id = '' #合约代码
#         self.pnl = 0 # 累计盈亏
#         self.daily_pnl = 0 # 当日盈亏
#         self.holding_pnl = 0 # 持仓盈亏
#         self.realized_pnl = 0 # 平仓盈亏
#         self.transaction_cost = 0 #交易费用
#         self.margin = 0 #仓位总保证金
#         self.market_value = 0 #当前仓位的名义价值。如果当前净持仓为空方向持仓，则名义价值为负
#         self.buy_daily_pnl = 0 #多头仓位当日盈亏
#         self.buy_pnl = 0 #多头仓位累计盈亏
#         self.buy_transaction_cost = 0 #多头费用
#         self.closable_buy_quantity = 0 #可平多头持仓
#         self.buy_margin = 0#多头持仓占用保证金
#         self.buy_today_quantity = 0 # 多头今仓
#         self.buy_quantity = 0 # 多头持仓
#         self.buy_avg_open_price = 0 # 多头开仓均价
#         self.buy_avg_holding_price = 0 # 多头持仓均价
#         self.sell_daily_pnl = 0 # 空头仓位当日盈亏
#         self.sell_pnl = 0 # 空头仓位累计盈亏
#         self.sell_transaction_cost = 0 # 空头费用
#         self.closable_sell_quantity = 0 # 可平空头持仓
#         self.sell_margin = 0 # 空头持仓占用保证金
#         self.sell_today_quantity = 0 # 空头今仓
#         self.sell_quantity = 0 # 空头持仓
#         self.sell_avg_open_price = 0 # 空头开仓均价
#         self.sell_avg_holding_price = 0 # 空头持仓均价

# class Order(object):
#     def __init__(self):
#         self.symbol = ''
#         self.direction = ''
#         self.offset = ''
#         self.vol = 0
#         self.limit_price = 0
#         self.stop_price = 0
#         self.stop_type = ''
#         self.status = 0
#         self.slippage = 0
#
#

#
#
# class DailySummary(object):
#     def __init__(self):
#         self.date = ''
#         self.equity = 0
#         self.cash = 0
#         self.positions = []
#         self.upnl = 0
#         self.pnl = 0
#
# class Instrument(object):
#     def __init__(self):
#         self.instrument_id = '' # 期货代码
#         self.symbol = '' # 期货的简称，例如
#         self.margin_rate = 0 # 期货合约最低保证金率
#         self.abbrev_symbol = '' # 期货的名称缩写
#         self.listed_date = '' # 期货的上市日期。主力连续合约与指数连续合约都为 '0000-00-00'
#         self.contract_multiplier = 0 # 合约乘数，例如沪深300股指期货的乘数为300.0
#         self.underlying_symbol = '' # 合约标的名称，例如IF1005的合约标的名称为'IF'
#         self.maturity_date = '' # 期货到期日。主力连续合约与指数连续合约都为'0000-00-00'
#         self.settlement_method = '' # 交割方式，'CashSettlementRequired' - 现金交割, 'PhysicalSettlementRequired' - 实物交割
#         self.product = '' # 产品类型，'Index' - 股指期货, 'Commodity' - 商品期货, 'Government' - 国债期货
#         self.exchange = '' # 交易所，'DCE' - 大连商品交易所, 'SHFE' - 上海期货交易所，'CFFEX' - 中国金融期货交易所, 'CZCE' - 郑州商品交易所