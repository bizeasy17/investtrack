

import logging
import pandas as pd
from datetime import date, datetime, timedelta

from analysis.analysis_dingdi import handle_dingdi_cp
from analysis.analysis_jiuzhuan_cp import handle_jiuzhuan_cp
from analysis.models import PickedStocksMeetStrategy
from analysis.stock_hist import handle_hist_download
from analysis.utils import get_closest_trade_cal, last_download_date
from analysis.v2.mark_junxian_cp_v2 import handle_junxian_cp
from stockmarket.models import StockNameCodeMap
from analysis.models import StockHistoryDaily


def pre_stocks_pick():
    '''
    运行一遍下载，标记过程
    '''

def pick_stocks_by_strategy(strategy_code=None, freq='D', ts_code_list=[]
                            ):
    '''
    1. 当天的数据是否已经下载，如果未下载，先下载
    2. 执行选股
    - 九转
    - 均线
    - 底
    - 突破
    - W底
    3. 存入选股结果
    '''
    today = date.today
    try:
        if ts_code_list is None:
            listed_companies = StockNameCodeMap.objects.filter()
        else:
            listed_companies = StockNameCodeMap.objects.filter(
                ts_code__in=ts_code_list)

        for listed_company in listed_companies:
            last_date = last_download_date(
                listed_company.ts_code, 'HIST_DOWNLOAD', freq)
            # 下载数据
            if last_date is not None and len(last_date) > 1:
                handle_hist_download(
                    listed_company.ts_code, sdate=last_date[1], edate=today, freq=freq)
            else:
                handle_hist_download(
                    listed_company.ts_code, sdate=listed_company.list_date, edate=today, freq=freq)
        # 只记录交易日
        closest_trade_date = get_closest_trade_cal(today)
        # 标记九转序列
        handle_jiuzhuan_cp(None, freq=freq)
        # 标记斜率，顶底
        # handle_dingdi_cp(freq=freq)
        # 标记tupo
        # handle_tupo_cp(freq=freq)
        # 标记斜率，顶底
        # handle_mw_cp(freq=freq)
        # 标记均线
        handle_junxian_cp(None, freq=freq)
        # 存储选股结果?
        save_pick_result(strategy_code, closest_trade_date, freq=freq)
    except Exception as e:
        print(e)


def save_pick_result(strategy_code, pick_date, done_by=None, freq='D'):
    strategy_list = ['jiuzhuan_count_b', 'jiuzhuan_count_s', 'dingbu_s', 'dibu_b',
                     'tupo_b', 'diepo_s',  'm_ding', 'w_di',
                     'junxian25_zhicheng', 'junxian25_diepo', 'junxian25_yali', 'junxian25_tupo',
                     'junxian60_zhicheng', 'junxian60_diepo', 'junxian60_yali', 'junxian60_tupo',
                     'junxian200_zhicheng', 'junxian200_diepo', 'junxian200_yali', 'junxian200_tupo', ]

    df = pd.DataFrame.from_records(
        StockHistoryDaily.objects.filter(trade_date=pick_date, ))
    if strategy_code is not None:
        store_result(df, strategy_code, done_by, freq)
    else:
        for strategy in strategy_list:
            store_result(df, strategy, done_by, freq)


def store_result(df, strategy, done_by, freq='D'):
    picked_list = []
    if strategy.startswith('jiuzhuan_'):
        picked_df = df.loc[df[strategy] == 9]
    else:
        picked_df = df.loc[df[strategy] == 1]
    for index, row in picked_df.iterrows():
        picked_stocks = PickedStocksMeetStrategy(ts_code=row['ts_code'], trade_date=row['trade_date'], strategy_code=strategy,
                                                 test_freq=freq, done_by=done_by)
        picked_list.append(picked_stocks)
    PickedStocksMeetStrategy.object.bulk_create(picked_list)
