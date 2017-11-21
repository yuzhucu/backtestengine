# -*- coding: utf-8 -*-

'''
author:       sjsj
contact:      songjie1217@hotmail.com
file:         backteststrategy.py
time:         2017/9/7 上午午9:02
description:

'''

from backtest.eventengine.eventEngine import *
from backtest.eventengine.eventType import *
from backtest.core.context import *
from backtest.data.getdata import *
from backtest.data.datatype import *
from backtest.data.datatools import *
from backtest.handlers.position import *
from backtest.handlers.portfolio import *
from backtest.tools.tools import *






class BacktestStrategy(object):
    def __init__(self):
        self._engine = EventEngine()
        self._engine.register(EVENT_ON_FEED, self._handle_data)  # 处理tick事件
        # self._engine.register(EVENT_ON_TICK, self._check_unfilled_orders)  # 检查挂单
        self._engine.register(EVENT_ORDER, self._portfolio)  # 执行order事件
        # self._engine.register(EVENT_FILL, self._fill)  # 更新账户持仓...
        self._engine.register(EVENT_AFTER_FILL, self._order_change)
        self._engine.register(EVENT_NEXT_BAR, self._next_bar)
        self._engine.register(EVENT_NEXT_TICK, self._next_tick)
        self._engine.register(EVENT_NEXT_DAY, self._next_day)
        self._engine.register(EVENT_DAY_END, self._handle_dayend)
        self._engine.register(EVENT_OUTPUT, self._handle_output)

        # context里保存所有需要的信息
        self.context = BacktestContext()


    def initialize(self):
        print('you must initilize account')
        raise NotImplementedError


    def handle_data(self, data):
        print('you must write a strategy')
        raise NotImplementedError

    def order_change(self,data):
        pass

    def run(self):
        self._engine.start()
        self.context.timestart = datetime.datetime.now()
        self.initialize()
        date_start_int = datestrtoint(self.context.run_info.start_date)
        date_end_int = datestrtoint(self.context.run_info.end_date)
        datelist = GetTradeDates().get_date_list(date_start_int, date_end_int)  # generate datelist
        # print(datelist)
        trade_days = len(datelist)
        print('交易日共 %d 天' % trade_days)
        self.context.datelist = iter(datelist)  # generate datelist iterator
        self.context.instmt_info = InstmtInfoMongo(symbol=self.context.universe[0]).get_instmt_info()  # get future info
        self.context.portfolio = Portfolio(self.context.init_cash)  # initiate portfolio from init cash
        self.context.portfolio.stats.backtestid = self.context.run_info.strategy_name  # save backtest name to context
        self._next_day()  # start backtest

    def _next_day(self,event={}):
        try:  # run datelist iterator
            date = self.context.datelist.__next__()
            self.context.date = date
            print('日期:%d' %date)
            print(self.context.portfolio.avail_cash)
            self.context.current_contract = self.context.universe
            # print(self.context.run_info.main_contract)
            if self.context.run_info.main_contract:
                self.context.current_contract = self.__get_main_contract(date=date, symbols=self.context.universe, ip=self.context.run_info.ip)
            self.context.portfolio.stats.dates.append(date)
            self.context.settlement_price = TradeDataMongo(self.context.universe[0], date, column=columns,
                                                           ip=self.context.run_info.ip).get_settlement_price() #get settlement price for daily summary

            if len(self.context.universe) == 1:  # handle single instrument
                if self.context.run_info.feed_frequency == 'tick':  # handle tick data
                    data_ticks = self.__get_tick(date, self.context.universe[0],self.context.run_info.ip)  # get tick data
                    self.context.data_day = data_ticks
                    self._next_tick()

                elif self.context.run_info.feed_frequency in ['30s','1m','3m','5m','15m','30m','60m','1d']:  # handle bar data
                    data_bars = self.__get_bar(date, self.context.universe[0], freq=self.context.run_info.feed_frequency,ip=self.context.run_info.ip)
                    self.context.data_day = data_bars
                    self._next_bar()

                else:
                    print("you must specify a data feed type")

            elif len(self.context.universe) > 1: # handle multi instruments
                pass

        except StopIteration:  # when datelist interation ends, start output
            event = Event(EVENT_OUTPUT)
            self._engine.sendEvent(event)

    def _next_bar(self, event={}):  # handles bar feeds
        try:  # start bar interation within day
            row = self.context.data_day.next()
            bar_obj = create_bar_obj(row)  # create bar object
            print(self.context.date, bar_obj.end_time, bar_obj.close)
            self.context.current_bar = bar_obj  # save current bar to context
            event = Event(EVENT_ON_FEED)
            event.dict = bar_obj
            self.context.portfolio.update_portfolio(event.dict.close,time=str(self.context.date)+' '+self.context.current_bar.end_time)  # update portfolio
            self._engine.sendEvent(event)
        except StopIteration:  # when bar interation ends, start day end process
            event =Event(EVENT_DAY_END)
            self._engine.sendEvent(event)
           # sleep(0.1)

    def _next_tick(self, event={}):  # handles tick feeds
        try:  # start bar interation within day
            row = self.context.data_day.next()
            self.context.current_tick = row # save current bar to context
            event = Event(EVENT_ON_FEED)
            event.dict = row
            self.context.portfolio.update_portfolio(event.dict['LastPrice'])  # update portfolio
            self._engine.sendEvent(event)
        except StopIteration:  # when bar interation ends, start day end process
            event =Event(EVENT_DAY_END)
            self._engine.sendEvent(event)

    def _handle_data(self, event):
        self.handle_data(event.dict)
        if not self.context.order_flag: # 若未产生交易，发送下一个数据
            if self.context.run_info.feed_frequency == 'tick':
                event = Event(EVENT_NEXT_BAR)
                self._engine.sendEvent(event)
            else:
                event = Event(EVENT_NEXT_BAR)
                self._engine.sendEvent(event)
        else:  # if order_flag, order itself will send move on signal
            pass

    def order(self, instrument_id, direction, offset, vol, limit_price=0, stop_price=0, contingent_condition='immediately'):

        '''
        下单
        :param instrument_id:           合约id: 如'rb1801'
        :param direction:               DirectionType.买:Buy  卖:Sell
        :param offset:                  OffsetFlagType.开:Open.__char__() 平:Close.__char__() 平今:CloseToday.__char__() 平昨:CloseYesterday__char__()
        :param vol:                     数量
        :param limit_price:             限价为0则为市价单 不为0则为限价单
        :param stop_price:              止损价为0则挂单条件为立即触发
        :param contingent_condition:    触发条件 默认立即 可设置stop条件
        :return:
        '''
        self.context.order_flag = True  # 更改order flag
        price_type = 'limit'
        if limit_price == 0:
            price_type = 'any'

        order = {}

        order['symbol'] = instrument_id
        order['direction'] = direction
        order['offset'] = offset
        order['vol'] = vol
        order['limit_price'] = limit_price
        order['stop_price'] = stop_price
        order['stop_type'] = contingent_condition
        order['status'] = ''
        order['slippage'] = 0

        event = Event(EVENT_ORDER)

        event.dict = order
        # print(self.context.current_data['endTime'])
        # print(event.dict)
        print("beforesend %s:" %datetime.datetime.now(),2)
        self._engine.sendEvent(event)

    def _portfolio(self, event):
        order = event.dict
        if self.context.instmt_info['commission_type'] == 'vol':
            comm_o = self.context.instmt_info['opening_fee_by_num']
            comm_t = self.context.instmt_info['closing_today_fee_by_num']
            comm_y = self.context.instmt_info['closing_fee_by_num']
        else:
            comm_o = self.context.instmt_info['opening_fee_by_value']
            comm_t = self.context.instmt_info['closing_today_fee_by_value']
            comm_y = self.context.instmt_info['closing_fee_by_value']

        margin = self.context.instmt_info['broker_margin']/100
        contract_size = self.context.instmt_info['contract_size']
        exch_code = self.context.instmt_info['exch_code']
        time = self.context.current_bar.end_time
        date = self.context.date
        print('receive order %s:' %datetime.datetime.now(),3)
        # print('order direction:%s offset:%s vol:%d price:%d date:%d time:%s' %
        #       (order.direction,order.offset,order['vol'],order.limit_price,date,time))
        if order['direction'] == BUY and order['offset'] == OPEN:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='long', offset='open',
                                                   vol=order['vol']*contract_size, price=order['limit_price'],
                                                   marginratio=margin, comm_o=comm_o, comm_t=comm_t, comm_y=comm_y,
                                                   time=time, date=date, exch_code=exch_code,info=self.context.instmt_info)

        elif order['direction']  == SELL and order['offset'] == OPEN:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='short', offset='open',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time,date=date, exch_code=exch_code,info=self.context.instmt_info)

        elif order['direction']  == BUY and order['offset'] == CLOSE:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='short', offset='close',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time, date=date, exch_code=exch_code)

        elif order['direction']  == BUY and order['offset'] == CLOSE_T:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='short', offset='close_t',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time,date=date, exch_code=exch_code)

        elif order['direction']  == BUY and order['offset'] == CLOSE_Y:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='short', offset='close_y',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time,date=date, exch_code=exch_code)

        elif order['direction']  == SELL and order['offset'] == CLOSE:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='long', offset='close',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time,date=date, exch_code=exch_code)

        elif order['direction']  == SELL and order['offset'] == CLOSE_T:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='long', offset='close_t',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time,date=date, exch_code=exch_code)

        elif order['direction']  == SELL and order['offset'] == CLOSE_Y:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='long', offset='close_y',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time,date=date, exch_code=exch_code)
        # else:
        #     # 撤单
        #     pass
        print(
            'after trade: curtime:%s, curprice:%.2f,total:%d, marginreq:%d, avalcash:%d,upnl:%d,daypnl:%d,daycomm:%d,prebalance:%d' % (
                self.context.current_bar.end_time,
                self.context.current_bar.close,
                self.context.portfolio.total_value, self.context.portfolio.marginreq,
                self.context.portfolio.avail_cash, self.context.portfolio.upnl,
                self.context.portfolio.dailypnl,
                self.context.portfolio.dailycomm,
                self.context.portfolio.pre_balance))
        event = Event(EVENT_AFTER_FILL)
        event.dict = order
        self._engine.sendEvent(event)


    def _order_change(self,event):
        self.order_change(event.dict)
        self.context.order_flag = False
        event = Event(EVENT_NEXT_BAR)
        self._engine.sendEvent(event)


    def _handle_dayend(self,event={}):
        self.context.portfolio.dayend_summary(date=self.context.date,
                                              settlement_price=self.context.settlement_price)
        # print(self.context.date)
        self.context.portfolio.combine_portfolio_dayend()
        print(self.context.portfolio.positions)
        # print(self.context.date)
        event = Event(EVENT_NEXT_DAY)
        self._engine.sendEvent(event)


    def _handle_output(self, event={}):
        self.context.portfolio.stats.nv = np.array(self.context.portfolio.netvalue)
        self.context.portfolio.stats.datetime = self.context.portfolio.datetime
        self.context.portfolio.stats.kdj = self.context.kdjls
        # print(self.context.portfolio.stats.nv)
        self.context.portfolio.stats.output()

        timeend = datetime.datetime.now()
        timespend = timeend - self.context.timestart
        print('回测共耗时%s' % timespend)

        self._engine.stop()
        return self.context.portfolio.stats




    def _fill(self, event): #增加风控模块后调用
        pass

    def cancel_order(self, order):
        order = Order()
        order.cancel_flag = True

        # 发送执行order事件
        event = Event(EVENT_FILL)
        event.dict = order
        self._engine.sendEvent(event)

    # 更新持仓。。。


    # 生成滑点
    def stop(self):
        self._engine.stop()

    # 获取tick
    def __get_tick(self, date, symbol,ip):
        if self.context.datasource == 'mongo':
            tick = TradeDataMongo(symbol=symbol, date=date,column=miniclms, ip=ip).get_tick_data()  # 数据库取某天的tick
        elif self.context.datasource == 'csv':
            tick = GetDataCSV(symbol + '-' + date + '.csv').get_tick()
        return tick

    def __get_ticks_dict(self, date, symbols,ip):
        ticks = {}
        for symbol in symbols:
            ticks[symbol] = self.__get_tick(date, symbol,ip)
        return ticks

    def __get_bar(self, date, symbol, freq,ip):
        bar = {}
        if self.context.datasource == 'mongo':
            bar = TradeDataMongo(symbol=symbol, date=date, column=miniclms, ip=ip).get_bar_data(freq=freq)  # 数据库取某天的tick
        elif self.context.datasource == 'csv':
            bar = GetDataCSV(symbol + '-' + date + '.csv').get_tick()
        return bar

    def __get_bars_dict(self, date, symbols,ip):
        bars = {}
        for symbol in symbols:
            bars[symbol] = self.__get_bar(date, symbol,ip)
        return bars

    def __get_main_contract(self, date, symbols, ip):
        main_contract = []
        if self.context.datasource == 'mongo':
            for symbol in symbols:
                main_contract.append(TradeDataMongo(symbol=symbol, date=date, column=miniclms, ip=ip).get_main_contract())  # 数据库取某天的tick
        elif self.context.datasource == 'csv':
            pass
        return main_contract