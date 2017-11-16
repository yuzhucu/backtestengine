import datetime


def strtodate(datestr):
    return datetime.datetime.strptime(datestr,'%Y-%m-%d')

def datestrtoint(datestr):
    strt = datestr[:4]+datestr[5:7]+datestr[8:10]
    return int(strt)

def getabr(symbol):
    return symbol[:-4]


def get_date_list_range(start,end):
    datestart = datetime.datetime.strptime(start, '%Y-%m-%d')
    dateend = datetime.datetime.strptime(end, '%Y-%m-%d')
    datelist = [start]
    while datestart < dateend:
        datestart += datetime.timedelta(days=1)
        datelist.append(datestart.strftime('%Y-%m-%d'))
    return datelist



def combinedaytime(tradeday,updatetime,updatemilisec):
    return (str(tradeday)[0:4] + '-' + str(tradeday)[4:6] + '-' + str(tradeday)[6:8] + ' ' + updatetime+ ' '+str(updatemilisec))


def instidtoprodid (instid):
    prodid = ''
    for i in instid:
        if i.isalpha():
            prodid += i
    return prodid.lower()


# print(instidtoprodid('RB801'))

def ticktobar (tick):   #takes tick cursor object and transfer it to iter bar event
    templs = []
    timeflag = []
    bardict = {
        'TradingDay':[],
        'CloseTime':[],
        'Open':[],
        'Close':[],
        'High':[],
        'Low':[],
        'Volume':[],
        'curVol':[]
    }
    for row in tick:
        templs.append(row['LastPrice'])
        timeflag.append(row['UpdateTime'][4])
        try:
            if int(timeflag[-1]) != int(timeflag[1]):
                bardict['TradingDay'].append(row['TradingDay'])
                bardict['CloseTime'].append(row['UpdateTime'])
                bardict['Open'].append(templs[0])
                bardict['Close'].append(templs[-1])
                bardict['High'].append(max(templs))
                bardict['Low'].append(min(templs))
                bardict['Volume'].append(row['Volume'])
                templs =[]
                timeflag=[]
            else:
                pass
        except:
            pass

        bardict['curVol'] = bardict['Volume'].copy()
        for i in range(1,len(bardict['Volume'])):
            bardict['curVol'][i] = bardict['Volume'][i] - bardict['Volume'][i-1]

    return bardict


def convert_time(stoptimes):
    if len(stoptimes) != 2:
        return []
    else:
        st_day = int(stoptimes[0].split(':')[0]) * 60 + int(stoptimes[0].split(':')[-1])
        st_night = int(stoptimes[-1].split(':')[0]) * 60 + int(stoptimes[-1].split(':')[-1])
        return [st_day, st_night]

def calculate_stop(stoptimes):
    flag = False
    now = datetime.datetime.now()
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


