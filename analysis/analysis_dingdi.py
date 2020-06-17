

import pandas as pd
import numpy as np
import time
import logging
from scipy import stats
from datetime import date, datetime, timedelta
from investors.models import StockFollowing, TradeStrategy
from stockmarket.models import StockNameCodeMap
from .models import StockHistoryDaily, StockStrategyTestLog
from .utils import log_test_status
from .stock_hist import hist_since_listed

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


def recon_strategy_usage():
    '''
    同步策略在交易中的使用情况
    '''
    pass


def mark_dingdi_listed(freq, ts_code_list=[]):
    '''
    对于未标注九转的上市股票运行一次九转序列标记，
    每次运行只是增量上市股票标记
    '''
    # print(ts_code_list)
    # end_date = date.today()
    periods = [10, 20, 30, 50, 80]
    compare_offset = 2
    # end_date = date.today()
    if len(ts_code_list) == 0:
        listed_companies = StockNameCodeMap.objects.filter(
            is_hist_downloaded=True)
    else:
        listed_companies = StockNameCodeMap.objects.filter(
            is_hist_downloaded=True, ts_code__in=ts_code_list)
    # print(len(listed_companies))
    hist_list = []
    if listed_companies is not None and len(listed_companies) > 0:
        for listed_company in listed_companies:
            hist_list = []
            print(' marked dingdi on start code - ' + listed_company.ts_code +
                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            df = pd.DataFrame()
            if freq == 'D':
                df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=listed_company.ts_code).order_by(
                    'trade_date').values('id', 'trade_date', 'close', 'change', 'slope', 'dibu_b', 'dingbu_s'))
            else:
                pass
            if df is not None and len(df) > 0:
                pre_marked_df = pre_mark_dingdi(listed_company.ts_code, df)
                dingbu_s_list, dibu_b_list, ding_max_idx_list, di_min_idx_list = med_mark_dingdi(
                    pre_marked_df, compare_offset)
                post_marked_df = post_mark_dingdi(pre_marked_df, dingbu_s_list,
                                 dibu_b_list, ding_max_idx_list, di_min_idx_list)
                print(post_marked_df.tail(50))
                # for index, row in post_marked_df.iterrows():
                #     hist = object
                #     if freq == 'D':
                #         hist = StockHistoryDaily(pk=row['id'])
                #     else:
                #         pass
                #     hist.dibu_b = row['dibu_b']
                #     hist.dingbu_s = row['dingbu_s']
                #     hist_list.append(hist)
                # if freq == 'D':
                #     StockHistoryDaily.objects.bulk_update(hist_list, ['slope','dibu_b','dingbu_s'])
                # else:
                #     pass
                # log_test_status(listed_company.ts_code, 'MARK_CP', freq, ['dingbu_s','dibu_b'])
                # listed_company.is_marked_dingdi = True
                # listed_company.save()
                print(' marked dingdi on end code - ' + listed_company.ts_code +
                      ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return len(hist_list)


def pre_mark_dingdi(ts_code, df):
    '''
    标记股票的顶底
    '''
    print('pre mark dingdi on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # print(len(df))
    slope_deg3 = 0.05241
    slope_deg5 = 0.08749
    slope = object
    day_offset = 2
    dingdi_count = 0
    is_dingdi = False
    is_end = False
    slope_list = []
    dingdi_list = []
    dingdi_count_list = []
    dingdi_last_list = []
    try:
        for index, row in df.iterrows():
            # 股价与往前第四个交易日比较，如果<前值，那么开始计算九转买点，
            if index - day_offset < 0 or index + day_offset + 1 > len(df):
                # print(ts_code + ' on ' +
                #       row['trade_date'].strftime('%Y-%m-%d') + '/s slope is NaN')
                # dingdi_list.append(False)
                slope = 'NaN'
                dingdi_count = 0
                dingdi_last_list.append(0)
            else:
                offset_df = df[['close']].iloc[index -
                                               day_offset: index + day_offset]
                offset_df.reset_index(level=0, inplace=True)
                offset_df.columns = ['ds', 'y']
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    offset_df.ds, offset_df.y)
                # slope_list.append(slope)
                slope = slope
                if abs(slope) < slope_deg3:
                    # if dingdi_count == 0:
                    #     start = True
                    dingdi_count += 1
                    is_dingdi = True
                    # print(ts_code + ' on ' + row['trade_date'].strftime(
                    #     '%Y-%m-%d') + '/s ding/di num:' + str(dingdi_count) + ' slope is ' + str(round(slope, 3)))
                    dingdi_last_list.append(0)

                # elif slope >=1:
                #     print(ts_code + ' on ' + row['trade_date'].strftime('%Y-%m-%d') + '/s zhang slope is ' + str(round(slope,5)))
                else:
                    if dingdi_count > 0:
                        # index - 1 # 顶底最后一个元素的index
                        # dingdi_count # 符合顶底要求的个数
                        dingdi_last_list[len(dingdi_last_list)-1] = 1
                        # print(ts_code + ' on ' + row['trade_date'].strftime(
                        #     '%Y-%m-%d') + '/s ding/di index:' + str(index-1) + ' .num:' + str(dingdi_count) + ' slope is ' + str(round(slope, 3)))

                    dingdi_last_list.append(0)
                    dingdi_count = 0
                    # print(ts_code + ' on ' + row['trade_date'].strftime(
                    #     '%Y-%m-%d') + '/s normal slope is ' + str(round(slope, 3)))
                    # dingdi_list.append(False)
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
        df['is_dingdi_end'] = dingdi_last_list
        print('pre mark dingdi end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        time.sleep(1)
        print(e)
    else:
        return df


def med_mark_dingdi(pre_marked_df, compare_offset):
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
    print('med mark dingdi start ' +
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
    print(last_idx_list)
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
                ding_max_idx = pre_marked_df.iloc[dingdi_idx]['close'].astype('float').idxmax(axis=0)
                ding_max = pre_marked_df.iloc[dingdi_idx]['close'].astype('float').max(axis=0)
                ding_max_idx_list.append(ding_max_idx)
                ding_max_list.append(round(ding_max,3))
                # pass
            elif left_slope < 0 and right_slope > 0:
                # di
                for i in dingdi_idx:
                    dibu_b_list.append(i)
                di_min_idx = pre_marked_df.iloc[dingdi_idx]['close'].astype('float').idxmin(axis=0)
                di_min = pre_marked_df.iloc[dingdi_idx]['close'].astype('float').min(axis=0)
                di_min_idx_list.append(di_min_idx)
                di_min_list.append(round(di_min,3))
                # pass
    except Exception as e:
        print(e)
    print('post mark dingdi end ' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('ding max:')
    print(ding_max_list)
    print('di min:')
    print(di_min_list)
    return dingbu_s_list, dibu_b_list, ding_max_idx_list, di_min_idx_list,


def post_mark_dingdi(med_marked_df, dingbu_s_idx_list, dibu_b_idx_list, ding_max_idx_list, di_min_idx_list):
    print('post mark dingdi start ' +
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
    print('post mark dingdi end ' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return med_marked_df


