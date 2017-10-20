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
    return prodid

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