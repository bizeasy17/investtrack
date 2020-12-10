

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
from .utils import (get_analysis_task, get_event_status, get_trade_cal_diff,
                    init_eventlog, set_event_completed, set_task_completed)

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


def pre_handle(ts_code, freq, slope_offset=2, slope_deg=0.05241, version='v1'):
    exec_date = date.today()
    evt_mk_status = get_event_status(
        'MARK_CP', 'dingdi', freq=freq)
    evt_dl_status = get_event_status('HIST_DOWNLOAD', freq=freq)

    if ts_code is None:
        if evt_dl_status == 0:
            print("previous downloading is still ongoing")
        elif evt_dl_status == -1:
            print("history has not yet been downloaded today")
        else:
            if evt_mk_status == 0:
                print("previous marking is still ongoing")
            elif evt_mk_status == 1:
                print("marking has been done today")
            else:
                init_eventlog('MARK_CP', 'dingdi', exec_date, freq=freq)
                handle_dingdi_cp(ts_code, freq, slope_offset,
                                 slope_deg, version)
                set_event_completed('MARK_CP', 'dingdi', exec_date, freq=freq)
    else:
        handle_dingdi_cp(ts_code, freq, slope_offset, slope_deg, version)


def handle_dingdi_cp(ts_code, freq, slope_offset=2, slope_deg=0.05241, version='v1'):
    '''
    同步策略在交易中的使用情况
    '''
    if ts_code is not None and freq is not None:
        start_date = None
        end_date = None
        # today = date.today()
        ts_code_list = ts_code.split(',')

        if ts_code_list is not None and len(ts_code_list) >= 1:
            for ts_code in ts_code_list:
                try:
                    listed_company = StockNameCodeMap.objects.get(
                        ts_code=ts_code)
                    task = get_analysis_task(
                        ts_code, 'MARK_CP', 'dingdi', freq)
                    if task is not None:
                        # 如何差额取之前的历史记录？9
                        atype = 1
                        if task.start_date == listed_company.list_date:
                            print('第一次处理，从上市日开始。。。')
                            atype = '0'  # 从上市日开始标记
                            start_date = task.start_date
                        else:
                            # q更新交易记录开始时间需要往前获取日期为MA周期的时间
                            print('更新处理，从上一次更新时间-2d offset day - 开盘日 开始...')
                            start_date = task.start_date - \
                                timedelta(days=get_trade_cal_diff(
                                    ts_code, task.start_date, period=int(slope_offset * 2)))  # 取2倍于计算slope的偏差的交易日数量，保证最后几个slope_offset的slope有值

                        mark_dingdi_listed(
                            freq, ts_code, start_date, task.end_date, slope_deg=slope_deg, atype=atype)

                        # print(task.start_date)
                        # # print(task.end_date)
                        set_task_completed(ts_code, 'MARK_CP',
                                           freq, 'dingdi', task.start_date, task.end_date)
                    else:
                        print('no mark dingdi cp task')
                except Exception as e:
                    print(e)


