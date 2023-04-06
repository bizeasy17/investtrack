from datetime import date, datetime, timedelta
from tracemalloc import start
import time

import pandas as pd
import tushare as ts
from django.db.models import Q
from stockmarket.models import StockNameCodeMap

from analysis.utils import (days_between, generate_task, init_eventlog,
                            get_event_status, last_download_date,
                            log_download_hist, set_event_completed)

from .models import StockHistory, StockHistoryDaily, StockStrategyTestLog, StockIndexHistory

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


def process_stock_download(ts_code, start_date, end_date, asset='E', freq='D', sys_event_list=['MARK_CP']):
    exec_date = date.today()
    evt_status = get_event_status('HIST_DOWNLOAD', exec_date)

    if ts_code is None:
        if evt_status == 0:
            print("previous downloading is still ongoing")
        elif evt_status == 1:
            print("history has been downloaded today")
        else:  # event not exist, can run today
            if ts_code is None:
                init_eventlog('HIST_DOWNLOAD', exec_date=exec_date, freq=freq)
            handle_hist_download(ts_code, start_date, end_date,
                                 asset, freq, sys_event_list)
            if ts_code is None:
                set_event_completed(
                    'HIST_DOWNLOAD', exec_date=exec_date, freq=freq)
            print("history has been downloaded successfully")
    else:
        handle_hist_download(ts_code, start_date, end_date,
                             asset, freq, sys_event_list)


def proess_stock_download_new(ts_code, start_date, freq='D',):
    start_date = None
    # end_date = None
    today = date.today()

    try:
        if ts_code is not None:
            ts_code_list = ts_code.split(',')
            if ts_code_list is not None:
                if len(ts_code_list) > 1:
                    companies = StockNameCodeMap.objects.filter(
                        ts_code__in=ts_code_list).order_by('ts_code')
                else:
                    companies = StockNameCodeMap.objects.filter(
                        ts_code=ts_code).order_by('ts_code')
        else:
            companies = StockNameCodeMap.objects.filter().order_by('ts_code')

        for company in companies:
            # end_date = today
            if freq == 'D':
                start_date = company.last_update_date
                # company.last_update_date = today
            if freq == 'W':
                start_date = company.hist_download_date_w
                # company.hist_download_date_w = today
            if freq == 'M':
                start_date = company.hist_download_date_m
                # company.hist_download_date_m = today
            
            if start_date is not None: # 如果有差异就下载，不然就退出
                # 已完成首次下载
                print('hist update time')
                if start_date >= today: 
                    print('ran it today, exit...')
                    continue
                
                days_btw = days_between(start_date, today)
                if freq == 'D':
                    if days_btw < 1:
                        continue
                if freq == 'W':
                    if days_btw < 7:
                        continue
                if freq == 'M':
                    if days_btw < 28:
                        continue

                download_stock_hist(company,
                    company.ts_code, start_date + timedelta(days=1), today, company.asset, freq, )
            else:
                # 需要进行首次下载
                print('first time')
                download_stock_hist(company,
                    company.ts_code, company.list_date, today, company.asset, freq, )

            if company.asset == 'E':
                if freq == 'D':
                    # start_date = company.last_update_date
                    hist = StockHistoryDaily.objects.filter(ts_code=company.ts_code, freq=freq).order_by('-trade_date').first()
                if freq in ['W','M']:
                    hist = StockHistory.objects.filter(ts_code=company.ts_code, freq=freq).order_by('-trade_date').first()
            else:
                hist = StockIndexHistory.objects.filter(ts_code=company.ts_code, freq=freq).order_by('-trade_date').first()   
            
            if hist is not None:
                if freq == 'D':
                    company.last_update_date = hist.trade_date
                if freq == 'W':
                    company.hist_download_date_w = hist.trade_date
                if freq == 'M':
                    company.hist_download_date_m = hist.trade_date
                company.save()
    except Exception as err:
        print(err)
    # pass

