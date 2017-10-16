# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         storage.py
time:         2017/9/4 下午3:18
description: 

'''

__author__ = 'Jimmy'


import pymongo
from ctp.ctp_struct import *
from bson import json_util as jsonb
from utils.tools import *


def _getDataBase():
    client = pymongo.MongoClient(host='127.0.0.1', port=27017)
    return client.trade


# 报单回报 OnRtnOrder
def insertRtnOrder(event):
    db = _getDataBase()
    dict = getStrategyInfo(event.dict)
    db.order.insert(dict)


# 报单操作 OnErrRtnOrderAction
def insertErrRtnOrderAction(event):
    db = _getDataBase()
    dict = getStrategyInfo(event.dict)
    db.order_action.insert(dict)


# 输入报单操作 OnRspOrderAction
def insertRspOrderAction(event):
    db = _getDataBase()
    dict = getStrategyInfo(event.dict)
    db.input_order_action.insert(dict)


# 报单录入 OnRspOrderInsert OnErrRtnOrderInsert
def insertRspOrderInsert(event):
    db = _getDataBase()
    dict = getStrategyInfo(event.dict)
    db.input_order.insert(dict)


# 交易回报 OnRtnTrade
def insertRtnTrade(event):
    db = _getDataBase()
    dict = getStrategyInfo(event.dict)
    db.trade.insert(dict)

# 请求错误
def insertRspError(event):
    db = _getDataBase()
    dict = getStrategyInfo(event.dict)
    db.error_info.insert(dict)
    # db.CThostFtdcRspInfoField.insert(event.dict)


# 保存下单参数
def insertSendOrderArgs(event):
    db = _getDataBase()
    # 枚举类型要转字符串保存
    direction = str(event.dict['direction']).split('.')[-1]
    event.dict['direction'] = direction
    price_type = str(event.dict['price_type']).split('.')[-1]
    event.dict['price_type'] = price_type
    stop_price = str(event.dict['stop_price']).split('.')[-1]
    event.dict['stop_price'] = stop_price
    contingent_condition = str(event.dict['contingent_condition']).split('.')[-1]
    event.dict['contingent_condition'] = contingent_condition

    event.dict = _insertTime(event.dict)

    db.send_order.insert(event.dict)

# 保存撤单参数
def insertCancelOrderArgs(event):
    db = _getDataBase()
    event.dict = _insertTime(event.dict)
    db.cancel_order.insert(event.dict)



# 更新持仓
def insertPosition(event):
    db = _getDataBase()
    dict = _insertTime(event.dict)
    db.position.insert(dict)


# 更新账户
def updateAccount(event):
    db = _getDataBase()
    dict = _insertTime(event.dict)
    if db.account.find().count() > 0:
        db.account.update({'AccountID': dict['AccountID']},{"$set": dict})
    else:
        db.account.insert(dict)


# 插入时间
def _insertTime(dict):
    date = getTime()
    dict['insert_date'] = date[0]
    dict['insert_time'] = date[1]
    dict['insert_msec'] = date[2]
    return dict


def getStrategyInfo(dict):
    db = _getDataBase()
    dict = _insertTime(dict)
    result = list(db.send_order.find({'order_ref':int(dict['OrderRef'])}))
    if len(result) > 0:
        result = result[0]
        dict['strategy_name'] = result['strategy_name']
        dict['strategy_id'] = result['strategy_id']
    else:
        dict['strategy_name'] = '未知'
        dict['strategy_id'] = '未知'
    return dict

# 获取最大报单编号
def getMaxOrderRef():
    db = _getDataBase()
    result = list(db.send_order.find({}).sort([('order_ref', -1)]).limit(1))
    if len(result) > 0:
        result = result[0]
        return int(result['order_ref'])
    else:
        return 0


def getMaxOrderActionRef():
    db = _getDataBase()
    result = list(db.cancel_order.find({}).sort([('order_action_ref', -1)]).limit(1))
    if len(result) > 0:
        result = result[0]
        return int(result['order_action_ref'])
    else:
        return 0

if __name__ == '__main__':
    def updateAccount(event):
        db = _getDataBase()
        if db.account.find().count() > 0:
            db.account.update({'AccountID': event.dict['AccountID']},
                              {"$set": event.dict})
        else:
            db.account.insert(event.dict)