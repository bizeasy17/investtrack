

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


def mark_junxian_bs_listed(freq, ts_code_list=[]):
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
                    'trade_date').values('id', 'trade_date', 'open', 'close', 'low', 'high', 'slope', 'ma25', 'ma60', 'di_min', 'ding_max'))
            else:
                pass
            if df is not None and len(df) > 0:
                # 标注顶底，未区分顶还是底，但顶底最后一个元素已标记
                pre_marked_df = mark_ma(listed_company.ts_code, df)
                post_marked_df = post_mark(
                    listed_company.ts_code, pre_marked_df, price_chg_3pct)
                # print(post_marked_df.tail(50))
                # for index, row in post_marked_df.iterrows():
                #     hist = object
                #     if freq == 'D':
                #         hist = StockHistoryDaily(pk=row['id'])
                #     else:
                #         pass
                #     # print(type(row['tupo_b']))
                #     hist.tupo_b = row['tupo_b'] if not math.isnan(row['tupo_b']) else None
                #     hist_list.append(hist)
                # if freq == 'D':
                #     StockHistoryDaily.objects.bulk_update(hist_list, ['tupo_b'])
                # else:
                #     pass
                # log_test_status(listed_company.ts_code, 'MARK_CP', freq, ['junxian_bs'])
                # listed_company.is_marked_junxian_bs = True
                # listed_company.save()
                print(' marked junxian bs on end code - ' + listed_company.ts_code +
                      ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                hist_list.clear()  # 清空已经保存的记录列表
    else:
        print('mark junxian bs for code - ' + str(ts_code_list) +
              ' marked already or not exist,' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return len(hist_list)


def mark_ma(ts_code, df):
    '''
    标记股票的ma
    '''
    print('pre mark ma25/60 started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        df['ma25'] = df['close'].rolling(window=25).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()
        print('pre ma25/60 end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        time.sleep(1)
        print(e)
    else:
        return df


def post_mark(ts_code, df, price_chg_pct):
    '''
    标记股票的ma b&s
    '''
    print('post mark junxian b&s started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        # MA zhicheng
        # df['open_ma25_pct'] = (df['open'] - df['ma25']).div(df['ma25'])
        # df['low_ma25_pct'] = (df['low'] - df['ma25']).div(df['ma25'])
        # df['close_ma25_pct'] = (df['close'] - df['ma25']).div(df['ma25'])
        # 计算支撑，股价底部趋势
        min_idx_list = df.loc[df['di_min'] == 1].index
        # 计算突破，股价需要在上升趋势
        up_idx_list = df.loc[df['slope'] > 0].index
        # 计算跌破，股价下跌趋势
        down_idx_list = df.loc[df['slope'] < 0].index
        # 计算MA压力，股价顶部趋势
        max_idx_list = df.loc[df['ding_max'] == 1].index

        # 计算支撑，股价底部趋势
        for min_idx in min_idx_list:
            low_pct = (df.loc[min_idx].ma25 -
                       df.loc[min_idx].low) / df.loc[min_idx].low
            if abs(low_pct) <= price_chg_pct and df.loc[min_idx].close > df.loc[min_idx].ma25:
                df.loc[min_idx, 'ma25_zhicheng_b'] = 1
                # print('ma25_zhicheng_b')

        # 计算突破，股价需要在上升趋势
        for up_idx in up_idx_list:
            close_pct = (df.loc[up_idx].close -
                         df.loc[up_idx].ma25) / df.loc[up_idx].ma25
            if abs(close_pct) >= price_chg_pct and df.loc[up_idx].low < df.loc[up_idx].ma25:
                df.loc[id, 'ma25_tupo_b'] = 1
                print(df.loc[up_idx].trade_date)

        # 计算跌破，股价下跌趋势
        for down_idx in down_idx_list:
            close_pct = (df.loc[down_idx].close -
                         df.loc[down_idx].ma25) / df.loc[down_idx].ma25
            if df.loc[down_idx].close < df.loc[down_idx].ma25 and df.loc[down_idx].open > df.loc[down_idx].ma25 and abs(close_pct) >= price_chg_pct:
                df.loc[id, 'ma25_diepo_s'] = 1
                print(df.loc[down_idx].trade_date)


        # 计算MA压力，股价顶部趋势
        for max_idx in max_idx_list:
            high_pct = (df.loc[max_idx].ma25 -
                       df.loc[max_idx].high) / df.loc[max_idx].high
            if df.loc[max_idx].close < df.loc[max_idx].ma25 and abs(high_pct) <= price_chg_pct:
                df.loc[id, 'ma25_yali_s'] = 1
                # print('ma25_yali_s')

        # print(len(slope_list))
        # print(len(dingdi_list))
        # print(len(dingdi_count_list))
        # print(len(end_dingdi_list))
        # df['w_di'] = w_di_list
        # df['m_tou'] = m_tou_list
        print('post mark ma b&s end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        time.sleep(1)
        print(e)
    else:
        return df
