

import pandas as pd
import numpy as np
import time
import math
import logging
from scipy import stats
from datetime import date, datetime, timedelta
from stockmarket.models import StockNameCodeMap
from investors.models import StockFollowing, TradeStrategy
from analysis.models import StockHistoryDaily, StockStrategyTestLog
from analysis.utils import log_test_status, is_analyzed, get_analysis_task
from analysis.stock_hist import download_hist_data
from .utils import mark_mov_avg, calculate_slope
from analysis.utils import is_analyzed, get_analysis_task, get_trade_cal_diff,set_task_completed

logger = logging.getLogger(__name__)
version = 'v2'
# def trade_calendar(exchange, stadf_slc_date, end_date):
#     # 获取20200101～20200401之间所有有交易的日期
#     pro = ts.pro_api()
#     df = pro.trade_cal(exchange=exchange, is_open='1',
#                        start_date=start_date,
#                        end_date=edf_slc_date,
#                        fidf_slcds='cal_date')
#     return df
#     # print(df.head())

def handle_junxian_cp(ts_code, freq='D', ma_freq='25', version='v1', days_offset=2):    
    if ts_code is not None and freq is not None:
        start_date = None
        end_date = None
        today = date.today()
        ts_code_list = ts_code.split(',')

        if ts_code_list is not None and len(ts_code_list) >= 1:
            for ts_code in ts_code_list:
                try:
                    listed_company = StockNameCodeMap.objects.get(
                        ts_code=ts_code)
                    task = get_analysis_task(
                        ts_code, 'MARK_CP', 'junxian'+ma_freq+'_bs', freq)
                    if task is not None:
                        atype = '1'  # 标记更新的股票历史记录
                        # 如何差额取之前的历史记录？9
                        if task.start_date == listed_company.list_date:
                            print('第一次处理，从上市日开始。。。')
                            atype = '0'  # 从上市日开始标记
                            start_date = task.start_date
                        else:
                            #q更新交易记录开始时间需要往前获取日期为MA周期的时间
                            print('更新处理，从上一次更新时间-25,60,200d - 开盘日 开始...')
                            start_date = task.start_date - timedelta(days=get_trade_cal_diff(ts_code, task.start_date, period=int(ma_freq)+days_offset))

                        mark_junxian_cp(ts_code, start_date, task.end_date, ma_freq=ma_freq, atype=atype)

                        # print(task.start_date)
                        # # print(task.end_date)
                        # set_task_completed(ts_code, 'MARK_CP',
                        #                    freq, 'junxian'+ma_freq+'_bs', task.start_date, task.end_date)
                    else:
                        print('no jiuzhuan mark cp task')
                except Exception as e:
                    print(e)

