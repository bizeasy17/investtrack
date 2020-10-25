

import logging
import time
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from investors.models import StockFollowing, TradeStrategy
from scipy import stats
from stockmarket.models import StockNameCodeMap

from .models import StockHistoryDaily, StockStrategyTestLog
from .stock_hist import download_hist_data
from .utils import get_analysis_task, get_trade_cal_by_attr, set_task_completed

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


def handle_wm_cp(ts_code, freq, version):
    '''
    同步策略在交易中的使用情况
    '''
    if ts_code is not None and freq is not None:
        ts_code_list = ts_code.split(',')
        if ts_code_list is not None and len(ts_code_list) >= 1:
            # print(ts_code_list)
            for ts_code in ts_code_list:
                try:
                    listed_company = StockNameCodeMap.objects.get(
                        ts_code=ts_code)
                    task = get_analysis_task(
                        ts_code, 'MARK_CP', 'wm_dingdi_bs', freq)
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
                                    ts_code, task.start_date, ))

                        mark_wm_listed(ts_code, freq, start_date,
                                       task.end_date, atype)

                        # print(task.start_date)
                        # print(task.end_date)
                        set_task_completed(listed_company.ts_code, 'MARK_CP',
                                           freq, 'wm_dingdi_bs', task.start_date, task.end_date, atype)
                    else:
                        print('no wm_dingdi_bs mark cp task')
                except Exception as e:
                    print(e)
    pass


def mark_wm_listed(ts_code, freq, start_date, end_date, price_chg_pct=0.03, atype='1'):
    '''
    对于未标注支撑位买入的的上市股票标记，
    每次运行只是增量上市股票标记
    算法
    1. 查询获得所有底部买点（低点？）index
    2. 在给定的时间段periods = [10, 20, 30, 50, 80]内，向后搜索指定时间段内低点，
        2.1 如果在选定周期内的前低，价格波动在某一范围内（3%，5%，8%？），则当前底部买点就可标记为支撑位
    '''
    # print(ts_code_list)
    # end_date = date.today()
    # periods = [10, 20, 30, 50, 80]
    # price_chg_3pct = 0.03
    # price_chg_5pct = 0.05
    hist_list = []

    # end_date = date.today()
    print(' marked w, m on start code - ' + ts_code +
          ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    df = pd.DataFrame()
    if freq == 'D':
        df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=ts_code, trade_date__gte=start_date, trade_date__lte=end_date).order_by(
            'trade_date').values('id', 'trade_date', 'close', 'w_di', 'm_ding', 'ding_max', 'di_min'))
    else:
        pass
    start_index = 0
    if atype != 0:
        start_index = 0
    if df is not None and len(df) > 0:
        # 标注顶底，未区分顶还是底，但顶底最后一个元素已标记
        pre_marked_df = mark_wm(ts_code, df, price_chg_pct)
        # print(post_marked_df.tail(50))
        for index, row in pre_marked_df.iterrows():
            hist = object
            if freq == 'D':
                hist = StockHistoryDaily(pk=row['id'])
            else:
                pass
            hist.m_ding = row['m_ding']
            hist.w_di = row['w_di']
            hist_list.append(hist)
        if freq == 'D':
            StockHistoryDaily.objects.bulk_update(
                hist_list, ['w_di', 'm_ding'])
        else:
            pass
        print(' marked w or m on end code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        hist_list.clear()  # 清空已经保存的记录列表


def mark_wm(ts_code, df, price_chg_pct):
    '''
    标记股票的顶底
    '''
    print('pre mark w/m started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    w_di_list = []
    m_tou_list = []
    try:
        idx_list = df.loc[df['di_min'] == 1].index
        idx_prev = -1
        for id in idx_list:
            if idx_prev != -1:
                chg_pct = abs(df.loc[id].close -
                              df.loc[idx_prev].close) / df.loc[id].close
                if chg_pct <= price_chg_pct:
                    # print('w di found')
                    df.loc[id, 'w_di'] = 1
            idx_prev = id
        idx_list = df.loc[df['ding_max'] == 1].index
        idx_prev = -1
        for id in idx_list:
            if idx_prev != -1:
                chg_pct = abs(df.loc[id].close -
                              df.loc[idx_prev].close) / df.loc[id].close
                if chg_pct <= price_chg_pct:
                    # print('m ding found')
                    df.loc[id, 'm_ding'] = 1
            idx_prev = id

        # print(len(slope_list))
        # print(len(dingdi_list))
        # print(len(dingdi_count_list))
        # print(len(end_dingdi_list))
        # df['w_di'] = w_di_list
        # df['m_tou'] = m_tou_list
        print('pre mark w/m end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        time.sleep(1)
        print(e)
    else:
        return df


def update_wm_mark(ts_code, df, price_chg_pct):
    '''
    更新股票的w/m顶底
    '''
    print('update pre mark tupo b started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        idx_list = df.loc[df['ding_max'] == 1].index
        last_index = idx_list[-1]
        max_prev = df.loc[last_index].close
        # 跳过第一个顶的索引
        for index, row in df.loc[last_index:].iterrows():
            chg_pct = (max_prev - row['close']) / row['close']
            # slope >0 means 上涨趋势
            if row['slope'] > 0 and row['open'] < max_prev and chg_pct >= price_chg_pct:
                df.loc[index, 'tupo_b'] = 1
        print('update pre tupo b end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        time.sleep(1)
        print(e)
    else:
        return df
