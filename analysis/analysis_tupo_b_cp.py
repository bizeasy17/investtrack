

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
from .utils import log_test_status, has_analysis_task
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


def mark_tupo_yali_listed(freq, ts_code_list=[]):
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
            if has_analysis_task(listed_company.ts_code, 'MARK_CP', 'tupo_yanli_b', freq):
                print(' marked tupo b on start code - ' + listed_company.ts_code +
                    ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                task = get_analysis_task(
                    listed_company.ts_code, 'MARK_CP', 'tupo_yanli_b', freq)
                df = pd.DataFrame()
                if task.start_date == listed_company.list_date: #第一次下载历史数据
                    if freq == 'D':
                        df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=listed_company.ts_code).order_by(
                            'trade_date').values('id', 'trade_date', 'close', 'slope', 'm_ding', 'ding_max'))
                else: # 历史数据更新
                    if freq == 'D':
                        last_ding_max = StockHistoryDaily.objects.filter(ts_code=listed_company.ts_code, ding_max=1).order_by(
                            'trade_date')[0]
                        if last_ding_max is not None:
                            df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=listed_company.ts_code, trade_date__gte=last_ding_max.trade_date, trade_date__lte=task.end_date).order_by(
                                'trade_date').values('id', 'trade_date', 'close', 'slope', 'm_ding', 'ding_max'))
                if df is not None and len(df) > 0:
                    # 标注顶底，未区分顶还是底，但顶底最后一个元素已标记
                    pre_marked_df = mark_tupo(listed_company.ts_code, df, price_chg_3pct)
                    if task.start_date != listed_company.list_date: #更新历史数据
                        pre_marked_df = update_tupo_mark(listed_company.ts_code, df, price_chg_3pct)
                    # print(post_marked_df.tail(50))
                    if 'tupo_b' in pre_marked_df.columns:
                        for index, row in pre_marked_df.iterrows():
                            hist = object
                            if freq == 'D':
                                hist = StockHistoryDaily(pk=row['id'])
                            else:
                                pass
                            # print(type(row['tupo_b']))calibrate_realtime_position
                            hist.tupo_b = row['tupo_b'] if not math.isnan(row['tupo_b']) else None
                            hist_list.append(hist)
                        if freq == 'D':
                            StockHistoryDaily.objects.bulk_update(hist_list, ['tupo_b'])
                        else:
                            pass
                        log_test_status(listed_company.ts_code, 'MARK_CP', freq, ['tupo_yali_b'])
                        listed_company.is_marked_tupo = True
                        listed_company.save()
                        print(' marked tupo b on end code - ' + listed_company.ts_code +
                            ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        hist_list.clear() # 清空已经保存的记录列表
    else:
        print('mark tupo b for code - ' + str(ts_code_list) +
                      ' marked already or not exist,' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return len(hist_list)


def mark_tupo(ts_code, df, price_chg_pct):
    '''
    标记股票的顶底
    '''
    print('pre mark tupo b started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        idx_list = df.loc[df['ding_max'] == 1].index
        idx_prev = -1
        for id in idx_list:
            if idx_prev != -1: # 跳过第一个顶的索引
                for idx_bwt in range(idx_prev, id):
                    chg_pct = (df.loc[idx_bwt+1].close - df.loc[id].close) / df.loc[id].close
                    if df.loc[idx_bwt].slope > 0 and chg_pct >= price_chg_pct:# slope >0 means 上涨趋势
                        # pass
                        # print(df.loc[idx_bwt].trade_date)
                        # print(df.loc[idx_bwt].close)

                        df.loc[idx_bwt, 'tupo_b'] = 1
                        break
            idx_prev = id
        print('pre tupo b end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        time.sleep(1)
        print(e)
    else:
        return df

def update_tupo_mark(ts_code, df, price_chg_pct):
    '''
    标记股票的顶底
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
            if row['slope'] > 0 and row['open'] < max_prev and chg_pct >= price_chg_pct:# slope >0 means 上涨趋势
                df.loc[index, 'tupo_b'] = 1
        print('update pre tupo b end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        time.sleep(1)
        print(e)
    else:
        return df