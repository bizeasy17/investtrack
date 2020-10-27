from datetime import date, datetime, timedelta

import pandas as pd
import tushare as ts
from django.db.models import Q
from stockmarket.models import StockNameCodeMap

from analysis.utils import (generate_systask, hist_downloaded,
                            last_download_date, log_download_hist)

from .models import StockHistoryDaily, StockStrategyTestLog

'''
check the missing history sql query
SELECT ts_code 
FROM   public.stockmarket_stocknamecodemap code 
WHERE  NOT EXISTS (
   SELECT  -- SELECT list mostly irrelevant; can just be empty in Postgres
   FROM   public.analysis_stockhistorydaily
   WHERE  ts_code = code.ts_code
   );
'''


def handle_hist_download(ts_code, sdate, edate, asset, freq, sys_event_list):
    if ts_code is not None and freq is not None:
        start_date = None
        end_date = None
        today = date.today()
        ts_code_list = ts_code.split(',')

        if ts_code_list is not None and len(ts_code_list) >= 1:
            for ts_code in ts_code_list:
                try:
                    listed_company = StockNameCodeMap.objects.get(
                        ts_code=ts_code)
                    last_date = last_download_date(
                        ts_code, 'HIST_DOWNLOAD', freq)

                    if sdate is not None and edate is not None:  # 给定下载开始和结束时间
                        start_date = sdate
                        end_date = edate
                        download_stock_hist(
                            ts_code, listed_company.list_date, today, asset, freq, )
                    else:  # 根据日志记录下载相应历史记录
                        if last_date is not None:
                            if last_date[1] < today:
                                # 已完成首次下载
                                # print('not first time')
                                start_date = last_date[1] + \
                                    timedelta(days=1)
                                download_stock_hist(
                                    ts_code, last_date[1] + timedelta(days=1), today, asset, freq, )
                        else:
                            # 需要进行首次下载
                            # print('first time')
                            start_date = listed_company.list_date
                            download_stock_hist(
                                ts_code, listed_company.list_date, today, asset, freq, )
                        end_date = today
                    if start_date is not None and end_date is not None:
                        log_download_hist(
                            ts_code, 'HIST_DOWNLOAD', start_date, end_date, freq)
                        generate_systask(
                            ts_code, freq, start_date, end_date, sys_event_list)
                    else:
                        print('no history to be downloaded for give period')
                except Exception as e:
                    print(e)

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


def download_hist_data(stock_symbol, start_date, end_date, freq='D', asset='E'):
    '''
    将每次的收盘历史数据按照10年分隔从tushare接口获取
    再按照时间先后顺序拼接
    '''
    if start_date is not None:
        split_cal_list = split_trade_cal(start_date, end_date)
        print(split_cal_list)
        df_list = []
        for trade_cal in split_cal_list:
            # 增加指数数据
            print(stock_symbol)
            print(asset)
            print(freq)
            print(trade_cal[0].strftime('%Y%m%d'))
            print(trade_cal[1].strftime('%Y%m%d'))
            df = ts.pro_bar(ts_code=stock_symbol, asset=asset, freq=freq,
                            start_date=trade_cal[0].strftime('%Y%m%d'), end_date=trade_cal[1].strftime('%Y%m%d'))
            # df = df.iloc[::-1]  # 将数据按照时间顺序排列
            df_list.append(df)
        return pd.concat(df_list)


def download_stock_hist(ts_code, start_date, end_date, asset='E', freq='D'):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':' + ts_code +
          ' history trade info started.')
    end_date = date.today()
    # print(listed_company.ts_code)
    df = download_hist_data(ts_code, start_date, end_date, freq, asset,)
    hist_list = []
    for v in df.values:
        hist = object
        if freq == 'D':
            hist = StockHistoryDaily(ts_code=v[0], trade_date=datetime.strptime(v[1], '%Y%m%d'), open=v[2], high=v[3],
                                     low=v[4], close=v[5], pre_close=v[6], change=v[7], pct_chg=v[8], vol=v[9],
                                     amount=v[10], freq=freq)
        else:
            pass
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
        hist_list.append(hist)
    if freq == 'D':
        StockHistoryDaily.objects.bulk_create(hist_list)
    else:
        pass
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':' + ts_code +
          ' history trade info downloaded.')
