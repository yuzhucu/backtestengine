# -*- coding: utf-8 -*-

'''
author:       sjsj
contact:      songjie1217@hotmail.com
file:         iterator.py
time:         2017/9/8 11:38
description:

'''

__author__ = 'sjsj'

class PriceEventIterator(object):
    def __iter__(self):
        return self

    def next(self):
        return self.__next__()


# class TickEventIterator(PriceEventIterator):
#     def _create_event(self, row):
#         """
#         Obtain all elements of the bar a row of dataframe
#         and return a TickEvent
#         """
#         return row


class PandasDFTickEventIterator(PriceEventIterator):
    """
    PandasPanelBarEventIterator is designed to read a Pandas DataFrame like

                                   Bid        Ask
    Time
    2016-02-01 00:00:01.358  683.56000  683.58000
    2016-02-01 00:00:02.544  683.55998  683.58002
    2016-02-01 00:00:03.765  683.55999  683.58001

    with tick data (bid/ask)
    for one financial instrument and iterate TickEvents.
    """
    def __init__(self, df):
        """
        Takes the the events queue, ticker and Pandas DataFrame
        """
        self.data = df
        # self.ticker = ticker
        # self.tickers_lst = [ticker]
        self._itr_tick = self.data.iterrows()

    def __next__(self):
        index, row = next(self._itr_tick)
        price_event = row
        return price_event



