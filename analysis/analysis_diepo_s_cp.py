

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
from .utils import (get_analysis_task, get_event_status, init_eventlog,
                    set_event_completed, set_task_completed, ready2proceed)

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


def pre_handle(ts_code, freq='D'):
    exec_date = date.today()

    if ts_code is None:
        if ready2proceed('wm_dingdi_bs', exec_date):
                init_eventlog('MARK_CP', 'diepo_zhicheng_s',
                              exec_date, freq=freq)
                handle_diepo_s(ts_code, freq)
                set_event_completed(
                    'MARK_CP', 'diepo_zhicheng_s', exec_date, freq=freq)
    else:
        handle_diepo_s(ts_code, freq)


def handle_diepo_s(freq, ts_code):
    '''
    对于未标注支撑位买入的的上市股票标记，
    每次运行只是增量上市股票标记
    算法
    1. 查询获得所有顶部卖点（高点？）index
    2. 循环所有高点，
        2.1 先前取一个高点，获取两个高点之间的所有slope>0 & 价格高于前高的点，
        2.2 如果在选定周期内的前低，价格高于前高一范围内（>3%，5%，8%？），则当前底部买点就可标记为突破点
    '''
    # print(ts_code_list)
    # end_date = date.today()
    # periods = [10, 20, 30, 50, 80]
    price_chg_3pct = 0.03
    price_chg_5pct = 0.05
    compare_offset = 2
    # end_date = date.today()
    if ts_code is not None:
        ts_code_list = ts_code.split(',')
        if len(ts_code_list) > 0:
            listed_companies = StockNameCodeMap.objects.filter(
                ts_code__in=ts_code_list)
    else:
        listed_companies = StockNameCodeMap.objects.filter()

    # print(len(listed_companies))
    hist_list = []
    if listed_companies is not None and len(listed_companies) > 0:
        for listed_company in listed_companies:
            print(' marked diepo s on start code - ' + listed_company.ts_code +
                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if has_analysis_task(listed_company.ts_code, 'MARK_CP', 'diepo_zhicheng_s', freq):
                df = pd.DataFrame()
                task = get_analysis_task(
                    listed_company.ts_code, 'MARK_CP', 'diepo_zhicheng_s', freq)
                if task.start_date == listed_company.list_date:  # 第一次下载历史数据
                    if freq == 'D':
                        df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=listed_company.ts_code).order_by(
                            'trade_date').values('id', 'trade_date', 'close', 'slope', 'di_min', 'open', 'high'))
                else:  # 历史数据更新
                    if freq == 'D':
                        last_di_min = StockHistoryDaily.objects.filter(ts_code=listed_company.ts_code, di_min=1).order_by(
                            'trade_date')[0]
                        if last_di_min is not None:
                            df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=listed_company.ts_code, trade_date__gte=last_di_min.trade_date, trade_date__lte=task.end_date).order_by(
                                'trade_date').values('id', 'trade_date', 'close', 'slope', 'di_min', 'open', 'close', 'high'))
                if df is not None and len(df) > 0:
                    # 标注顶底，未区分顶还是底，但顶底最后一个元素已标记
                    pre_marked_df = mark_diepo(
                        listed_company.ts_code, df, price_chg_3pct)
                    # 更新历史数据
                    if task.start_date != listed_company.list_date:
                        pre_marked_df = update_diepo_mark(
                            listed_company.ts_code, df, price_chg_3pct)
                    # print(post_marked_df.tail(50))
                    if 'diepo_s' in pre_marked_df.columns:
                        for index, row in pre_marked_df.iterrows():
                            hist = object
                            if freq == 'D':
                                hist = StockHistoryDaily(pk=row['id'])
                            else:
                                pass
                            # print(type(row['tupo_b']))
                            hist.diepo_s = row['diepo_s'] if not math.isnan(
                                row['diepo_s']) else None
                            hist_list.append(hist)
                        if freq == 'D':
                            StockHistoryDaily.objects.bulk_update(
                                hist_list, ['diepo_s'])
                        else:
                            pass

                        set_task_completed(listed_company.ts_code, 'MARK_CP',
                                           freq, 'diepo_zhicheng_s', task.start_date, task.end_date, atype)
                        print(' marked diepo s on end code - ' + listed_company.ts_code +
                              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        hist_list.clear()  # 清空已经保存的记录列表
                else:
                    print('mark diepo s for code - ' + str(ts_code_list) +
                          ' marked already ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    else:
        print(str(ts_code_list) +
              ' not exist - ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return len(hist_list)


def mark_diepo(ts_code, df, price_chg_pct):
    '''
    标记股票的顶底
    '''
    print('pre mark diepo s started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        idx_list = df.loc[df['di_min'] == 1].index
        idx_prev = -1
        for id in idx_list:
            if idx_prev != -1:  # slope >0 means 上涨趋势
                for idx_bwt in range(idx_prev+1, id):
                    # 收盘价和前低的比率
                    close_chg_pct = (
                        df.loc[idx_bwt].close - df.loc[idx_prev].close) / df.loc[idx_prev].close
                    # 最高价和前低的比率
                    high_chg_pct = (
                        df.loc[idx_bwt].high - df.loc[idx_prev].close) / df.loc[idx_prev].close
                    # 开盘价和前底的比率
                    open_chg_pct = (
                        df.loc[idx_bwt].open - df.loc[idx_prev].close) / df.loc[idx_prev].close
                    # print('close prev:'+str(df.loc[idx_prev].close)+',close:'+str(df.loc[idx_bwt].close)+',open:'+str(df.loc[idx_bwt].open)+',chg_pct:'+str(chg_pct))
                    # 判断跌破的依据
                    # 1. 下降通道 slope < 0 and
                    # 2. 当前收盘价 <= 前低3% or 5%? and
                    # 3. 最高价和前低相差 < 3% or 5%? or
                    # 4. 开盘价和前低相差 < 3% or 5%?
                    if df.loc[idx_bwt].slope < 0 and close_chg_pct <= -price_chg_pct and (high_chg_pct >= -price_chg_pct or open_chg_pct >= -price_chg_pct):
                        # pass
                        print(df.loc[idx_bwt].trade_date)
                        # print(df.loc[idx_bwt].close)
                        df.loc[idx_bwt, 'diepo_s'] = 1
                        # print('close pct:'+str(close_chg_pct)+',high pct:'+str(high_chg_pct)+',open pct:'+str(open_chg_pct))
                        # print('close prev:'+str(df.loc[idx_prev].close)+',close:'+str(df.loc[idx_bwt].close)+',open:'+str(df.loc[idx_bwt].open)+',chg_pct:'+str(close_chg_pct))
                        break
            idx_prev = id
        print('pre diepo s end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        time.sleep(1)
        print(e)
    else:
        return df


def update_diepo_mark(ts_code, df, price_chg_pct):
    '''
    标记股票的顶底
    '''
    print('update pre mark tupo b started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        idx_list = df.loc[df['di_min'] == 1].index
        last_index = idx_list[-1]
        min_prev = df.loc[last_index].close
        # 跳过第一个顶的索引
        for index, row in df.loc[last_index:].iterrows():
            chg_pct = (min_prev - row['close']) / min_prev
            # slope <0 means 下跌趋势
            if row['slope'] < 0 and row['open'] > min_prev and chg_pct >= price_chg_pct:
                df.loc[index, 'diepo_s'] = 1
        print('update pre tupo b end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        time.sleep(1)
        print(e)
    else:
        return df
