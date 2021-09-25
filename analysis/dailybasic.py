from datetime import date, datetime, timedelta

import pandas as pd
import tushare as ts
from django.db.models import Q
# from .models import StockHistoryDaily, StockStrategyTestLog, StockIndexHistory
from stockmarket.models import (CompanyDailyBasic, IndexDailyBasic,
                                StockNameCodeMap)

from analysis.models import IndustryBasicQuantileStat
from analysis.utils import apply_analysis_date, init_log, ready2_download

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
DAILYBASIC_TYPE = 'DAILY_BASIC'


def get_listed_companies(ts_code):
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

    return listed_companies


def download_dailybasic(ts_code=None, start_date=None, end_date=None, freq='D'):
    # 检查ts_code的下载状态
    # 根据状态判断是下载，或者退出
    # 如果是下载，通过接口获得数据，创建对象，
    #
    if end_date is None:
        end_date = date.today()

    if start_date is None:
        reset_start = True

    listed_companies = get_listed_companies(ts_code)

    # print(reset_start)

    for company in listed_companies:
        if start_date is None:
            # print(company.ts_code)
            # print(start_date)
            if company.dailybasic_date is None:
                start_date = company.list_date
            else:
                start_date = company.dailybasic_date + timedelta(days=1)
        try:
            if ready2_download(company.ts_code, end_date, DAILYBASIC_TYPE, freq):
                log = init_log(
                    company.ts_code, start_date, end_date, freq, DAILYBASIC_TYPE)
                store_daily_basic(company, start_date, end_date)
                log.is_done = True
                log.save()

                company.dailybasic_date = end_date
                company.save()
                # complete_download(company.ts_code, end_date, DOWNLOAD_TYPE, freq)
            else:
                print(company.ts_code +
                      ' not ready for download / already completed')
        except Exception as err:
            print(err)

        if reset_start:
            print('reset start date')
            start_date = None  # fix bug，所有股票的下载开始日会默认为第一个list_date


def store_daily_basic(company, start_date, end_date):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':' + company.ts_code +
          ' history daily basic info started.')
    # end_date = date.today()
    # print(listed_company.ts_code)
    df = download_basic_data(
        company.ts_code, start_date, end_date, company.asset)
    hist_list = []
    for index, row in df.iterrows():
        hist = None

        if company.asset == 'E':
            hist = CompanyDailyBasic(ts_code=row['ts_code'], stock_code=row['ts_code'].split('.')[0], trade_date=datetime.strptime(row['trade_date'], '%Y%m%d'),
                                     close=row['close'], turnover_rate=row['turnover_rate'], turnover_rate_f=row['turnover_rate_f'],
                                     volume_ratio=row['volume_ratio'], pe=row['pe'], pe_ttm=row['pe_ttm'], pb=row['pb'], ps=row['ps'],
                                     ps_ttm=row['ps_ttm'], dv_ratio=row['dv_ratio'], dv_ttm=row['dv_ttm'], total_share=row['total_share'],
                                     float_share=row['float_share'], free_share=row['free_share'], total_mv=row['total_mv'], circ_mv=row['circ_mv'], company=company)
        else:  # 指数信息
            hist = IndexDailyBasic(ts_code=row['ts_code'], trade_date=datetime.strptime(row['trade_date'], '%Y%m%d'),
                                   turnover_rate=row['turnover_rate'], turnover_rate_f=row['turnover_rate_f'],
                                   pe=row['pe'], pe_ttm=row['pe_ttm'], pb=row['pb'], total_share=row['total_share'],
                                   float_share=row['float_share'], free_share=row['free_share'], total_mv=row['total_mv'], float_mv=row['float_mv'], company=company)
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
    if company.asset == 'E':
        CompanyDailyBasic.objects.bulk_create(hist_list)
    elif company.asset == 'I':  # 指数信息
        IndexDailyBasic.objects.bulk_create(hist_list)

    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':' + company.ts_code +
          ' history daily basic info downloaded.')


def download_basic_data(ts_code, start_date, end_date, asset):
    '''
    将每次的收盘历史数据按照10年分隔从tushare接口获取
    再按照时间先后顺序拼接
    '''
    print(start_date)
    print(end_date)

    if start_date is not None:
        split_cal_list = split_trade_cal(start_date, end_date)
        print(split_cal_list)
        dailybasic_list = []
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
            dailybasic_list.append(df)
        return pd.concat(dailybasic_list)


def process_industrybasic_quantile(quantile, next_dates, analysis_type='INDUSTRY_BASIC_QUANTILE'):
    # now = date.today()
    if next_dates is not None and len(next_dates) > 0:
        company = StockNameCodeMap.objects.order_by('industry').values('industry').distinct()
        if company is not None and len(company) > 0:
            for date in next_dates:
                for c in company:
                    try:
                        # print(date)
                        log = init_log(
                            c['industry'], date.analysis_date, date.analysis_date, 'D', analysis_type)
                        collect_industrybasic_quantile(
                            c['industry'], quantile, date.analysis_date)
                        log.is_done = True
                        log.save()
                        # complete_download(company.ts_code, end_date, DOWNLOAD_TYPE, freq)
                    except Exception as err:
                        print('process_industrybasic_quantile')
                        print(err)
                    print(c['industry'] + ' completed for date')
                    print(date.analysis_date)
                apply_analysis_date(analysis_type, date.analysis_date)
    else:
        print('not ready for calculate quantile / already completed')


def collect_industrybasic_quantile(industry, quantile, snap_date):
    '''
    1. 获取所有该行业下所有股票的daily basic
    2. 对每项基本面指标进行%统计
    3. 从当前start date循环到开盘后的第一个月的快照日
    '''

    cdb = CompanyDailyBasic.objects.filter(
        company__industry=industry, trade_date=snap_date).values('pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm')

    if len(cdb) > 0:
        # print(industry)
        df = pd.DataFrame(cdb)

        basic_qtile = df.quantile(quantile)
        # pe_ttm_qtile = df.pe_ttm.quantile(quantile)
        # pb_qtile = df.pb.quantile(quantile)
        # ps_qtile = df.ps.quantile(quantile)
        # ps_ttm_qtile = df.ps_ttm.quantile(quantile)

        for index, row in basic_qtile.iterrows():
            # print(index)
            for col, val in row.items():
                try:
                    # print(col)
                    # print(val)
                    new_ibqs = IndustryBasicQuantileStat(
                        industry=industry, basic_type=col, quantile=index, quantile_val=round(val,2),stk_quantity=len(cdb), snap_date=snap_date)
                    new_ibqs.save()
                except Exception as err:
                    print('collect_industrybasic_quantile')
                    print(err)
                    # print('new calculation quantile ' +
                    #       quantile + ' for ' + industry)
                    # new_ibqs = IndustryBasicQuantileStat(
                    #     industry=industry, basic_type=col, quantile=index, stk_quantity=len(cdb), snap_date=snap_date)
                    # new_ibqs.save()
    else:
        print('no stock in ' + industry)
