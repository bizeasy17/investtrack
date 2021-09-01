from datetime import date, datetime, timedelta

import pandas as pd
import tushare as ts
from django.db.models import Q
from stockmarket.models import StockNameCodeMap

from analysis.utils import (generate_task, get_analysis_task,
                            get_trade_cal_diff, init_eventlog,
                            get_event_status, set_event_completed,
                            set_task_completed, is_hist_downloaded, last_download_date, log_download_hist)

# from .models import StockHistoryDaily, StockStrategyTestLog, StockIndexHistory
from stockmarket.models import CompanyDailyBasic, IndexDailyBasic
from .stock_hist import split_trade_cal
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


def handle_daily_basic(ts_code, start_date, end_date, freq='D'):
    exec_date = date.today()
    if ts_code is None:
        if is_hist_downloaded():
            init_eventlog('DAILY_BASIC',  exec_date=exec_date, freq=freq)
            basic_download(ts_code, start_date, end_date, freq,)
            set_event_completed(
                'DAILY_BASIC', exec_date=exec_date, freq=freq)
    else:
        basic_download(ts_code, start_date, end_date, freq,)


def basic_download(ts_code, start_date, end_date, freq='D'):
    exec_date = date.today()
    evt_status = get_event_status('DAILY_BASIC', exec_date)

    if ts_code is None:
        if evt_status == 0:
            print("previous downloading is still ongoing")
        elif evt_status == 1:
            print("history has been downloaded today")
        else:  # event not exist, can run today
            if ts_code is None:
                init_eventlog('DAILY_BASIC', exec_date=exec_date, freq=freq)
            process_basic_download(ts_code, start_date, end_date, freq)
            if ts_code is None:
                set_event_completed(
                    'DAILY_BASIC', exec_date=exec_date, freq=freq)
            print("history has been downloaded successfully")
    else:
        process_basic_download(ts_code, start_date, end_date, freq)


def process_basic_download(ts_code, sdate, edate, freq='D'):
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
                    listed_company.ts_code, 'DAILY_BASIC', freq)
                if sdate is not None and edate is not None:  # 给定下载开始和结束时间
                    start_date = sdate
                    end_date = edate
                    store_daily_basic(listed_company, 
                        listed_company.ts_code, listed_company.list_date, today, listed_company.asset, freq, )
                else:  # 根据日志记录下载相应历史记录

                    if last_date is not None:
                        if last_date[1] < today:  # 如果有差异就下载，不然就退出
                            # 已完成首次下载
                            download_type = 1
                            print('update daily basic')
                            start_date = last_date[1] + \
                                timedelta(days=1)
                            store_daily_basic(listed_company, 
                                listed_company.ts_code, last_date[1] + timedelta(days=1), today, listed_company.asset, freq, )
                    else:
                        # 需要进行首次下载
                        print('first time')
                        start_date = listed_company.list_date
                        store_daily_basic(listed_company, 
                            listed_company.ts_code, listed_company.list_date, today, listed_company.asset, freq, )
                    end_date = today
                if start_date is not None and end_date is not None:
                    set_task_completed(listed_company.ts_code, 'DAILY_BASIC',
                                       freq, None, task.start_date, task.end_date)
                else:
                    print('no daily hist to be downloaded for give period')
    except Exception as e:
        print(e)


def download_basic_data(ts_code, start_date, end_date, asset='E', freq='D'):
    '''
    将每次的收盘历史数据按照10年分隔从tushare接口获取
    再按照时间先后顺序拼接
    '''
    if start_date is not None:
        split_cal_list = split_trade_cal(start_date, end_date)
        print(split_cal_list)
        df_list = []
        pro = ts.pro_api()
        for trade_cal in split_cal_list:
            # 增加指数数据
            # print(stock_symbol)
            # print(asset)
            # print(freq)
            # print(trade_cal[0].strftime('%Y%m%d'))
            # print(trade_cal[1].strftime('%Y%m%d'))
            if asset == 'E':
                df = pro.daily_basic(ts_code=ts_code, start_date=trade_cal[0].strftime(
                    '%Y%m%d'), end_date=trade_cal[1].strftime('%Y%m%d'))
            elif asset == 'I':
                df = pro.index_dailybasic(ts_code=ts_code, start_date=trade_cal[0].strftime(
                    '%Y%m%d'), end_date=trade_cal[1].strftime('%Y%m%d'))
            # df = ts.pro_bar(ts_code=stock_symbol, asset=asset, freq=freq,
            #                 start_date=trade_cal[0].strftime('%Y%m%d'), end_date=trade_cal[1].strftime('%Y%m%d'))
            # df = df.iloc[::-1]  # 将数据按照时间顺序排列
            df_list.append(df)
        return pd.concat(df_list)


def store_daily_basic(listed_company, ts_code, start_date, end_date, asset='E', freq='D'):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':' + ts_code +
          ' history trade info started.')
    # end_date = date.today()
    # print(listed_company.ts_code)
    df = download_basic_data(ts_code, start_date, end_date,  asset, freq,)
    hist_list = []
    for index, row in df.iterrows():
        hist = None

        if asset == 'E':
            hist = CompanyDailyBasic(ts_code=row['ts_code'], stock_code=row['ts_code'].split('.')[0], trade_date=datetime.strptime(row['trade_date'], '%Y%m%d'),
                                     close=row['close'], turnover_rate=row['turnover_rate'], turnover_rate_f=row['turnover_rate_f'], 
                                     volume_ratio=row['volume_ratio'], pe=row['pe'], pe_ttm=row['pe_ttm'], pb=row['pb'], ps=row['ps'],
                                     ps_ttm=row['ps_ttm'], dv_ratio=row['dv_ratio'], dv_ttm=row['dv_ttm'], total_share=row['total_share'],
                                     float_share=row['float_share'], free_share=row['free_share'], total_mv=row['total_mv'], circ_mv=row['circ_mv'], company=listed_company)
        else:  # 指数信息
            hist = IndexDailyBasic(ts_code=row['ts_code'], trade_date=datetime.strptime(row['trade_date'], '%Y%m%d'),
                                     turnover_rate=row['turnover_rate'], turnover_rate_f=row['turnover_rate_f'], 
                                     pe=row['pe'], pe_ttm=row['pe_ttm'], pb=row['pb'], total_share=row['total_share'],
                                     float_share=row['float_share'], free_share=row['free_share'], total_mv=row['total_mv'], float_mv=row['float_mv'], company=listed_company)
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
    if asset == 'E':
        CompanyDailyBasic.objects.bulk_create(hist_list)
    else:  # 指数信息
        IndexDailyBasic.objects.bulk_create(hist_list)

    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':' + ts_code +
          ' history trade info downloaded.')
