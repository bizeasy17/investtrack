

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
from .utils import log_test_status,is_strategy_tested
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


def mark_die_pct_listed(freq, ts_code_list=[]):
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
        listed_companies = StockNameCodeMap.objects.filter(is_hist_downloaded=True)
    else:
        listed_companies = StockNameCodeMap.objects.filter(is_hist_downloaded=True, ts_code__in=ts_code_list)
    # print(len(listed_companies))
    hist_list = []
    if listed_companies is not None and len(listed_companies) > 0:
        for listed_company in listed_companies:
            if not is_strategy_tested(listed_company.ts_code, 'MARK_CP', 'die_pct', freq):
                print(' marked die pct on start code - ' + listed_company.ts_code +
                    ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                df = pd.DataFrame()
                if freq == 'D':
                    df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=listed_company.ts_code).order_by(
                        'trade_date').values('id', 'trade_date', 'close', 'slope', 'ding_max'))
                else:
                    pass
                if df is not None and len(df) > 0:
                    # 标注顶底，未区分顶还是底，但顶底最后一个元素已标记
                    pre_marked_df = mark_die_pct(listed_company.ts_code, df)
                    # print(post_marked_df.tail(50))
                    # for index, row in pre_marked_df.iterrows():
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
                    # log_test_status(listed_company.ts_code, 'MARK_CP', freq, ['die_pct'])
                    # listed_company.is_marked_tupo = True
                    # listed_company.save()
                    print(' marked die pct on end code - ' + listed_company.ts_code +
                        ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    hist_list.clear() # 清空已经保存的记录列表
            else:
                print('mark die pct for code - ' + str(ts_code_list) +
                            ' marked already ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    else:
        print('mark die pct for code - ' + str(ts_code_list) +
                      ' not exist,' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return len(hist_list)

def get_down_pct_idx(df, prev_close, pct_down):
    offset = 0.1
    try:
        # down_pct = (df['close'] > prev_close) / df.loc[id].close
        # print(pct_down)
        # print('prev close:'+str(prev_close))
        # print('up:'+str((1-(pct_down+offset)/100) * prev_close)) #bigger
        # print('down:'+str((1-(pct_down-offset)/100) * prev_close))#small
        down_pct = df[(df['slope'] < 0) & (df['close'] >= (1-(pct_down+offset)/100) * prev_close) &
                          (df['close'] <= (1-(pct_down-offset)/100) * prev_close)]  # ??方法是否对？
        # pct_date = closest_date[0].strptime('%Y%m%d')
        # if len(down_pct)>0: print(down_pct.id)
        print(down_pct.index)
        # if len(down_pct)>0:
        #     print(down_pct)
        pct_idx = down_pct.index[0]
    except Exception as e:
        # logger.error(e)
        # print('inner')
        # print(e)
        pct_idx = None
    return pct_idx

def mark_die_pct(ts_code, df):
    '''
    标记股票的down pct
    '''
    offset = 1
    down_pct_list = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    print('pre mark die pct started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        idx_list = df.loc[df['ding_max'] == 1].index
        idx_prev = -1
        for id in idx_list:
            if idx_prev != -1: # slope >0 means 上涨趋势
                for pct_down in down_pct_list:
                    idx_match = get_down_pct_idx(df[idx_prev+offset:id-offset], df.loc[idx_prev].close, pct_down)
                    if idx_match is not None:
                        df.loc[idx_match, 'ding_die_'+str(pct_down)+'pct'] = 1
                        # pass df.loc[idx_bwt].slope > 0 and
                        print('ding')
                        print(df.loc[idx_prev].trade_date)
                        print('match')
                        print(df.loc[idx_match].trade_date)
                        print(pct_down)
                        # print('prev:'+str(df.loc[id].close))
                        # print('match:'+str(df.loc[idx_match].close))
            idx_prev = id
        # print(df.head(-50))
        print('pre die pct end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        time.sleep(1)
        # print('outter')
        print(e)
    else:
        return df