# -*- coding: utf-8 -*-

'''
author:       Jimmy
contact:      234390130@qq.com
file:         tradeType.py
time:         2017/9/12 上午10:11
description: 

'''

__author__ = 'Jimmy'
from ctp.ctp_struct import *

# 方向
BUY = DirectionType.Buy
SELL = DirectionType.Sell


# 开平
OPEN = OffsetFlagType.Open.__char__()
CLOSE = OffsetFlagType.Close.__char__()
CLOSET = OffsetFlagType.CloseToday.__char__()
CLOSEY = OffsetFlagType.CloseYesterday.__char__()


#   Immediately = 49
# 	Touch = 50
# 	TouchProfit = 51
# 	ParkedOrder = 52
# 	LastPriceGreaterThanStopPrice = 53
# 	LastPriceGreaterEqualStopPrice = 54
# 	LastPriceLesserThanStopPrice = 55
# 	LastPriceLesserEqualStopPrice = 56
# 	AskPriceGreaterThanStopPrice = 57
# 	AskPriceGreaterEqualStopPrice = 65
# 	AskPriceLesserThanStopPrice = 66
# 	AskPriceLesserEqualStopPrice = 67
# 	BidPriceGreaterThanStopPrice = 68
# 	BidPriceGreaterEqualStopPrice = 69
# 	BidPriceLesserThanStopPrice = 70
# 	BidPriceLesserEqualStopPrice = 72