def handle_hist_download(ts_code, sdate, edate, asset='E', freq='D', sys_event_list=['MARK_CP']):
    '''
    可以接受的输入参数
    ts_code：1) 如果有输入，则只下载输入的code股票，2）未输入，下载所有股票
    start date：下载开始时间
    end date：下载结束时间
    asset：股票还是指数，E or I
    freq：周期，D，W（未实现），M（未实现），60分钟（为实现）
    system event list：完成下载后
    '''
    download_type = 0  # 首次
    start_date = None
    end_date = None
    today = date.today()

    try:
        if ts_code is not None:
            ts_code_list = ts_code.split(',')
            if ts_code_list is not None:
                if len(ts_code_list) > 1:
                    listed_companies = StockNameCodeMap.objects.filter(
                        ts_code__in=ts_code_list)
                else:
                    listed_companies = StockNameCodeMap.objects.filter(
                        ts_code=ts_code)
        else:
            listed_companies = StockNameCodeMap.objects.filter()

        if listed_companies is not None:
            for listed_company in listed_companies:
                last_date = last_download_date(
                    listed_company.ts_code, 'HIST_DOWNLOAD', freq)
                if sdate is not None and edate is not None:  # 给定下载开始和结束时间
                    start_date = datetime.strptime(sdate, '%Y-%m-%d')
                    end_date = datetime.strptime(edate, '%Y-%m-%d')
                    download_stock_hist(listed_company,
                        listed_company.ts_code, start_date, end_date, listed_company.asset, freq, )
                else:  # 根据日志记录下载相应历史记录
                    print(last_date)
                    if last_date is not None:
                        if last_date[1] < today and today > listed_company.last_update_date:  # 如果有差异就下载，不然就退出
                            # 已完成首次下载
                            download_type = 1
                            print('update hist')
                            start_date = last_date[1] + \
                                timedelta(days=1)
                            download_stock_hist(listed_company,
                                listed_company.ts_code, last_date[1] + timedelta(days=1), today, listed_company.asset, freq, )
                    else:
                        # 需要进行首次下载
                        print('first time')
                        start_date = listed_company.list_date
                        download_stock_hist(listed_company,
                            listed_company.ts_code, listed_company.list_date, today, listed_company.asset, freq, )
                    end_date = today
                if start_date is not None and end_date is not None:
                    # print('update log...')
                    log_download_hist(
                        listed_company.ts_code, 'HIST_DOWNLOAD', start_date, end_date, freq)
                    # generate_event(listed_company, download_type, freq)
                    generate_task(
                        listed_company, start_date, end_date, freq)
                    listed_company.last_update_date = end_date
                    listed_company.save()
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
        # mid_date = start_date + timedelta(days=365 * 10)
        split_date_list.append(
            [start_date, start_date + timedelta(days=365 * 10)])
        split_date_list.append(
            # fix issue of 年份分割错误 start_date -> end_date
            [start_date + timedelta(days=365 * 10) + \
             timedelta(days=1), end_date]
        )
    elif end_year - start_year <= 30:
        # mid_date = start_date + timedelta(days=365*10)
        split_date_list.append(
            [start_date, start_date + timedelta(days=365 * 10)])
        split_date_list.append(
            [start_date + timedelta(days=365 * 10) + timedelta(days=1),
             start_date + timedelta(days=365 * 20)])
        split_date_list.append(
            [start_date + timedelta(days=365*20) + timedelta(days=1),
             end_date],
        )
    elif end_year - start_year <= 40:
        # mid_date = start_date + timedelta(days=365*10)
        split_date_list.append(
            [start_date, start_date + timedelta(days=365*10)])
        split_date_list.append(
            [start_date + timedelta(days=365*10) + timedelta(days=1),
             start_date + timedelta(days=365*20)])
        split_date_list.append(
            [start_date + timedelta(days=365*20) + timedelta(days=1),
             start_date + timedelta(days=365*30)],
        )
        split_date_list.append(
            [start_date + timedelta(days=365*30) + timedelta(days=1),
             end_date],
        )
    return split_date_list


def download_hist_data(ts_code, start_date, end_date, freq='D', asset='E'):
    '''
    将每次的收盘历史数据按照10年分隔从tushare接口获取
    再按照时间先后顺序拼接
    '''
    if start_date is not None:
        split_cal_list = split_trade_cal(start_date, end_date)
        print(split_cal_list)
        df_list = []
        df_adj_list = []
        for trade_cal in split_cal_list:
            # 增加指数数据
            # print(ts_code)
            # print(asset)
            # print(freq)
            # print(trade_cal[0].strftime('%Y%m%d'))
            # print(trade_cal[1].strftime('%Y%m%d'))
            pro = ts.pro_api()

            if asset == 'I':
                df = ts.pro_bar(ts_code=ts_code, asset='I', freq=freq,
                                start_date=trade_cal[0].strftime('%Y%m%d'), end_date=trade_cal[1].strftime('%Y%m%d'))
            if asset == 'E':
                df = pro.stk_factor(ts_code=ts_code, start_date=trade_cal[0].strftime('%Y%m%d'), end_date=trade_cal[1].strftime('%Y%m%d'),
                    fields='ts_code,open,high,low,close,change,pct_change,pre_close,vol,amount,open_qfq,high_qfq,low_qfq,close_qfq,pre_close_qfq,trade_date')

            # if asset == 'E':
            #     df_adj = ts.pro_bar(ts_code=ts_code, asset=asset, freq=freq,
            #                     start_date=trade_cal[0].strftime('%Y%m%d'), end_date=trade_cal[1].strftime('%Y%m%d'), adj='qfq')
            #     # df_adj.rename(columns={'open': 'open_adj',
                #                 'high': 'high_adj', 'low': 'low_adj', 'close': 'close_adj', 'change': 'change_adj', 'pre_close': 'pre_close_adj', }, inplace=True)
                # df = df.iloc[::-1]  # 将数据按照时间顺序排列
                # df['open_qfq'] = df_adj['open']
                # df['high_qfq'] = df_adj['high']
                # df['low_qfq'] = df_adj['low']
                # df['close_qfq'] = df_adj['close']
                df['change_qfq'] = round(df['close_qfq'] - df['pre_close_qfq'],2)
                # df['pre_close_qfq'] = df_adj['pre_close']
                df['pct_chg_qfq'] = round(df['change_qfq'] / df['close_qfq'], 2)
            
            time.sleep(5)

            df_list.append(df)
        return pd.concat(df_list)


