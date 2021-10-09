import ast
import decimal
from datetime import datetime

import numpy as np
import tushare as ts
from analysis.models import (AnalysisDateSeq, IndustryBasicQuantileStat,
                             StockHistoryDaily)

from .models import StockNameCodeMap


def get_single_realtime_quote(symbol):
    # 保持向前兼容
    code = symbol.split('.')
    symbol = code[0]
    # 获得实时报价
    realtime_df = ts.get_realtime_quotes(symbol)  # 需要再判断一下ts_code
    realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                               'high', 'low', 'bid', 'ask', 'volume', 'amount', 'date', 'time']]
    realtime_price_dict = {}
    if len(realtime_df) > 0:
        if realtime_df['price'].mean() != 0:
            realtime_quote = realtime_df['price'].mean()
        elif realtime_df['pre_close'].mean() != 0:
            realtime_quote = realtime_df['pre_close'].mean()
        elif realtime_df['open'].mean() != 0:
            realtime_quote = realtime_df['open'].mean()
        t = datetime.strptime(str(
            realtime_df['date'][0]) + ' ' + str(realtime_df['time'][0]), "%Y-%m-%d %H:%M:%S")
        realtime_price_dict = {
            't': t, 'o': realtime_df['open'].mean(), 'h': realtime_df['high'].mean(),
            'l': realtime_df['low'].mean(),
            'c': realtime_quote, 'p': realtime_df['pre_close'].mean(),
        }
    return realtime_price_dict


def get_realtime_quote(stock_symbols=[]):
    realtime_quotes = {}
    if stock_symbols is not None and len(stock_symbols) >= 1:
        realtime_df = ts.get_realtime_quotes(stock_symbols)
        realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                                   'high', 'low', 'bid', 'ask', 'volume', 'amount', 'date', 'time']]
        if realtime_df is not None and len(realtime_df) > 0:
            for realtime_quote in realtime_df.values:
                price = round(decimal.Decimal(realtime_quote[3]), 2)
                bid = round(decimal.Decimal(realtime_quote[6]), 2)
                pre_close = round(decimal.Decimal(realtime_quote[2]), 2)
                if price != decimal.Decimal(0.00):
                    price = price
                elif bid != decimal.Decimal(0.00):
                    price = bid
                else:
                    price = pre_close
                realtime_quotes[realtime_quote[0]] = price
    return realtime_quotes


def get_realtime_quotes(stock_symbols=[]):
    realtime_quotes = {}
    if stock_symbols is not None and len(stock_symbols) >= 1:
        realtime_df = ts.get_realtime_quotes(stock_symbols)
        realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                                   'high', 'low', 'bid', 'ask', 'volume', 'amount', 'date', 'time']]
        if realtime_df is not None and len(realtime_df) > 0:
            for realtime_quote in realtime_df.values:
                price = round(decimal.Decimal(realtime_quote[3]), 2)
                bid = round(decimal.Decimal(realtime_quote[6]), 2)
                pre_close = round(decimal.Decimal(realtime_quote[2]), 2)
                if price != decimal.Decimal(0.00):
                    price = price
                elif bid != decimal.Decimal(0.00):
                    price = bid
                else:
                    price = pre_close
                realtime_quotes[realtime_quote[0]] = str(price) + ',' + str(round(
                    (price - pre_close) / pre_close, 2) * 100)
    return realtime_quotes


def get_stocknames(stock_symbols=[]):
    stocknames = {}
    if stock_symbols is not None and len(stock_symbols) >= 1:
        for stock_symbol in stock_symbols:
            map = StockNameCodeMap.objects.get(ts_code=stock_symbol)
            stocknames[stock_symbol] = map.stock_name
    return stocknames


def str_eval(str):
    '''
    逗号分隔，转成dict
    '''
    dict = ast.literal_eval(str)
    return dict


def get_ind_basic(industry, type=[]):
    ind_dict = {}

    try:
        last_analysis = AnalysisDateSeq.objects.filter(
            applied=True, seq_type='INDUSTRY_BASIC_QUANTILE').order_by('-analysis_date').first()

        ibqs = IndustryBasicQuantileStat.objects.filter(industry=industry,
                                                        basic_type__in=type, snap_date=last_analysis.analysis_date).exclude(
                                                        quantile=.25).exclude(quantile=.75).order_by('-snap_date')

        if ibqs is not None and len(ibqs) > 0:
            for ibq in ibqs:
                ind_dict[ibq.basic_type+str(ibq.quantile)] = ibq.quantile_val if not np.isnan(ibq.quantile_val) else 0

        return ind_dict
    except Exception as e:
        print(e)
