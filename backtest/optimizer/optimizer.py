# encoding: utf-8


"""
@version: python3.6
@author: ‘sj‘
@contact: songjie1217@hotmail.com
@file: optimizer.py
@time: 10/20/17 10:06 PM
"""
from backtest.eventengine.eventEngine import *
from backtest.eventengine.eventType import *
from backtest.core.context import *
from backtest.data.getdata import *
from backtest.data.datatype import *
from backtest.data.datatools import *
from backtest.handlers.position import *
from backtest.handlers.portfolio import *
from backtest.tools.tools import *
from backtest.tools.ta import *



class Optimizer(object):
    def __init__(self):
        self.target_func = ''

class StrategyCompareDay(object):

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
        # self.context.run_info = RunInfo()


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
        self.context.portfolio = Portfolio(self.context.init_cash)  # initiate portfolio from init cash
        self.context.portfolio.stats.backtestid = self.context.run_info.strategy_name  # save backtest name to context
        self._next_day()  # start backtest

    def _next_day(self,event={}):
        try:  # run datelist iterator
            date = self.context.datelist.__next__()
            self.context.date = date
            print('日期:%d' %date)
            self.context.portfolio.stats.dates.append(date)
            self.context.current_contract = self.context.universe
            if self.context.run_info.main_contract:
                self.context.current_contract = self.__get_main_contract(date=date, symbols=self.context.universe, ip=self.context.run_info.ip)


            if len(self.context.universe) == 1:  # handle single instrument
                self.context.instmt_info = InstmtInfoMongo(
                    symbol=self.context.current_contract[0]).get_instmt_info()  # get future info
                self.context.settlement_price = TradeDataMongo(self.context.current_contract[0], date, column=columns,
                                                               ip=self.context.run_info.ip).get_settlement_price()  # get settlement price for daily summary

                if self.context.run_info.feed_frequency == 'tick':  # handle tick data
                    data_ticks = self.__get_tick(date, self.context.current_contract[0],ip=self.context.run_info.ip)  # get tick data
                    self.context.data_day = data_ticks
                    self._next_tick()

                elif self.context.run_info.feed_frequency in ['30s','1m','3m','5m','15m','30m','60m','1d']:  # handle bar data
                    data_bars = self.__get_bar(date, self.context.current_contract[0], freq=self.context.run_info.feed_frequency,ip=self.context.run_info.ip)
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
            # print(self.context.date, bar_obj.end_time, bar_obj.close)
            self.context.current_bar = bar_obj  # save current bar to context
            event = Event(EVENT_ON_FEED)
            event.dict = bar_obj
            self.context.portfolio.update_portfolio(event.dict.close,time=str(self.context.date)+' '+self.context.current_bar.end_time)  # update portfolio
            self._engine.sendEvent(event)
        except StopIteration:  # when bar interation ends, start day end process
            # self.context.portfolio
            event = Event(EVENT_DAY_END)
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
            event = Event(EVENT_DAY_END)
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

    def order(self, instrument_id, direction, offset, vol, limit_price=0, stop_price=0, contingent_condition='immediately',type = '',max_dev=0):

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

        event = Event(EVENT_ORDER)

        event.dict = {
            # 'tick':self.context.current_tick,
            'symbol': instrument_id,
            'vol': vol,
            'limit_price': limit_price,
            'pricetype': price_type,
            'direction': direction,
            'offset': offset,
            'stop_price': stop_price,
            'contingent_condition': contingent_condition,
            'type': type,
            'max_dev': max_dev
            # 'cancel_flag': False
        }
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
        #       (order['direction'],order['offset'],order['vol'],order['limit_price'],date,time))
        if order['direction'] == BUY and order['offset'] == OPEN:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='long', offset='open',
                                                   vol=order['vol']*contract_size, price=order['limit_price'],
                                                   marginratio=margin, comm_o=comm_o, comm_t=comm_t, comm_y=comm_y,
                                                   time=time, date=date, exch_code=exch_code,info=self.context.instmt_info)

        elif order['direction'] == SELL and order['offset'] == OPEN:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='short', offset='open',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time,date=date, exch_code=exch_code,info=self.context.instmt_info)

        elif order['direction'] == BUY and order['offset'] == CLOSE:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='short', offset='close',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time,date=date, exch_code=exch_code,type=order['type'],max_dev=order['max_dev'])

        elif order['direction'] == BUY and order['offset'] == CLOSE_T:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='short', offset='close_t',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time,date=date, exch_code=exch_code,type=order['type'],max_dev=order['max_dev'])

        elif order['direction'] == BUY and order['offset'] == CLOSE_Y:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='short', offset='close_y',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time,date=date, exch_code=exch_code,type=order['type'],max_dev=order['max_dev'])

        elif order['direction'] == SELL and order['offset'] == CLOSE:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='long', offset='close',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time,date=date, exch_code=exch_code,type=order['type'],max_dev=order['max_dev'])

        elif order['direction'] == SELL and order['offset'] == CLOSE_T:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='long', offset='close_t',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time,date=date, exch_code=exch_code,type=order['type'],max_dev=order['max_dev'])

        elif order['direction'] == SELL and order['offset'] == CLOSE_Y:
            self.context.portfolio.modify_position(symbol=order['symbol'], direction='long', offset='close_y',
                                                   vol=order['vol'] * contract_size, price=order['limit_price'],
                                                   marginratio=margin,
                                                   comm_o=comm_o, comm_t=comm_t, comm_y=comm_y, time=time,date=date, exch_code=exch_code,type=order['type'],max_dev=order['max_dev'])
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


    def _order_change(self, event):
        self.order_change(event.dict)
        self.context.order_flag = False
        event = Event(EVENT_NEXT_BAR)
        self._engine.sendEvent(event)


    def _handle_dayend(self, event={}):
        self.context.portfolio.dayend_summary(date=self.context.date,
                                              settlement_price=self.context.current_bar.close)
        print(self.context.date)

        self.context.portfolio.stats.nv = np.array(self.context.portfolio.netvalue)
        self.context.comparision.datelst.append(self.context.date)
        self.context.comparision.dayend_value.append(self.context.portfolio.total_value)
        self.context.comparision.simplereturn.append(self.context.portfolio.stats.returns('simple', 'def'))
        self.context.comparision.logreturn.append(self.context.portfolio.stats.returns('log', 'def'))
        self.context.comparision.volit.append(self.context.portfolio.stats.volatility())
        self.context.comparision.maxdd.append(self.context.portfolio.stats.maxdd())
        self.context.comparision.sharpe.append(self.context.portfolio.stats.sharpe())
        self.context.comparision.totalcommission.append(self.context.portfolio.totalcomm)
        self.context.comparision.tradecount.append(self.context.portfolio.tradecount)
        self.context.comparision.net_profit.append(self.context.portfolio.total_value-self.context.init_cash)
        self.context.comparision.trans += self.context.portfolio.stats.transactions

        #
        # self.context.direction = ''
        # self.context.open_vol = 0 # 当前开仓手数
        # self.context.open_flag = False # false表示没有开仓 true表示已经开仓了
        # self.context.can_open_flag = True # ture 表示能继续开仓 flase 表示已经开足仓了
        # self.context.close_count = 0 # 平仓计数器
        # self.context.boll =Boll()
        # self.context.open_price = 0

        self.initialize()

        self.context.portfolio = Portfolio(init_cash=self.context.init_cash)
        event = Event(EVENT_NEXT_DAY)
        self._engine.sendEvent(event)


    def _handle_output(self, event={}):
        outputwb = xlwt.Workbook()
        dayend = outputwb.add_sheet('dayend')
        transdetail = outputwb.add_sheet('transactions')

        profit = np.array(self.context.comparision.net_profit)
        avg_profit = np.mean(profit)
        std_profit = np.std(profit)

        n = len(profit)
        count_gain = 0
        for i in self.context.comparision.net_profit:
            if i >0:
                count_gain += 1

        count_loss = n - count_gain


        dayend.write(0, 0, 'date')
        dayend.write(0, 1, 'value')
        dayend.write(0, 2, 'simple_return')
        dayend.write(0, 3, 'log_return')
        dayend.write(0, 4, 'volitility')
        dayend.write(0, 5, 'maxdd')
        dayend.write(0, 6, 'sharpe')
        dayend.write(0, 7, 'total_commission')
        dayend.write(0, 8, 'trade_count')
        dayend.write(0, 9, 'net_profit')

        dayend.write(1, 11, 'average_profit')
        dayend.write(2, 11, 'std_profit')
        dayend.write(3, 11, 'days_total')
        dayend.write(4, 11, 'days_gain')
        dayend.write(5, 11, 'days_loss')

        dayend.write(1, 12, avg_profit)
        dayend.write(2, 12, std_profit)
        dayend.write(3, 12, n)
        dayend.write(4, 12, count_gain)
        dayend.write(5, 12, count_loss)


        for i in range(0, len(self.context.comparision.datelst)):
            dayend.write(i+1, 0, self.context.comparision.datelst[i])
            dayend.write(i+1, 1, self.context.comparision.dayend_value[i])
            dayend.write(i+1, 2, self.context.comparision.simplereturn[i])
            dayend.write(i+1, 3, self.context.comparision.logreturn[i])
            dayend.write(i+1, 4, self.context.comparision.volit[i])
            dayend.write(i+1, 5, self.context.comparision.maxdd[i])
            dayend.write(i+1, 6, self.context.comparision.sharpe[i])
            dayend.write(i+1, 7, self.context.comparision.totalcommission[i])
            dayend.write(i+1, 8, self.context.comparision.tradecount[i])
            dayend.write(i+1, 9, self.context.comparision.net_profit[i])

        transdetail.write(0, 0, 'index')
        transdetail.write(0, 1, 'date')
        transdetail.write(0, 2, 'time')
        transdetail.write(0, 3, 'symbol')
        transdetail.write(0, 4, 'direction')
        transdetail.write(0, 5, 'offset')
        transdetail.write(0, 6, 'price')
        transdetail.write(0, 7, 'volume')
        transdetail.write(0, 8, 'commission')
        transdetail.write(0, 9, 'realized gain/loss')
        transdetail.write(0, 10, 'max_dev')
        transdetail.write(0, 11, 'type')

        for i in range(0, len(self.context.comparision.trans)):
            trans = self.context.comparision.trans[i]
            transdetail.write(i + 1, 0, i)
            transdetail.write(i + 1, 1, trans.date)
            transdetail.write(i + 1, 2, trans.time)
            transdetail.write(i + 1, 3, trans.symbol)
            transdetail.write(i + 1, 4, trans.direction)
            transdetail.write(i + 1, 5, trans.offset)
            transdetail.write(i + 1, 6, trans.price)
            transdetail.write(i + 1, 7, trans.vol)
            transdetail.write(i + 1, 8, trans.commission)
            transdetail.write(i + 1, 9, trans.pnl)
            transdetail.write(i + 1, 10, trans.max_dev)
            transdetail.write(i + 1, 11, trans.type)

        outputwb.save(self.context.run_info.strategy_name + '-'+ str(self.context.comparision.datelst[0]) + '-'
                      + str(self.context.comparision.datelst[-1]) + '-backtest-comp' + '.xls')

        timeend = datetime.datetime.now()
        timespend = timeend - self.context.timestart
        print('回测共耗时%s' % timespend)

        self._engine.stop()





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
    def __get_tick(self, date, symbol, ip):
        tick={}
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

    def __get_bar(self, date, symbol, freq, ip):
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