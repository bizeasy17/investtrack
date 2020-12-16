

import logging
import pandas as pd
from datetime import date, datetime, timedelta

from analysis.analysis_dingdi import handle_dingdi_cp
from analysis.analysis_jiuzhuan_cp import handle_jiuzhuan_cp
from analysis.models import PickedStocksMeetStrategy
from analysis.stock_hist import handle_hist_download
from analysis.utils import get_closest_trade_cal, last_download_date
from analysis.v2.mark_junxian_cp_v2 import pre_handle_jx
from stockmarket.models import StockNameCodeMap
from analysis.models import StockHistoryDaily
from analysis.utils import (generate_task, get_analysis_task,
                            get_trade_cal_diff, init_eventlog,
                            get_event_status, set_event_completed,
                            set_task_completed, set_event_exception)


def handle_stocks_pick(freq='D', force_run='0'):
    '''
    运行一遍下载，标记过程?
    '''
    try:
        exec_date = date.today()
        if exec_date.weekday() == 5:  # 周日推2天
            exec_date = exec_date - timedelta(days=1)
        elif exec_date.weekday == 6:
            exec_date = exec_date - timedelta(days=2)

        strategy_list = ['jiuzhuan_bs', 'dingdi', 'tupo_yali_b', 'diepo_zhicheng_s',
                         'wm_dingdi_bs', 'junxian25_bs', 'junxian60_bs', 'junxian200_bs']
        strategy_cp_list = {'jiuzhuan_bs': {'jiuzhuan_count_b', 'jiuzhuan_count_s'}, 'dingdi': {'dingbu_s', 'dibu_b'},
                            'tupo_yali_b': {'tupo_b'}, 'diepo_zhicheng_s': {'diepo_s'},  'wm_dingdi_bs': {'m_ding', 'w_di'},
                            'junxian25_bs': {'ma25_zhicheng', 'ma25_diepo', 'ma25_yali', 'ma25_tupo'},
                            'junxian60_bs': {'ma60_zhicheng', 'ma60_diepo', 'ma60_yali', 'ma60_tupo'},
                            'junxian200_bs': {'ma200_zhicheng', 'ma200_diepo', 'ma200_yali', 'ma200_tupo', }}

        evt_status = get_event_status('HIST_DOWNLOAD', exec_date)

        if evt_status == 1:  # 系统历史数据已经下载
            closest_trade_date = get_closest_trade_cal(exec_date)
            for strategy_code in strategy_list:
                evt_mk_status = get_event_status(
                    'MARK_CP', exec_date=exec_date, strategy_code=strategy_code, freq=freq)
                if evt_mk_status == 1:  # mark cp已经结束
                    evt_pk_status = get_event_status(
                        'PICK_STOCKS', strategy_code=strategy_code, exec_date=exec_date)
                    if evt_pk_status == 1:  # pick stock已经结束
                        print("pick stock is done already")
                    elif evt_pk_status == 0:  # pick stock 进行中
                        print("pick stock is still ongoing")
                    else:
                        init_eventlog('PICK_STOCKS',  exec_date=exec_date,
                                      strategy_code=strategy_code, freq=freq)
                        feed_marked_stock(strategy_code,
                                          strategy_cp_list[strategy_code], closest_trade_date, freq=freq)
                        set_event_completed('PICK_STOCKS', exec_date=exec_date,
                                            strategy_code=strategy_code, freq=freq)
                else:
                    print("previous marking is still ongoing or not run")
        else:
            if force_run == '1':
                closest_trade_date = get_closest_trade_cal(exec_date)

                for strategy_code in strategy_list:
                    print("picking stock started for " + strategy_code)
                    evt_mk_status = get_event_status(
                        'MARK_CP', exec_date=date.today(), strategy_code=strategy_code, freq=freq)
                    if evt_mk_status == 1:  # mark cp已经结束
                        init_eventlog('PICK_STOCKS',  exec_date=exec_date,
                                    strategy_code=strategy_code, freq=freq)
                        feed_marked_stock(strategy_code,
                                        strategy_cp_list[strategy_code], closest_trade_date, freq=freq)
                        set_event_completed('PICK_STOCKS', exec_date=exec_date,
                                            strategy_code=strategy_code, freq=freq)
                        print("picking stock finished for " + strategy_code)
            else:
                print("history has not yet downloade or still downloading")
    except Exception as e:
        print(e)
        set_event_exception('PICK_STOCKS', exec_date=exec_date,
                            strategy_code=strategy_code, freq=freq)
    # 标记九转序列
    # handle_jiuzhuan_cp(None, freq=freq)
    # 标记斜率，顶底
    # handle_dingdi_cp(freq=freq)
    # 标记tupo
    # handle_tupo_cp(freq=freq)
    # 标记斜率，顶底
    # handle_mw_cp(freq=freq)
    # 标记均线
    # handle_junxian_cp(None, freq=freq)
    # 存储选股结果?

# 目前无法手动单独执行


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
        pre_handle_jx(None, freq=freq)
        # 存储选股结果?
        feed_marked_stock(strategy_code, closest_trade_date, freq=freq)
    except Exception as e:
        print(e)


def feed_marked_stock(strategy_code, strategy_cp_codes, pick_date, done_by=None, freq='D'):
    # strategy_list = ['jiuzhuan_count_b', 'jiuzhuan_count_s', 'dingbu_s', 'dibu_b',
    #                  'tupo_b', 'diepo_s',  'm_ding', 'w_di',
    #                  'junxian25_zhicheng', 'junxian25_diepo', 'junxian25_yali', 'junxian25_tupo',
    #                  'junxian60_zhicheng', 'junxian60_diepo', 'junxian60_yali', 'junxian60_tupo',
    #                  'junxian200_zhicheng', 'junxian200_diepo', 'junxian200_yali', 'junxian200_tupo', ]

    df = pd.DataFrame.from_records(
        StockHistoryDaily.objects.filter(trade_date=pick_date).values())
    # if strategy_code is not None:
    for strategy_cp_code in strategy_cp_codes:
        store_result(df, strategy_cp_code, done_by, freq)
    # else:
    #     for strategy in strategy_list:
    #         store_result(df, strategy, done_by, freq)


def store_result(df, strategy, done_by='sys', freq='D'):
    picked_list = []
    if strategy.startswith('jiuzhuan_'):
        picked_df = df.loc[df[strategy] == 9]
    else:
        picked_df = df.loc[df[strategy] == 1]
    for index, row in picked_df.iterrows():
        picked_stocks = PickedStocksMeetStrategy(ts_code=row['ts_code'], trade_date=row['trade_date'], strategy_code=strategy,
                                                 test_freq=freq)
        picked_list.append(picked_stocks)
    if len(picked_list) > 0:
        PickedStocksMeetStrategy.objects.bulk_create(picked_list)
