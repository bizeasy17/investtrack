

import logging
import math
import time
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from investors.models import StockFollowing, TradeStrategy
from scipy import stats
from stockmarket.models import StockNameCodeMap

from .models import StockHistoryDaily, StockStrategyTestLog
from .stock_hist import download_hist_data
from .utils import (get_analysis_task, get_event_status, get_trade_cal_by_attr,
                    init_eventlog, ready2proceed, set_event_completed,
                    set_task_completed)

logger = logging.getLogger(__name__)

# def trade_calendar(exchange, start_date, end_date):
#     # 获取20200101～20200401之间所有有交易的日期
#     pro = ts.pro_api()
#     df = pro.trade_cal(exchange=exchange, is_open='1',
#                        start_date=start_date,
#                        end_date=end_date,
#                        fields='cal_date')
#     return df
#     # print(df.head())


def pre_handle(ts_code, freq, price_chg_pct=0.03, version='1'):
    exec_date = date.today()

    if ts_code is None:
        if ready2proceed('tupo_yali_b', freq):
            init_eventlog('MARK_CP', 'tupo_yali_b', exec_date, freq=freq)
            handle_tupo_cp(ts_code, freq, price_chg_pct, version)
            set_event_completed(
                'MARK_CP', 'tupo_yali_b', exec_date, freq=freq)
    else:
        handle_tupo_cp(ts_code, freq, price_chg_pct, version)


def handle_tupo_cp(ts_code, freq, price_chg_pct=0.03, version='1'):
    '''
    同步策略在交易中的使用情况
    '''
    ts_code_list = ts_code.split(',')
    if ts_code_list is not None and len(ts_code_list) >= 1:
        # print(ts_code_list)
        for ts_code in ts_code_list:
            try:
                listed_company = StockNameCodeMap.objects.get(
                    ts_code=ts_code)
                task = get_analysis_task(
                    ts_code, 'MARK_CP', 'tupo_yali_b', freq)
                if task is not None:
                    atype = '1'  # 标记更新的股票历史记录
                    # 如何差额取之前的历史记录？9
                    if task.start_date == listed_company.list_date:
                        print('第一次处理，从上市日开始。。。')
                        atype = '0'  # 从上市日开始标记
                        start_date = task.start_date
                    else:
                        print('更新处理，从上一次更新时间-4d - 开盘日 开始...')
                        start_date = task.start_date - \
                            timedelta(days=get_trade_cal_by_attr(
                                ts_code, task.start_date, attr='ding_max'))

                    mark_tupo_yali_listed(ts_code, freq, start_date,
                                            task.end_date, task.start_date, price_chg_pct, atype)

                    # print(task.start_date)
                    # print(task.end_date)
                    set_task_completed(listed_company.ts_code, 'MARK_CP',
                                        freq, 'tupo_yali_b', task.start_date, task.end_date)
                else:
                    print('no tupo_b mark cp task')
            except Exception as e:
                print(e)


def mark_tupo_yali_listed(ts_code, freq, start_date, end_date, task_start, price_chg_pct=0.03, atype='1'):
    '''
    对于未标注支撑位买入的的上市股票标记，
    每次运行只是增量上市股票标记
    算法
    1. 查询获得所有顶部卖点（高点？）index
    2. 循环所有高点，
        2.1 先前取一个高点，获取两个高点之间的所有slope>0 & 价格高于前高的点，
        2.2 如果在选定周期内的前低，价格高于前高一范围内（>3%，5%，8%？），则当前底部买点就可标记为突破点
    '''
    hist_list = []
    print(' marked tupo b on start code - ' + ts_code +
          ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    df = pd.DataFrame()
    if freq == 'D':
        # last_ding_max = StockHistoryDaily.objects.filter(ts_code=ts_code, ding_max=1).order_by(
        #     'trade_date')[0]
        df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=ts_code, trade_date__gte=start_date, trade_date__lte=end_date).order_by(
            'trade_date').values('id', 'trade_date', 'open', 'close', 'slope', 'm_ding', 'ding_max'))
    if df is not None and len(df) > 0:
        # 标注所有高点之间的突破点
        last_ding_index = mark_tupo_bwt_ding(ts_code, df, price_chg_pct)
        # 标注尾部的收盘价和前一高点是否突破
        tail_tupo_mark(ts_code, df, last_ding_index=last_ding_index,
                       price_chg_pct=price_chg_pct)
        # start_index = 0
        if atype == '1':  # 用于更新
            # start_index = 0  # ???
            df = df[df['trade_date'] >= task_start]
        # else: #更新历史数据
        #     pre_marked_df = update_tupo_mark(ts_code, df, price_chg_pct)
        #     post_tupo_mark(ts_code, df, last_ding_index = 1, price_chg_pct=price_chg_pct)
        # print(post_marked_df.tail(50))
        if 'tupo_b' in df.columns:
            for index, row in df.iterrows():
                hist = object
                if freq == 'D':
                    hist = StockHistoryDaily(pk=row['id'])
                else:
                    pass
                # print(type(row['tupo_b']))calibrate_realtime_position
                hist.tupo_b = row['tupo_b'] if not math.isnan(
                    row['tupo_b']) else None
                hist_list.append(hist)
            if freq == 'D':
                StockHistoryDaily.objects.bulk_update(hist_list, ['tupo_b'])
            else:
                pass
            print(' marked tupo b on end code - ' + ts_code +
                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            hist_list.clear()  # 清空已经保存的记录列表
    else:
        print('mark tupo b for code - ' + str(ts_code) +
              ' marked already or not exist,' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return len(hist_list)


def mark_tupo_bwt_ding(ts_code, df, price_chg_pct):
    '''
    标记股票的顶底
    '''
    print('pre mark tupo b started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        idx_list = df.loc[df['ding_max'] == 1].index
        idx_prev = -1
        for id in idx_list:
            # max_prev = df.loc[id].close
            if idx_prev != -1:  # 跳过第一个顶的索引
                print(range(idx_prev, id))
                for idx_bwt in range(idx_prev+1, id):
                    chg_pct = (df.loc[idx_bwt].close -
                               df.loc[idx_prev].close) / df.loc[idx_prev].close
                    # slope >0 means 上涨趋势
                    if df.loc[idx_bwt].open < df.loc[idx_prev].close and df.loc[idx_bwt].close > df.loc[idx_prev].close and chg_pct >= price_chg_pct:
                        # pass
                        print(df.loc[idx_prev].trade_date)
                        print(df.loc[idx_prev].close)
                        print(df.loc[idx_bwt].trade_date)
                        print(df.loc[idx_bwt].close)
                        print(df.loc[idx_bwt].open)

                        df.loc[idx_bwt, 'tupo_b'] = 1
            idx_prev = id
        print('pre tupo b end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return idx_prev
    except Exception as e:
        print(e)


def tail_tupo_mark(ts_code, df, last_ding_index, price_chg_pct):
    '''
    遍历从最后一个高点开始，到end_date的收盘价，是否有突破点
    '''
    print('update tail mark tupo b started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        prev_close = df.loc[last_ding_index].close
        trade_date = df.loc[last_ding_index].trade_date

        # 跳过第一个顶的索引
        for index, row in df.loc[last_ding_index:].iterrows():
            chg_pct = (row['close'] - prev_close) / prev_close
            # slope >0 means 上涨趋势
            if row['open'] < prev_close and row['close'] > prev_close and chg_pct >= price_chg_pct:
                print(trade_date)
                print(prev_close)
                print(row['trade_date'])
                print(row['close'])
                print(row['open'])
                df.loc[index, 'tupo_b'] = 1
        print('update tail tupo b end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        print(e)
    pass