def download_stock_hist(company, ts_code, start_date, end_date, asset='E', freq='D'):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':' + ts_code +
          ' history trade info started.')
    # end_date = date.today()
    # print(listed_company.ts_code)
    df = download_hist_data(ts_code, start_date, end_date, freq, asset,)
    hist_list = []
    for idx, row in df.iterrows():
        hist = None
        if asset == 'E':
            if freq == 'D':
                hist = StockHistoryDaily(ts_code=row['ts_code'], trade_date=datetime.strptime(row['trade_date'], '%Y%m%d'), open=row['open'], high=row['high'],
                                        low=row['low'], close=row['close'], pre_close=row['pre_close'], change=row['change'], pct_chg=row['pct_change'], vol=row['vol'],
                                        amount=row['amount'],  open_qfq=row['open_qfq'], high_qfq=row['high_qfq'], low_qfq=row['low_qfq'], close_qfq=row['close_qfq'], 
                                        pre_close_qfq=row['pre_close_qfq'], change_qfq=row['change_qfq'], pct_chg_qfq=row['pct_chg_qfq'], freq=freq, company=company)
            else:
                hist = StockHistory(ts_code=row['ts_code'], trade_date=datetime.strptime(row['trade_date'], '%Y%m%d'), open=row['open'], high=row['high'],
                                        low=row['low'], close=row['close'], pre_close=row['pre_close'], change=row['change'], pct_chg=row['pct_change'], vol=row['vol'],
                                        amount=row['amount'], open_qfq=row['open_qfq'], high_qfq=row['high_qfq'], low_qfq=row['low_qfq'], close_qfq=row['close_qfq'], 
                                        pre_close_qfq=row['pre_close_qfq'], change_qfq=row['change_qfq'], pct_chg_qfq=row['pct_chg_qfq'], freq=freq, company=company)
        else: # 指数信息
            hist = StockIndexHistory(ts_code=row['ts_code'], trade_date=datetime.strptime(row['trade_date'], '%Y%m%d'), open=row['open'], high=row['high'],
                                        low=row['low'], close=row['close'], pre_close=row['pre_close'], change=row['change'], pct_chg=row['pct_chg'], vol=row['vol'],
                                        amount=row['amount'], freq=freq, company=company)
    # for v in df.values:
    #     hist = object

    #     if asset == 'E':
    #         if freq == 'D':
    #             hist = StockHistoryDaily(ts_code=v[0], trade_date=datetime.strptime(v[1], '%Y%m%d'), open=v[2], high=v[3],
    #                                     low=v[4], close=v[5], pre_close=v[6], change=v[7], pct_chg=v[8], vol=v[9],
    #                                     amount=v[10], freq=freq, company=company)
    #         else:
    #             hist = StockHistory(ts_code=v[0], trade_date=datetime.strptime(v[1], '%Y%m%d'), open=v[2], high=v[3],
    #                                     low=v[4], close=v[5], pre_close=v[6], change=v[7], pct_chg=v[8], vol=v[9],
    #                                     amount=v[10], freq=freq, company=company)
    #     else: # 指数信息
    #         hist = StockIndexHistory(ts_code=v[0], trade_date=datetime.strptime(v[1], '%Y%m%d'), open=v[2], high=v[3],
    #                                  low=v[4], close=v[5], pre_close=v[6], change=v[7], pct_chg=v[8], vol=v[9],
    #                                  amount=v[10], freq=freq, company=company)
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
    if len(hist_list) > 0:
        if asset == 'E':
            if freq == 'D':
                StockHistoryDaily.objects.bulk_create(hist_list)
            else:
                StockHistory.objects.bulk_create(hist_list)

        else:  # 指数信息
            StockIndexHistory.objects.bulk_create(hist_list)

        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':' + ts_code +
          ' history trade info downloaded.')
        
        # return hist_list[0].trade_date  
    else:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':' + ts_code +
          ' history trade info downloaded. Empty datafram')
        # return None

    