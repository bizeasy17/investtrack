

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
    print(ts_code_list)
    # end_date = date.today()
    periods = [10, 20, 30, 50, 80]

    # end_date = date.today()
    if len(ts_code_list) == 0 :
        listed_companies = StockNameCodeMap.objects.filter(
            is_hist_downloaded=True)
    else:
        listed_companies = StockNameCodeMap.objects.filter(
            is_hist_downloaded=True, ts_code__in=ts_code_list)
    print(len(listed_companies))
    hist_list = []
    if listed_companies is not None and len(listed_companies) > 0:
        for listed_company in listed_companies:
            hist_list = []
            print(' marked dingdi on start code - ' + listed_company.ts_code + ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            df = pd.DataFrame()
            if freq == 'D':
                df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=listed_company.ts_code).order_by('trade_date').values('id','trade_date','close','change','slope','dibu_b','dingbu_s'))
            else:
                pass
            if df is not None and len(df) > 0:
                pre_marked_df = pre_mark_dingdi(listed_company.ts_code, df)
                post_marked_df = post_mark_dingdi(pre_marked_df)
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
                print(' marked dingdi on end code - ' + listed_company.ts_code + ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return len(hist_list)  

def pre_mark_dingdi(ts_code, df):
    '''
    标记股票的顶底
    '''
    print('pre mark dingdi on code - ' + ts_code + ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(len(df))
    slope_deg3 = 0.05241
    slope_deg5 = 0.08749
    day_offset = 2
    slope_list = []
    dingdi_list = []
    try:
        for index, row in df.iterrows():
            # 股价与往前第四个交易日比较，如果<前值，那么开始计算九转买点，
            if index - day_offset < 0 or index + day_offset > len(df):
                slope_list.append(None)
                print(ts_code + ' on ' + row['trade_date'].strftime('%Y-%m-%d') + '/s slope is NaN')
                dingdi_list.append(False)
            else:
                offset_df = df[['close']].iloc[index - day_offset : index + day_offset]
                offset_df.reset_index(level=0, inplace=True)
                offset_df.columns=['ds','y']
                slope, intercept, r_value, p_value, std_err = stats.linregress(offset_df.ds, offset_df.y)
                slope_list.append(slope)
                if abs(slope) < slope_deg3:
                    print(ts_code + ' on ' + row['trade_date'].strftime('%Y-%m-%d') + '/s ding/di slope is ' + str(round(slope,5)))
                    dingdi_list.append(True)
                elif slope >=1:
                    print(ts_code + ' on ' + row['trade_date'].strftime('%Y-%m-%d') + '/s zhang slope is ' + str(round(slope,5)))
        df['slope'] = slope_list
        df['dingdi'] = dingdi_list
        print('pre mark dingdi end on code - ' + ts_code + ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        time.sleep(1)
        print(e)
    else:
        return df

def post_mark_dingdi(pre_marked_df, sequence_count):
    day_offset = 5
    slope_deg3 = 0.05241
    slope_deg5 = 0.08749
    dibu_b_list = []
    dingbu_s_list = []
    for index, row in pre_marked_df.iterrows():
        if row['slope'] is not None:
            if abs(row['slope']) <= slope_deg3:# 斜率<3°，认为是顶或者底
                offset_df = row[['slope']].iloc[index - sequence_count : index + day_offset]
                if stock_hist < 0: # 股价与往前第四个交易日比较，如果<前值，那么开始计算九转买点，
                    # 同时九转卖点设置为0
                    if count_b < 9:
                        count_b += 1
                    else:
                        count_b = 1
                    count_s = 0
                else:  # 股价与往前第四个交易日比较，如果>前值，那么开始计算九转卖点，
                    # 同时九转买点设置为0
                    if count_s < 9:
                        count_s += 1
                    else:
                        count_s = 1
                    count_b = 0
            dibu_b_list.append(count_b)
            dingbu_s_list.append(count_s)
        else:
            dingbu_s_list.append(True)
    pass