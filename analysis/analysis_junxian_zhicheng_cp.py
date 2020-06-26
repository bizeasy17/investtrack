

import pandas as pd
import numpy as np
import time
import math
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


def mark_junxian_zhicheng_listed(freq, ts_code_list=[]):
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
    if len(ts_code_list) == 0:
        listed_companies = StockNameCodeMap.objects.filter(
            is_hist_downloaded=True, is_marked_tupo=None)
    else:
        listed_companies = StockNameCodeMap.objects.filter(
            is_hist_downloaded=True, is_marked_tupo=None, ts_code__in=ts_code_list)
    # print(len(listed_companies))
    hist_list = []
    if listed_companies is not None and len(listed_companies) > 0:
        for listed_company in listed_companies:
            print(' marked junxian zhicheng on start code - ' + listed_company.ts_code +
                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            df = pd.DataFrame()
            if freq == 'D':
                df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=listed_company.ts_code).order_by(
                    'trade_date').values('id', 'trade_date', 'close', 'slope', 'ma25'))
            else:
                pass
            if df is not None and len(df) > 0:
                # 标注顶底，未区分顶还是底，但顶底最后一个元素已标记
                pre_marked_df = mark_zhicheng(listed_company.ts_code, df, price_chg_3pct)
                # print(post_marked_df.tail(50))
                for index, row in pre_marked_df.iterrows():
                    hist = object
                    if freq == 'D':
                        hist = StockHistoryDaily(pk=row['id'])
                    else:
                        pass
                    # print(type(row['tupo_b']))
                    hist.tupo_b = row['tupo_b'] if not math.isnan(row['tupo_b']) else None
                    hist_list.append(hist)
                if freq == 'D':
                    StockHistoryDaily.objects.bulk_update(hist_list, ['tupo_b'])
                else:
                    pass
                log_test_status(listed_company.ts_code, 'MARK_CP', freq, ['tupo_b'])
                listed_company.is_marked_wm = True
                listed_company.save()
                print(' marked tupo b on end code - ' + listed_company.ts_code +
                      ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                hist_list.clear() # 清空已经保存的记录列表
    else:
        print('mark tupo b for code - ' + str(ts_code_list) +
                      ' marked already or not exist,' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return len(hist_list)


def mark_zhicheng(ts_code, df, price_chg_pct):
    '''
    标记股票的顶底
    '''
    print('pre mark tupo b started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        idx_list = df.loc[df['ding_max'] == 1].index
        idx_prev = -1
        for id in idx_list:
            if idx_prev != -1: # slope >0 means 上涨趋势
                for idx_bwt in range(idx_prev, id):
                    chg_pct = abs(df.loc[idx_bwt].close > df.loc[id].close) / df.loc[id].close
                    if df.loc[idx_bwt].slope > 0 and chg_pct >= price_chg_pct:
                        # pass
                        # print(df.loc[idx_bwt].trade_date)
                        # print(df.loc[idx_bwt].close)

                        df.loc[idx_bwt, 'tupo_b'] = 1
            idx_prev = id
        print('pre tupo b end on code - ' + ts_code +
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