def mark_dingdi_listed(freq, ts_code, start_date, end_date, slope_offset=2, slope_deg=0.05241, atype='1'):
    '''
    对于未标注九转的上市股票运行一次九转序列标记，
    每次运行只是增量上市股票标记
    '''
    # print(ts_code_list)
    # end_date = date.today()
    # periods = [10, 20, 30, 50, 80]

    # print(len(listed_companies))
    hist_list = []
    print(' marked dingdi on start code - ' + ts_code +
          ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    df = pd.DataFrame()
    if freq == 'D':
        df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=ts_code, trade_date__gte=start_date, trade_date__lte=end_date).order_by(
            'trade_date').values('id', 'trade_date', 'close', 'slope', 'dibu_b', 'dingbu_s', 'is_dingdi_end', 'dingdi_count', 'ding_max', 'di_min'))
    else:
        pass
    if df is not None and len(df) > 0:
        # 标注顶底，未区分顶还是底，但顶底最后一个元素已标记
        pre_marked_df = pre_mark_dingdi(ts_code, df, day_offset=int(
            slope_offset), slope_deg=float(slope_deg))
        # 记录顶部还是底部的index，顶部的最大值的index，底部的最小值的index
        dingbu_s_list, dibu_b_list, ding_max_idx_list, di_min_idx_list = med_mark_dingdi(
            pre_marked_df, int(slope_offset), ts_code,)
        # 根据记录的index，生成完整的顶底，最大最小值生成相应的列数据
        post_marked_df = post_mark_dingdi(pre_marked_df, dingbu_s_list,
                                          dibu_b_list, ding_max_idx_list, di_min_idx_list, ts_code,)
        # 截取从task需要执行的时间对数据切片更新
        # if post_marked_df is not None and len(post_marked_df) > 0:
        #     post_marked_df = post_marked_df[df['trade_date'] >= start_date]
        # else:
        #     return
        start_index = 0
        if atype != '0':  # 更新MA CP标记
            start_index = slope_offset
        if post_marked_df is not None and len(post_marked_df) > 0:
            post_marked_df = post_marked_df[start_index:]
            # print(post_marked_df.tail(50))
            for index, row in post_marked_df.iterrows():
                hist = object
                if freq == 'D':
                    hist = StockHistoryDaily(pk=row['id'])
                else:
                    pass
                hist.dibu_b = row['dibu_b'] if row['dibu_b'] != 0 else None
                hist.dingbu_s = row['dingbu_s'] if row['dingbu_s'] != 0 else None
                hist.is_dingdi_end = row['is_dingdi_end'] if row['is_dingdi_end'] != 0 else None
                hist.dingdi_count = row['dingdi_count']
                hist.ding_max = row['ding_max'] if row['ding_max'] != 0 else None
                hist.di_min = row['di_min'] if row['di_min'] != 0 else None
                hist.slope = row['slope'] if row['slope'] != 0 else None
                hist_list.append(hist)
            if freq == 'D':
                StockHistoryDaily.objects.bulk_update(hist_list, [
                    'slope', 'dibu_b', 'dingbu_s', 'is_dingdi_end', 'dingdi_count', 'ding_max', 'di_min'])
            else:
                pass
            print(' marked dingdi on end code - ' + ts_code +
                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            hist_list.clear()  # 清空已经保存的记录列表
    else:
        print('dingdi for code - ' + ts_code +
              ' marked already or not exist,' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return len(hist_list)


def pre_mark_dingdi(ts_code, df, day_offset=2, slope_deg=0.05241):
    '''
    标记股票的顶底
    如果day_offset=2的话，会导致最后的2个交易日的slope为空，怎么解决？
    情况
    1. 上市开始
    2. 非上市日
        - 
    '''
    print('pre mark dingdi started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # print(len(df))
    # slope_deg5 = 0.08749
    slope = float()
    # day_offset = 2
    dingdi_count = 0
    is_dingdi = False
    is_end = False
    slope_list = []
    dingdi_list = []
    dingdi_count_list = []
    dingdi_end_list = []

    try:
        for index, row in df.iterrows():
            '''
            1. 前几个点
                slope = 0
            2. 中间的正常点
            3. 末尾几个点
                只会计算有限到序列结束为止的点的slope
            '''
            # 股价与往前第四个交易日比较，如果<前值，那么开始计算九转买点，
            try:
                offset_df = df[['close']].iloc[index -
                                               day_offset: index + day_offset]
                offset_df.reset_index(level=0, inplace=True)
                offset_df.columns = ['ds', 'y']
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    offset_df.ds, offset_df.y)
                # slope_list.append(slope)
                slope = round(slope, 3)
                if abs(slope) < slope_deg:
                    # if dingdi_count == 0:
                    #     start = True
                    dingdi_count += 1
                    is_dingdi = True
                    # print(ts_code + ' on ' + row['trade_date'].strftime(
                    #     '%Y-%m-%d') + '/s ding/di num:' + str(dingdi_count) + ' slope is ' + str(round(slope, 3)))
                    dingdi_end_list.append(0)
                else:
                    if dingdi_count > 0:
                        # index - 1 # 顶底最后一个元素的index
                        # dingdi_count # 符合顶底要求的个数
                        dingdi_end_list[len(dingdi_end_list)-1] = 1
                        # print(ts_code + ' on ' + row['trade_date'].strftime(
                        #     '%Y-%m-%d') + '/s ding/di index:' + str(index-1) + ' .num:' + str(dingdi_count) + ' slope is ' + str(round(slope, 3)))

                    dingdi_end_list.append(0)
                    dingdi_count = 0
            except Exception as e:
                slope = None
                dingdi_count = 0
                dingdi_end_list.append(0)

            # if index - day_offset < 0: #前几个交易日
            #     slope = None
            #     dingdi_count = 0
            #     dingdi_end_list.append(0)
            # else: #其他交易日
            #     if index + day_offset + 1 > len(df):#最后几个交易日，需要用来做选股用
            #         # print(ts_code + ' on ' +
            #         #       row['trade_date'].strftime('%Y-%m-%d') + '/s slope is NaN')
            #         # dingdi_list.append(False)
            #         offset_df = df[['close']].iloc[index -
            #                                     day_offset: index] #这些点在在之后会被重新修复计算
            #     else:
            #         offset_df = df[['close']].iloc[index -
            #                                     day_offset: index + day_offset]
            #     offset_df.reset_index(level=0, inplace=True)
            #     offset_df.columns = ['ds', 'y']
            #     slope, intercept, r_value, p_value, std_err = stats.linregress(
            #         offset_df.ds, offset_df.y)
            #     # slope_list.append(slope)
            #     slope = round(slope, 3)
            #     if abs(slope) < slope_deg:
            #         # if dingdi_count == 0:
            #         #     start = True
            #         dingdi_count += 1
            #         is_dingdi = True
            #         # print(ts_code + ' on ' + row['trade_date'].strftime(
            #         #     '%Y-%m-%d') + '/s ding/di num:' + str(dingdi_count) + ' slope is ' + str(round(slope, 3)))
            #         dingdi_end_list.append(0)

            #     # elif slope >=1:
            #     #     print(ts_code + ' on ' + row['trade_date'].strftime('%Y-%m-%d') + '/s zhang slope is ' + str(round(slope,5)))
            #     else:
            #         if dingdi_count > 0:
            #             # index - 1 # 顶底最后一个元素的index
            #             # dingdi_count # 符合顶底要求的个数
            #             dingdi_end_list[len(dingdi_end_list)-1] = 1
            #             # print(ts_code + ' on ' + row['trade_date'].strftime(
            #             #     '%Y-%m-%d') + '/s ding/di index:' + str(index-1) + ' .num:' + str(dingdi_count) + ' slope is ' + str(round(slope, 3)))

            #         dingdi_end_list.append(0)
            #         dingdi_count = 0
            #         # print(ts_code + ' on ' + row['trade_date'].strftime(
            #         #     '%Y-%m-%d') + '/s normal slope is ' + str(round(slope, 3)))
            #         # dingdi_list.append(False)
            slope_list.append(slope)
            dingdi_list.append(is_dingdi)
            dingdi_count_list.append(dingdi_count)

        # print(len(slope_list))
        # print(len(dingdi_list))
        # print(len(dingdi_count_list))
        # print(len(end_dingdi_list))
        df['slope'] = slope_list
        # df['dingdi'] = dingdi_list
        df['dingdi_count'] = dingdi_count_list
        df['is_dingdi_end'] = dingdi_end_list
        print('pre mark dingdi end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        time.sleep(1)
        print(e)
    else:
        return df


def med_mark_dingdi(pre_marked_df, compare_offset, ts_code):
    '''
    sample input
    000001.SZ on 2020-05-18/s ding/di num:1 slope is 0.015
    000001.SZ on 2020-05-19/s ding/di index:6897 .num:1 slope is 0.1
    000001.SZ on 2020-05-19/s normal slope is 0.1
    000001.SZ on 2020-05-20/s normal slope is 0.075
    000001.SZ on 2020-05-21/s normal slope is -0.143
    000001.SZ on 2020-05-22/s normal slope is -0.213
    000001.SZ on 2020-05-25/s normal slope is -0.104
    000001.SZ on 2020-05-26/s ding/di num:1 slope is 0.032
    000001.SZ on 2020-05-27/s ding/di num:2 slope is 0.029
    000001.SZ on 2020-05-28/s ding/di num:3 slope is -0.005
    000001.SZ on 2020-05-29/s ding/di index:6905 .num:3 slope is 0.089
    '''
    print('med mark dingdi start  - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    day_offset = 5
    slope_deg3 = 0.05241
    slope_deg5 = 0.08749
    ding_max_idx_list = []
    ding_max_list = []
    di_min_idx_list = []
    di_min_list = []
    dibu_b_list = []
    dingbu_s_list = []
    dingdi_index_list = []
    last_idx_list = pre_marked_df.loc[pre_marked_df['is_dingdi_end'] == 1].index
    # print(last_idx_list)
    try:
        for idx in last_idx_list:
            count = int(pre_marked_df['dingdi_count'].iloc[idx])
            left_slope = round(
                pre_marked_df['slope'].iloc[idx - count - compare_offset: idx - count].mean(), 3)
            right_slope = round(
                pre_marked_df['slope'].iloc[idx + 1: idx + compare_offset].mean(), 3)
            # print('left slope is' + str(left_slope) + ', right slope is ' + str(right_slope))
            # idx = 6878, count = 11
            # dingdi_idx = [6867(6878 - 11), 6878]
            dingdi_idx = [id for id in range(
                idx - count + 1, idx + 1)]
            if left_slope > 0 and right_slope < 0:
                # ding
                for i in dingdi_idx:
                    dingbu_s_list.append(i)
                ding_max_idx = pre_marked_df.iloc[dingdi_idx]['close'].astype(
                    'float').idxmax(axis=0)
                ding_max = pre_marked_df.iloc[dingdi_idx]['close'].astype(
                    'float').max(axis=0)
                ding_max_idx_list.append(ding_max_idx)
                ding_max_list.append(round(ding_max, 3))
                # pass
            elif left_slope < 0 and right_slope > 0:
                # di
                for i in dingdi_idx:
                    dibu_b_list.append(i)
                di_min_idx = pre_marked_df.iloc[dingdi_idx]['close'].astype(
                    'float').idxmin(axis=0)
                di_min = pre_marked_df.iloc[dingdi_idx]['close'].astype(
                    'float').min(axis=0)
                di_min_idx_list.append(di_min_idx)
                di_min_list.append(round(di_min, 3))
                # pass
    except Exception as e:
        print(e)
    print('med mark dingdi end  - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # print('ding max:')
    # print(ding_max_list)
    # print('di min:')
    # print(di_min_list)
    return dingbu_s_list, dibu_b_list, ding_max_idx_list, di_min_idx_list,


def post_mark_dingdi(med_marked_df, dingbu_s_idx_list, dibu_b_idx_list, ding_max_idx_list, di_min_idx_list, ts_code):
    print('post mark dingdi start  - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    dingbu_s_list = []
    dibu_b_list = []
    ding_max_list = []
    di_min_list = []
    for index, row in med_marked_df.iterrows():
        if index in dingbu_s_idx_list:
            dingbu_s_list.append(1)
        else:
            dingbu_s_list.append(0)

        if index in dibu_b_idx_list:
            dibu_b_list.append(1)
        else:
            dibu_b_list.append(0)

        if index in ding_max_idx_list:
            ding_max_list.append(1)
        else:
            ding_max_list.append(0)

        if index in di_min_idx_list:
            di_min_list.append(1)
        else:
            di_min_list.append(0)
    med_marked_df['dingbu_s'] = dingbu_s_list
    med_marked_df['dibu_b'] = dibu_b_list
    med_marked_df['ding_max'] = ding_max_list
    med_marked_df['di_min'] = di_min_list
    print('post mark dingdi end  - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return med_marked_df


def calculate_slope(df, offset=2):
    pass
