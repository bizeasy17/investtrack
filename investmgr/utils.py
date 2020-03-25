import decimal
from datetime import datetime

import tushare as ts


def get_realtime_price(stock_symbols=[]):
    realtime_quotes = {}
    if stock_symbols is not None and len(stock_symbols) >= 1:
        realtime_df = ts.get_realtime_quotes(stock_symbols)
        # realtime_df = realtime_df[[('price', 'bid', 'pre_close', 'code')]]
        realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                                   'high', 'low', 'bid', 'ask', 'volume', 'amount', 'date', 'time']]
        if realtime_df is not None and len(realtime_df) > 0:
            for realtime_quote in realtime_df.values:
                price = round(decimal.Decimal(realtime_quote[3]), 2)
                bid = round(decimal.Decimal(realtime_quote[6]), 2)
                pre_close = round(decimal.Decimal(realtime_quote[2]), 2)
                quote_datetime = realtime_quote[10] + ' ' + realtime_quote[11]
                if price != decimal.Decimal(0.00):
                    price = price
                elif bid != decimal.Decimal(0.00):
                    price = bid
                else:
                    price = pre_close
                realtime_quotes[realtime_quote[0]] = price
    return realtime_quotes
