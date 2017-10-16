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

# start = '2012-02-01'
# end = '2012-02-03'

# print(get_date_list(start,end))
# # print(strtoint('2012-02-01'))

def instidtoprodid (instid):
    prodid = ''
    for i in instid:
        if i.isalpha():
            prodid += i
    return prodid