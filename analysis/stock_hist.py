from datetime import date, datetime, timedelta

import pandas as pd
import tushare as ts
from django.db.models import Q

from stockmarket.models import StockNameCodeMap

from .models import StockHistoryDaily, StockStrategyTestLog


def split_trade_cal(start_date, end_date):
    '''
    如果取数的时间跨度大于10年，就需要对时间进行拆分
    譬如：
    1. 19910901 - 20050901，返回的是[(19910901,20010831),(20010901,20050901)]
    2. 19910901 - 20010901，返回的是[(19910901,20010901)]
    3. 19910901 - 20200501，返回的是[(19910901,20010831),(20010901,20110901),(20110902,20200501)]
    '''
    split_date_list = []
    start_year = start_date.year
    end_year = end_date.year
    if end_year - start_year <= 10:
        split_date_list.append([start_date, end_date])
    elif end_year - start_year <= 20:
        mid_date = start_date + timedelta(days=365 * 10)
        split_date_list.append(
            [start_date, mid_date])
        split_date_list.append(
            [mid_date + timedelta(days=1), start_date]
        )
    elif end_year - start_year <= 30:
        mid_date = start_date + timedelta(days=365*10)
        split_date_list.append(
            [start_date, mid_date])
        split_date_list.append(
            [mid_date + timedelta(days=1), mid_date +
             timedelta(days=365*10) + timedelta(days=1)])
        split_date_list.append(
            [mid_date + timedelta(days=365*10) + timedelta(days=2),
             end_date],
        )
    return split_date_list


def hist_since_listed(stock_symbol, start_date, end_date, freq='D'):
    '''
    将每次的收盘历史数据按照10年分隔从tushare接口获取
    再按照时间先后顺序拼接
    '''
    split_cal_list = split_trade_cal(start_date, end_date)
    df_list = []
    for trade_cal in split_cal_list:
        df = ts.pro_bar(ts_code=stock_symbol, freq=freq,
                        start_date=trade_cal[0].strftime('%Y%m%d'), end_date=trade_cal[1].strftime('%Y%m%d'))
        # df = df.iloc[::-1]  # 将数据按照时间顺序排列
        df_list.append(df)
    return pd.concat(df_list)


def download_stock_hist(ts_code_list=[]):
    end_date = date.today()
    if len(ts_code_list) == 0:
        listed_companies = StockNameCodeMap.objects.filter(
            is_hist_downloaded=False)
    else:
        listed_companies = StockNameCodeMap.objects.filter(
            is_hist_downloaded=False, ts_code__in=ts_code_list)
    if listed_companies is not None and len(listed_companies) > 0:
        for listed_company in listed_companies:
            df = hist_since_listed(
                listed_company.ts_code, listed_company.list_date, end_date)
            hist_list = []
            for v in df.values:
                hist_D = StockHistoryDaily(ts_code=v[0], trade_date=datetime.strptime(v[1], '%Y%m%d'), open=v[2], high=v[3],
                                           low=v[4], close=v[5], pre_close=v[6], change=v[7], pct_chg=v[8], vol=v[9],
                                           amount=v[10], freq='D')
                '''
                ts_code	str	股票代码
                trade_date	str	交易日期
                open	float	开盘价
                high	float	最高价
                low	float	最低价
                close	float	收盘价
                pre_close	float	昨收价
                change	float	涨跌额
                pct_chg	float	涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
                vol	float	成交量 （手）
                amount	float	成交额 （千元）
                '''
                hist_list.append(hist_D)
            StockHistoryDaily.objects.bulk_create(hist_list)
            listed_company.is_hist_downloaded = True
            listed_company.hist_update_date = end_date
            listed_company.save()
            now = datetime.now()
            print(now.strftime("%Y-%m-%d %H:%M:%S") + ':' + listed_company.ts_code +
                  ' history trade info downloaded.')


def update_stock_hist():
    end_date = date.today()
    listed_companies = StockNameCodeMap.objects.filter(
        is_hist_downloaded=True).filter(Q(is_hist_updated=False) | Q(hist_update_date__lt=date.today()))
    if listed_companies is not None and len(listed_companies) > 0:
        for listed_company in listed_companies:
            df = hist_since_listed(
                listed_company.ts_code, listed_company.hist_update_date, end_date)
            hist_list = []
            for v in df.values:
                hist_D = StockHistoryDaily(ts_code=v[0], trade_date=datetime.strptime(v[1], '%Y%m%d'), open=v[2], high=v[3],
                                           low=v[4], close=v[5], pre_close=v[6], change=v[7], pct_chg=v[8], vol=v[9],
                                           amount=v[10], freq='D')
                '''
                ts_code	str	股票代码
                trade_date	str	交易日期
                open	float	开盘价
                high	float	最高价
                low	float	最低价
                close	float	收盘价
                pre_close	float	昨收价
                change	float	涨跌额
                pct_chg	float	涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
                vol	float	成交量 （手）
                amount	float	成交额 （千元）
                '''
                hist_list.append(hist_D)
            StockHistoryDaily.objects.bulk_create(hist_list)
            listed_company.is_hist_updated = True
            listed_company.hist_update_date = end_date
            listed_company.save()
            now = datetime.now()
            print(now.strftime("%Y-%m-%d %H:%M:%S") + ':' + listed_company.ts_code +
                  ' history trade info updated.')