class TickConver(object):
    def __init__(self, symbol, data_frequency = '1T'):
        self._symbol = symbol
        self._tick_prices = []
        self._begin_time = ''
        self._trading_day = ''
        self._vol_begin = 0
        self._vol_update = 0
        self.__option = self._compute_bar_option(data_frequency)
        self._bar_period = self.__option['period']
        self._bar_type = self.__option['type']
        self._night_close_time = self._get_night_close_time(symbol)


    def tick_to_bar(self, tick):
        # tick updatatime 合法
        if self._check_tick(tick) :
            # tick数量类型bar
            if self._bar_type == 'T':
                if self._bar_period == 1:
                    return tick
                else:
                    bar_length = len(self._tick_prices)
                    if bar_length == 0:
                        self._vol_begin = int(tick['Volume'])

                    if bar_length < self._bar_period:
                        self._tick_prices.append(tick['LastPrice'])
                        self._begin_time = tick['UpdateTime']
                        return None
                    elif bar_length == self._bar_period:
                        # 由于tick是快照,下一个bar的第一个tick计算到上一个bar中,保证bar连续
                        self._tick_prices.append(tick['LastPrice'])
                        vol = int(tick['Volume']) - self._vol_begin
                        arr = np.array(self._tick_prices)
                        bar = Bar(self._symbol, self._tick_prices[0], self._tick_prices[-1], arr.max(), arr.min(),
                                  trading_day=tick['TradingDay'], begin_time=self._begin_time,
                                  end_time=tick['UpdateTime'], vol=vol, tick_counter=bar_length + 1)
                        self._tick_prices = []
                        self._tick_prices.append(tick['LastPrice'])

                        return bar
            # 时间间隔类 bar
            elif self._bar_type == 'M':
                bar_length = len(self._tick_prices)
                if bar_length == 0:
                    self._init_first_tick_of_bar(tick)
                    return None
                else:
                    time_space = self._compute_time_space()
                    if self._compute_time_delta(self._trading_day, tick['UpdateTime'],
                                                self._begin_time) >= self._bar_period * 60 + time_space:
                        # 由于tick是快照,下一个bar的第一个tick计算到上一个bar中,保证bar连续
                        self._tick_prices.append(tick['LastPrice'])
                        self._vol_update = int(tick['Volume'])

                        vol = abs(self._vol_update - self._vol_begin)
                        arr = np.array(self._tick_prices)
                        bar = Bar(self._symbol, self._tick_prices[0], self._tick_prices[-1], arr.max(), arr.min(),
                                  trading_day=tick['TradingDay'], begin_time=self._begin_time,
                                  end_time=tick['UpdateTime'], vol=vol, tick_counter=len(self._tick_prices))
                        self._tick_prices = []
                        self._init_first_tick_of_bar(tick)
                        return bar
                    else:
                        self._tick_prices.append(tick['LastPrice'])
                        self._vol_update = int(tick['Volume'])
                        return None
        else:
            return None


    def _init_first_tick_of_bar(self, tick):
        self._tick_prices.append(tick['LastPrice'])
        self._trading_day = tick['TradingDay']
        self._begin_time = tick['UpdateTime']
        self._vol_begin = int(tick['Volume'])

    # 计算时间差  跨00:00:00的时间差计算需加1天后计算
    def _compute_time_delta(self, trading_day, update_time, compare_time):
        ut_year = ct_year = int(trading_day[0:4])
        ut_month = ct_month = int(trading_day[4:6])
        ut_day = ct_day = int(trading_day[6:8])

        uts = update_time.split(':')
        cts = compare_time.split(':')

        ut = dt(ut_year, ut_month, ut_day, int(uts[0]), int(uts[1]), int(uts[2]))
        # ct = dt(ct_year, ct_month, ct_day, int(cts[0]), int(cts[1]), int(cts[2]))
        # begin_time 秒位置为0参与计算 防止出现9:23:06 - 9:20:06 但实际应为 9:23:06-9:20:00
        ct = dt(ct_year, ct_month, ct_day, int(cts[0]), int(cts[1]), 0)

        if int(uts[0]) < 3:
            ut = ut + dtm.timedelta(days=1)
        if int(cts[0]) < 3:
            ct = ct + dtm.timedelta(days=1)

        return (ut - ct).seconds

    # 计算bar类型  1.按Tick数量组成bar  2.按时间周期组成bar
    def _compute_bar_option(self, data_frequency):
        return {'period': int(''.join(list(filter(str.isdigit, data_frequency)))), 'type': data_frequency[-1]}

    # 计算交易节点间隔 按秒计算
    def _compute_time_space(self):
        # print(self._night_close_time)
        if self._bar_period == 1 or self._night_close_time == None:
            return 0
        else:
            temp = self._begin_time.split(':')
            beg_timestamp = int(temp[0]) * 3600 + int(temp[1]) * 60 + int(temp[2])
            end_timestamp = beg_timestamp + self._bar_period * 60

            if beg_timestamp <= self._night_close_time < end_timestamp:
                if self._night_close_time < 10800:
                    return 32400 - self._night_close_time
                else:
                    return 86400 -self._night_close_time + 32400

            elif beg_timestamp <= 36900 < end_timestamp:
                return 900
            elif beg_timestamp <= 41400 < end_timestamp:
                return 7200
            else:
                return 0

    # 检查tick是否有效  => 是否在时间范围内 比如8：59：59, 15:00:01 ,23:30:01...均为不合法tick 不计入bar
    def _check_tick(self, tick):
        tick_timestamp = self._time_to_int(tick['UpdateTime'])
        flag = True

        # 11:30:00 ~ 13:30:00  15:00:00 ~ 21:00:00
        if 41400 < tick_timestamp < 48600 or 54000 < tick_timestamp < 75600:
            flag = False

        # 收盘时间 < 3:00
        if self._night_close_time < 10800:
            # 2:30:00 ~ 9:00:00
            if self._night_close_time < tick_timestamp < 32400:
                flag = False
        else:
            # 23:00:00 ~ 24:00:00
            if self._night_close_time < tick_timestamp < 86400:
                flag = False
            # 00:00:00 ~ 9:00:00
            elif 0 < tick_timestamp < 32400:
                flag = False
        return flag


    # 获取夜盘收盘时间
    def _get_night_close_time(self, symbol):
        db = bs.SharedDatabase.futuresDatabase
        symbol_code = tl.symbol_to_code(symbol)
        result = db.future_info.find({'instrument_code':symbol_code})
        try:
            res = result.next()
            night_close_time = res['night_close_time']
            temp = night_close_time.split(':')
            return int(temp[0]) * 3600 + int(temp[1]) * 60 + int(temp[2])
        except StopIteration:
            return None


    def _time_to_int(self, tm):
        temp = tm.split(':')
        return int(temp[0]) * 3600 + int(temp[1]) * 60 + int(temp[2])


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