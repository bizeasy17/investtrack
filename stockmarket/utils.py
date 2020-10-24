import decimal
from datetime import datetime

import tushare as ts


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
            'c': realtime_quote,'p':realtime_df['pre_close'].mean(),
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