def mark_junxian_since_listed(ts_code, list_date, freq='D', ma_freq='25', price_chg_pct=0.03, slope_deg=0.05241, day_offset=2, version='v2', atype='system'):
    '''
    目标：
    参数化分析均线，可能对结果有影响的参数
    - 价格变化
    - 斜率
    - 计算斜率所要考虑的连续的天数（前几天，后几天）
    '''
    print('marked junxian zhicheng on start code - ' + ts_code +
          ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    if not is_analyzed(ts_code, 'MARK_CP', 'junxian'+ma_freq+'_bs_'+version, freq):
        df = None
        hist_list = []
        if freq == 'D':
            df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=ts_code, trade_date__gte=list_date).order_by(
                'trade_date').values('id', 'trade_date', 'open', 'close', 'low', 'high', 'slope'))
            # print(df.head())
        else:
            pass
        if df is not None and len(df) > 0:
            # 标记均线
            mark_mov_avg(ts_code, df, ma_freq)
            # 标记均线关键点
            mark_ma_cp(price_chg_pct, df, ma_freq, version)
            # 计算斜率
            df.loc[:int(ma_freq)-1, 'ma'+ma_freq+"_slope"] = np.nan
            offset_df = df[int(ma_freq):]
            calculate_slope(df, offset_df, ts_code, col='ma' +
                       ma_freq, slope_col='ma'+ma_freq+'_slope')
            # 存储结果
            # df = df[int(ma_freq)-1:] #q只对
            for index, row in df.iterrows():
                hist = object
                if freq == 'D':
                    if atype == 'system':
                        hist = StockHistoryDaily(pk=row['id'])
                    else:
                        pass
                else:
                    pass
                # print(str(row['trade_date']) + ' ' + str(row['ma'+ma_freq+'_slope']))
                setattr(hist, 'ma'+ma_freq, row['ma'+ma_freq] if not math.isnan(
                    row['ma'+ma_freq]) else None)
                setattr(hist, 'ma'+ma_freq+'_slope', round(row['ma'+ma_freq+'_slope'], 3) if not math.isnan(
                    row['ma'+ma_freq+'_slope']) else None)
                setattr(hist, 'ma'+ma_freq+'_zhicheng_'+version, round(row['ma'+ma_freq+'_zhicheng_'+version], 3) if not math.isnan(
                    row['ma'+ma_freq+'_zhicheng_'+version]) else None)
                setattr(hist, 'ma'+ma_freq+'_tupo_'+version, round(row['ma'+ma_freq+'_tupo_'+version], 3) if not math.isnan(
                    row['ma'+ma_freq+'_tupo_'+version]) else None)
                setattr(hist, 'ma'+ma_freq+'_diepo_'+version, round(row['ma'+ma_freq+'_diepo_'+version], 3) if not math.isnan(
                    row['ma'+ma_freq+'_diepo_'+version]) else None)
                setattr(hist, 'ma'+ma_freq+'_yali_'+version, round(row['ma'+ma_freq+'_yali_'+version], 3) if not math.isnan(
                    row['ma'+ma_freq+'_yali_'+version]) else None)
                hist_list.append(hist)
            if freq == 'D':
                if atype == 'system':
                    StockHistoryDaily.objects.bulk_update(hist_list, ['ma'+ma_freq,
                                                                      'ma'+ma_freq+'_slope',
                                                                      'ma'+ma_freq+'_zhicheng_'+version,
                                                                      'ma'+ma_freq+'_tupo_'+version,
                                                                      'ma'+ma_freq+'_diepo_'+version,
                                                                      'ma'+ma_freq+'_yali_'+version])
                else:
                    pass
            else:
                pass
            log_test_status(ts_code,
                            'MARK_CP', freq, ['junxian'+ma_freq+'_bs_'+version])
            # listed_company.is_marked_junxian_bs = True
            # listed_company.save()
            print(' marked junxian bs on end code - ' + ts_code +
                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            hist_list.clear()  # 清空已经保存的记录列表
    else:
        print('no junxian cp task')
    # else:
    #     print('mark junxian bs for code - ' + str(ts_code_list) +
        #   ' marked already or not exist,' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return len(hist_list)


def update_junxian_cp(ts_code, last_upd_date, freq='D', ma_freq='25', atype='1', price_chg_pct=0.03, slope_deg=0.05241, day_offset=2, version='v2', done_by='system'):
    '''
    目标：
    参数化分析均线，可能对结果有影响的参数
    - 价格变化
    - 斜率
    - 计算斜率所要考虑的连续的天数（前几天，后几天）
    '''
    print('update junxian zhicheng on start code - ' + ts_code +
          ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    if not is_analyzed(ts_code, 'UPD_MARK_CP', 'junxian'+ma_freq+'_bs_'+version, freq):
        df = None
        hist_list = []
        if freq == 'D':
            df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=ts_code, trade_date__gte=last_upd_date - timedelta(days=int(ma_freq))).order_by(
                'trade_date').values('id', 'trade_date', 'open', 'close', 'low', 'high', 'slope'))
            # print(df.head())
        else:
            pass
        if df is not None and len(df) > 0:
            # 标记均线
            mark_mov_avg(ts_code, df, ma_freq)
            # 标记均线关键点
            mark_ma_cp(price_chg_pct, df, ma_freq, version)
            # 计算斜率
            df.loc[:int(ma_freq)-1, 'ma'+ma_freq+"_slope"] = np.nan
            offset_df = df[int(ma_freq):]
            calculate_slope(df, offset_df, ts_code, col='ma' +
                       ma_freq, slope_col='ma'+ma_freq+'_slope')
            # 存储结果
            df = df[int(ma_freq)-1:]  # q只对
            for index, row in df.iterrows():
                hist = object
                if freq == 'D':
                    if done_by == 'system':
                        hist = StockHistoryDaily(pk=row['id'])
                    else:
                        pass
                else:
                    pass
                # print(str(row['trade_date']) + ' ' + str(row['ma'+ma_freq+'_slope']))
                setattr(hist, 'ma'+ma_freq, row['ma'+ma_freq] if not math.isnan(
                    row['ma'+ma_freq]) else None)
                setattr(hist, 'ma'+ma_freq+'_slope', round(row['ma'+ma_freq+'_slope'], 3) if not math.isnan(
                    row['ma'+ma_freq+'_slope']) else None)
                setattr(hist, 'ma'+ma_freq+'_zhicheng_'+version, round(row['ma'+ma_freq+'_zhicheng_'+version], 3) if not math.isnan(
                    row['ma'+ma_freq+'_zhicheng_'+version]) else None)
                setattr(hist, 'ma'+ma_freq+'_tupo_'+version, round(row['ma'+ma_freq+'_tupo_'+version], 3) if not math.isnan(
                    row['ma'+ma_freq+'_tupo_'+version]) else None)
                setattr(hist, 'ma'+ma_freq+'_diepo_'+version, round(row['ma'+ma_freq+'_diepo_'+version], 3) if not math.isnan(
                    row['ma'+ma_freq+'_diepo_'+version]) else None)
                setattr(hist, 'ma'+ma_freq+'_yali_'+version, round(row['ma'+ma_freq+'_yali_'+version], 3) if not math.isnan(
                    row['ma'+ma_freq+'_yali_'+version]) else None)
                hist_list.append(hist)
            if freq == 'D':
                if done_by == 'system':
                    StockHistoryDaily.objects.bulk_update(hist_list, ['ma'+ma_freq,
                                                                      'ma'+ma_freq+'_slope',
                                                                      'ma'+ma_freq+'_zhicheng_'+version,
                                                                      'ma'+ma_freq+'_tupo_'+version,
                                                                      'ma'+ma_freq+'_diepo_'+version,
                                                                      'ma'+ma_freq+'_yali_'+version])
                else:
                    pass
            else:
                pass
            log_test_status(ts_code,
                            'UPD_MARK_CP', freq, ['junxian'+ma_freq+'_bs_'+version])
            # listed_company.is_marked_junxian_bs = True
            # listed_company.save()
            print(' marked junxian bs on end code - ' + ts_code +
                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            hist_list.clear()  # 清空已经保存的记录列表
    else:
        print('no junxian cp task')
    # else:
    #     print('mark junxian bs for code - ' + str(ts_code_list) +
        #   ' marked already or not exist,' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return len(hist_list)


def mark_junxian_cp(ts_code, start_date, end_date, atype='1', freq='D', ma_freq='25', price_chg_pct=0.03, slope_deg=0.05241, day_offset=2, version='v2', done_by='system'):
    '''
    目标：
    参数化分析均线，可能对结果有影响的参数
    - 价格变化
    - 斜率
    - 计算斜率所要考虑的连续的天数（前几天，后几天）
    '''
    print('marked junxian on start code - ' + ts_code +
          ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        df = None
        hist_list = []
        if freq == 'D':
            df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=ts_code,
                                                                            trade_date__gte=start_date, trade_date__lte=end_date).order_by('trade_date').values('id', 'ma'+ma_freq, 'trade_date', 'open', 'close', 'low', 'high', 'slope'))
            # print(df.head())
        else:
            pass
        if df is not None and len(df) > 0:
            # 标记均线
            mark_mov_avg(ts_code, df, ma_freq)
            # 存储结果
            start_index = 0
            if atype != '0': #更新标记
                start_index = int(ma_freq) + day_offset# - day_offset
            # 计算斜率,需要朝前取一个offset记录
            calculate_slope(df, ts_code, ma_freq=ma_freq)
            # print(start_index)
            # q只对更新交易记录做切片处理
            df = df[start_index:]
            # 标记均线关键点
            mark_ma_cp(price_chg_pct, df, ma_freq, version)
            # print(df.head(10))
            # print(df['trade_date'].iloc[start_index])
            # print(len(df))
            for index, row in df.iterrows():
                hist = object
                if freq == 'D':
                    if done_by == 'system':
                        hist = StockHistoryDaily(pk=row['id'])
                    else:
                        pass
                else:
                    pass
                # print(str(row['trade_date']) + ' ' + str(row['ma'+ma_freq+'_slope']))
                setattr(hist, 'ma'+ma_freq, row['ma'+ma_freq] if not math.isnan(
                    row['ma'+ma_freq]) else None)
                setattr(hist, 'ma'+ma_freq+'_slope', round(row['ma'+ma_freq+'_slope'], 3) if not math.isnan(
                    row['ma'+ma_freq+'_slope']) else None)
                setattr(hist, 'ma'+ma_freq+'_zhicheng', round(row['ma'+ma_freq+'_zhicheng'], 3) if not math.isnan(
                    row['ma'+ma_freq+'_zhicheng']) else None)
                setattr(hist, 'ma'+ma_freq+'_tupo', round(row['ma'+ma_freq+'_tupo'], 3) if not math.isnan(
                    row['ma'+ma_freq+'_tupo']) else None)
                setattr(hist, 'ma'+ma_freq+'_diepo', round(row['ma'+ma_freq+'_diepo'], 3) if not math.isnan(
                    row['ma'+ma_freq+'_diepo']) else None)
                setattr(hist, 'ma'+ma_freq+'_yali', round(row['ma'+ma_freq+'_yali'], 3) if not math.isnan(
                    row['ma'+ma_freq+'_yali']) else None)
                hist_list.append(hist)
            if freq == 'D':
                if done_by == 'system':
                    StockHistoryDaily.objects.bulk_update(hist_list, ['ma'+ma_freq,
                                                                    'ma'+ma_freq+'_slope',
                                                                    'ma'+ma_freq+'_zhicheng',
                                                                    'ma'+ma_freq+'_tupo',
                                                                    'ma'+ma_freq+'_diepo',
                                                                    'ma'+ma_freq+'_yali'])
                else:
                    pass
            else:
                pass
            # listed_company.is_marked_junxian_bs = True
            # listed_company.save()
            print(' marked junxian bs on end code - ' + ts_code +
                ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            # hist_list.clear()  # 清空已经保存的记录列表
    except Exception as e:
        print(e)


def mark_ma_cp(price_chg_pct, df_slc, ma_freq, version):
    print('mark cp start')
    mark_zhicheng(price_chg_pct, df_slc, ma_freq,version)
    mark_tupo(price_chg_pct, df_slc, ma_freq,version )
    mark_diepo(price_chg_pct, df_slc, ma_freq, version)
    mark_yali(price_chg_pct, df_slc, ma_freq, version)
    # return df
    print('mark cp end')



def mark_zhicheng(price_chg_pct, df_slc, ma_freq, version):
    '''
    1. 收盘 > MA && 开盘 > MA
    2. |最低价 - MA| < delta
    '''
    # cond = (df['close'] > df['ma'+freq]) & (df['open'] >
    #                  df['ma'+freq]) & ((abs(df['low'] - df['ma'+freq]) / df['ma'+freq]) < delta)
    df_slc['ma'+ma_freq+'_zhicheng'] = np.where((df_slc['close'] > df_slc['ma'+ma_freq]) & (df_slc['open'] >
                                                                                df_slc['ma'+ma_freq]) & (abs(df_slc['low'] - df_slc['ma'+ma_freq]) / df_slc['ma'+ma_freq] <= price_chg_pct), 1, np.nan)
    # print(df.head(100))
    return df_slc
    # for index, row in zhicheng_df.iterrows():
    #     zhicheng_df.loc[index, 'ma25_zhicheng_'+version] = 1


def mark_tupo(price_chg_pct, df_slc, ma_freq, version):
    '''
    1. 收盘 > MA && 开盘 < MA
    2. 收盘 - MA / MA >= delta
    '''
    df_slc['ma'+ma_freq+'_tupo'] = np.where((df_slc['close'] > df_slc['ma'+ma_freq]) & (df_slc['open'] <
                                                                            df_slc['ma'+ma_freq]) & ((df_slc['close'] - df_slc['ma'+ma_freq]) / df_slc['ma'+ma_freq] >= price_chg_pct), 1, np.nan)
    # print(df.head(100))
    return df_slc


def mark_diepo(price_chg_pct, df_slc, ma_freq, version):
    '''
    1. 收盘 < MA && 开盘 > MA
    2. MA - 收盘 / MA >= delta
    '''
    df_slc['ma'+ma_freq+'_diepo'] = np.where((df_slc['close'] < df_slc['ma'+ma_freq]) & (df_slc['open'] >
                                                                             df_slc['ma'+ma_freq]) & ((df_slc['ma'+ma_freq] - df_slc['close']) / df_slc['ma'+ma_freq] >= price_chg_pct), 1, np.nan)
    # print(df.head(100))
    return df_slc


def mark_yali(price_chg_pct, df_slc, ma_freq, version):
    '''
    1. 收盘 < MA && 开盘 < MA 
    2. && (MA - 最高价 / MA < delta or MA - 收盘价 / MA < delta)
    '''
    df_slc['ma'+ma_freq+'_yali'] = np.where((df_slc['close'] < df_slc['ma'+ma_freq]) & (df_slc['open'] <
                                                                            df_slc['ma'+ma_freq]) & (((df_slc['ma'+ma_freq] - df_slc['high']) / df_slc['ma'+ma_freq] <= price_chg_pct) | ((df_slc['ma'+ma_freq] - df_slc['close']) / df_slc['ma'+ma_freq] <= price_chg_pct)), 1, np.nan)
    # print(df.head(100))
    return df_slc


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
        print('zhicheng')
        for min_idx in min_idx_list:
            low_pct = (df.loc[min_idx].ma25 -
                       df.loc[min_idx].low) / df.loc[min_idx].low
            if abs(low_pct) <= price_chg_pct and df.loc[min_idx].close > df.loc[min_idx].ma25:
                df.loc[min_idx, 'ma25_zhicheng_b'] = 1
                print(df.loc[min_idx].trade_date)
                print('ma:'+str(df.loc[min_idx].ma25)+',low:' +
                      str(df.loc[min_idx].low)+',close:'+str(df.loc[min_idx].close))

        # 计算突破，股价需要在上升趋势
        print('tupo')
        idx_prev = -1
        for max_idx in min_idx_list:
            if idx_prev != -1:  # slope >0 means 上涨趋势
                for idx_bwt in range(idx_prev, max_idx):
                    close_pct = (df.loc[idx_prev].close -
                                 df.loc[idx_prev].ma25) / df.loc[idx_prev].ma25
                    if df.loc[idx_bwt].slope > 0 and close_pct >= price_chg_pct and df.loc[idx_bwt].open < df.loc[idx_bwt].ma25:
                        # pass
                        df.loc[max_idx, 'ma25_tupo_b'] = 1
                        print(df.loc[idx_bwt].trade_date)
                        print('ma:'+str(df.loc[idx_bwt].ma25)+',low:'+str(
                            df.loc[idx_bwt].low)+',close:'+str(df.loc[idx_bwt].close))
                        break
            idx_prev = max_idx
        # for up_idx in up_idx_list:
        #     close_pct = (df.loc[up_idx].close -
        #                  df.loc[up_idx].ma25) / df.loc[up_idx].ma25
        #     if abs(close_pct) >= price_chg_pct and df.loc[up_idx].low < df.loc[up_idx].ma25:
        #         df.loc[id, 'ma25_tupo_b'] = 1
        #         print(df.loc[up_idx].trade_date)

        # 计算跌破，股价下跌趋势
        print('diepo')
        idx_prev = -1
        for max_idx in max_idx_list:
            if idx_prev != -1:  # slope >0 means 上涨趋势
                for idx_bwt in range(idx_prev, max_idx):
                    close_pct = (df.loc[idx_bwt].close -
                                 df.loc[idx_bwt].ma25) / df.loc[idx_bwt].ma25
                    if df.loc[idx_bwt].slope < 0 and df.loc[idx_bwt].close < df.loc[idx_bwt].ma25 and df.loc[idx_bwt].open > df.loc[idx_bwt].ma25 and close_pct <= -price_chg_pct:
                        # pass
                        df.loc[max_idx, 'ma25_diepo_s'] = 1
                        print(df.loc[idx_bwt].trade_date)
                        print('ma:'+str(df.loc[idx_bwt].ma25)+',low:'+str(
                            df.loc[idx_bwt].open)+',close:'+str(df.loc[idx_bwt].close))
                        break
            idx_prev = max_idx
        # for down_idx in down_idx_list:
        #     close_pct = (df.loc[down_idx].close -
        #                  df.loc[down_idx].ma25) / df.loc[down_idx].ma25
        #     if df.loc[down_idx].close < df.loc[down_idx].ma25 and df.loc[down_idx].open > df.loc[down_idx].ma25 and abs(close_pct) >= price_chg_pct:
        #         df.loc[id, 'ma25_diepo_s'] = 1
        #         print(df.loc[down_idx].trade_date)

        # 计算MA压力，股价顶部趋势
        print('MA yali')
        idx_prev = -1
        for max_idx in max_idx_list:
            # option 1
            # high_pct = (df.loc[max_idx].ma25 -
            #            df.loc[max_idx].high) / df.loc[max_idx].high
            # if df.loc[max_idx].close < df.loc[max_idx].ma25 and abs(high_pct) <= price_chg_pct:
            #     # print('ma25_yali_s')
            #     df.loc[max_idx, 'ma25_yali_s'] = 1
            #     print(df.loc[max_idx].trade_date)
            #     print('ma:'+str(df.loc[max_idx].ma25)+',low:'+str(df.loc[max_idx].close)+',close:'+str(df.loc[max_idx].high))
            # option 1 (optimized)
            if idx_prev != -1:  # slope >0 means 上涨趋势
                for idx_bwt in range(idx_prev, max_idx-1):
                    high_pct = (df.loc[idx_bwt].ma25 -
                                df.loc[idx_bwt].high) / df.loc[idx_bwt].high
                    if df.loc[idx_bwt].close < df.loc[idx_bwt].ma25 and df.loc[idx_bwt].slope < 0 and abs(high_pct) <= price_chg_pct:
                        # pass
                        # print(df.loc[idx_bwt].trade_date)
                        # print(df.loc[idx_bwt].close)
                        df.loc[idx_bwt, 'ma25_yali_s'] = 1
                        print('ma:'+str(df.loc[idx_bwt].ma25)+',low:'+str(
                            df.loc[idx_bwt].close)+',close:'+str(df.loc[idx_bwt].high))
                        break
            idx_prev = max_idx
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
