'''
from talib import ema (e,g, highsMean = talib.EMA(highs, 5))
VAR1:=(CLOSE+HIGH+LOW)/3; 当天的收盘，最高和最低价的平均值
VAR2:=EMA (VAR1, 10); VAR1的10天的指数移动平均
VAR3:=REF (VAR2, 1); VAR2的前一天指数移动平均
绿探底震仓: IF (VAR2, 10, DRAWNULL), colorgreen, LINETHICK9;
红买: IF (VAR2>VAR3, 10, DRAWNULL), colored, LINETHICK9;
蓝卖: IF (VAR2<VAR3, 10, DRAWNULL), COLORFFFF00, LINETHICK9;
RSV:=(CLOSE-LLV (LOW, 9)) / (HHV (HIGH, 9)-LLV (LOW, 9))*100; - Relative Strengh Value
    (Close - 9日最低)/(9日最高 - 9日最低) * 100 
    Y轴值, 范围0 - 100
上穿买: SMA (RSV, 3, 1), colored; RSV的3日移动平均
下穿卖: SMA (上穿买, 3, 1), COLORFFFF00; 上穿买的3日移动平均

Daily/Weekly/Monthly History -
CLOSE: 12.04
HIGH: 14.4
LOW: 11.48
VOL: ?
TO: ?

D0:
D1:
D2:
...
Dn:
'''
# from http.client import _DataType
import math
import copy
import numpy as np
import pandas as pd
import talib
from numpy import busday_count
# from sklearn.datasets import load_wine
from typing import List
from analysis.models import StockHistoryIndicators


def enhanced_ema(ts_code, df_var, df_rsv, hist_count, var2_ema_param=10, rsv_param=9, bs_param=3, update_flag=0):
    '''
    duan_xian_kui_tan
    return df_ohlc['var1'],var2,var3,rsv,b,s
    '''
    # bottom = 0.0
    # b_point = 0.0
    # s_point = 0.0
    b = []
    s = []
    # df_hist = None
    # df_ohlc = df_hist.loc[:, ['close', 'high', 'low', ]]
    if update_flag != 0:
        return enhanced_ema_diff(ts_code, df_var, df_rsv, hist_count, update_flag, var2_ema_param=10, rsv_param=9, bs_param=3)

    # VAR1
    df_var['var1'] = round((df_var['close'] + df_var['high'] + df_var['low']) / 3, 2)
    # VAR2
    var2 = round(talib.EMA(df_var['var1'], var2_ema_param), 2)
    # VAR3
    var3 = pd.DataFrame(var2).shift()

    # RSV
    rsv = []
    for idx, row in df_rsv.iterrows():
        v = (row['close'] - df_rsv['low'].loc[idx-rsv_param+1:idx].min()) / \
            (df_rsv['high'].loc[idx-rsv_param+1:idx].max() -
             df_rsv['low'].loc[idx-rsv_param+1:idx].min()) * 100
        rsv.append(v)
        # pass
    # pass
    b = talib.SMA(np.array(rsv), bs_param)
    s = talib.SMA(b, bs_param)

    # if update_flag == 1:
    #     return df_hist['var1'].iloc[-1],var2.iloc[-1],var3.iloc[-1],rsv[-1],b[-1],s[-1]

    df_var['var2'] = var2  # pd.Series(var2.values.tolist()[::-1])
    df_var['var3'] = var3  # var3[::-1]
    df_var['rsv'] = pd.Series(rsv)  # pd.Series(rsv[::-1])
    df_var['b'] = pd.Series(b)  # pd.Series(b[::-1])
    df_var['s'] = pd.Series(s)  # pd.Series(s[::-1])
    # print(df_ohlc['var2'])
    # print(df_ohlc['var3'])
    return df_var

    # return df_ohlc['var1'],var2,var3,rsv,b,s


def EMA_diff(var1_new: List[any], N: int, var1_hist: List[any], var2_hist, ) -> List[any]:
    out = []
    full_var1 = var1_hist+var1_new
    if var2_hist is np.NaN:
        out.append(sum(full_var1[:N] / N))
        print(out)
    else:
        # print(sum(var1_new[:N]) / N)
        e = round((2 * var1_new[0] + (N - 1) * var2_hist) / (N + 1),2)
        out.append(e)

        for i in range(1, len(var1_new)):
            e = round((2 * var1_new[i] + (N - 1) * out[-1]) / (N + 1),2)
            print(e)
            out.append(e)
    return out


def SMA_diff(new_list: List[any], N: int, hist_list: List[any]) -> List[any]:
    out = []
    full_list = hist_list+new_list
    # if out_hist is np.NaN:
    #     out.append(sum(full_list[:N] / N))
    #     print(out)
    # else:
    for i in range(N-1, len(full_list)): 
        e = round(sum(full_list[i-2:i+1]) / N, 2) # list序列标号，前包后不包
        print(e) 
        out.append(e)
    return out
    # pass


def enhanced_ema_diff(ts_code, df_var, df_rsv, hist_count, update_flag=1, var2_ema_param=10, rsv_param=9, bs_param=3):
    '''
    df_new: 新的股票历史 trade_date > feed_date, <= today
    df_offset:  
    df_indic:
    1. 取最新的hist, 取>=8天的EEMA指标记录
    2. 计算最新的var1 (用最新的Close, High, Low), 单行数据
    3. 增加2的结果到现有var1
    4. 用3得到的var1计算var2 & var3
    5. 计算最新的(单值) RSV
    6. 将5得到的RSV合并到现有RSV
    7. 计算B & S, 利用6中得到的RSV
    8. 返回最后一条记录
    '''
    var1 = []
    ema_diff = []
    indic_hist = 9
    date_diff = int(update_flag)
    # 1
    # df_latest = df_hist.iloc[-(date_diff if date_diff>=9 else rsv_diff):]
    # df_latest = df_var[0] # new history dataframe, trade_date asc
    # df_rsv = df_hist.iloc[-(date_diff if date_diff >=
    #                         rsv_diff else rsv_diff):]  # why 15？
    # df_rsv = pd.concat([df_var[1][::-1], df_var[0]]) #, new - asc, offset - desc, target  asc
    df_rsv = df_rsv.reset_index()  # avoid duplicate index
    # ema 9条历史EMA数据
    eema_indic = StockHistoryIndicators.objects.filter(
        ts_code=ts_code).order_by('-trade_date').values('high', 'low', 'close', 'var1', 'var2', 'var3', 'rsv', 'eema_b', 'eema_s')[:indic_hist]

    # 2 date seq - asc
    for i in range(0, date_diff):
        var1.append(round((df_var['close'].iloc[i] +
                     df_var['high'].iloc[i] + df_var['low'].iloc[i]) / 3, 2))

    # 3
    df_eema = pd.DataFrame.from_records(eema_indic)  # date - desc
    # ser_var1 = pd.concat(
    #     [df_eema['var1'][::-1], pd.Series(var1)], ignore_index=True)  # reverse ema history -> asc,
    # ser_var1 = ser_var1.reset_index()

    var1_list = []
    rsv_hist_list = []
    eema_b_list = []
    for indic in eema_indic:
        var1_list.append(round(indic['var1'],2))
        if len(rsv_hist_list) < 2:
            rsv_hist_list.append(round(indic['rsv'],2))
            eema_b_list.append(round(indic['eema_b'],2))


    # 4
    var2 = EMA_diff(var1, var2_ema_param,
                    var1_list, eema_indic[len(eema_indic)-1]['var2'])
    temp = copy.copy(var2)
    temp.insert(0, round(eema_indic[len(eema_indic)-1]['var2'],2))
    var3 = temp[0:len(temp)-1]
    # var3.insert(0, )

    # 5
    rsv_new_list = []
    for idx, row in df_rsv.iterrows():
        if idx-rsv_param+1 >= 0:
            v = round((row['close'] - df_rsv['low'].loc[idx-rsv_param+1:idx].min()) / \
                (df_rsv['high'].loc[idx-rsv_param+1:idx].max() -
                 df_rsv['low'].loc[idx-rsv_param+1:idx].min()) * 100, 2)
            rsv_new_list.append(v)
        # pass

    # 6
    # 7

    b = SMA_diff(rsv_new_list, bs_param, rsv_hist_list, )
    s = SMA_diff(b, bs_param, eema_b_list, )

    # slice to only new history
    # var2 = var2[9:]
    # var3 = var3[9:]
    # rsv = rsv[9:]
    # b = b[9:]
    # s = s[9:]

    # new_eema = StockHistoryIndicators()
    # new_eema.var1 = var1
    # new_eema.var2 = var2.iloc[:-1]
    # new_eema.var3 = var3.iloc[:-1]
    # new_eema.rsv = rsv[-1]
    # new_eema.eema_b = b.iloc[:-1]
    # new_eema.eema_s = s.iloc[:-1]
    # new_eema.save()
    # for i in range(0, date_diff):
    #     ema_diff.append(
    #     {
    #         'close': df_latest['close'].iloc[i], # series, desc
    #         'high': df_latest['high'].iloc[i],# series, desc
    #         'low': df_latest['low'].iloc[i],# series, desc
    #         'vol':df_latest['vol'].iloc[i],# series, desc
    #         'amount':df_latest['amount'].iloc[i],# series, desc
    #         'trade_date':df_latest['trade_date'].iloc[i],# series, desc
    #         'var1': var1[-i:],# list, desc
    #         'var2': var2[-i:],# Series , desc
    #         'var3':var3[-i:],# pandas dataframe, desc
    #         'rsv':rsv[-1:][i],# array list , asc
    #         'eema_b':b[-1:][i],# numpy ndarray, asc
    #         'eema_s':s[-1:][i],# numpy ndarray, asc
    #     })

    # ema_df = pd.DataFrame()
    # df_latest = pd.Series([], dtype='float64')
    df_var['var1'] = var1  # list, asc
    df_var['var2'] = var2  # Series , asc
    df_var['var3'] = var3  # pandas dataframe, asc
    df_var['rsv'] = rsv_new_list  # array list , asc
    df_var['b'] = b  # numpy ndarray, asc
    df_var['s'] = s  # numpy ndarray, asc

    return pd.DataFrame(df_var)


def enhanced_ema_diff1(ts_code, df_hist, update_flag, var2_ema_param=10, rsv_param=9, bs_param=3):
    '''
    1. 取最新的hist, 取>=8天的EEMA指标记录
    2. 计算最新的var1 (用最新的Close, High, Low), 单行数据
    3. 增加2的结果到现有var1
    4. 用3得到的var1计算var2 & var3
    5. 计算最新的(单值) RSV
    6. 将5得到的RSV合并到现有RSV
    7. 计算B & S, 利用6中得到的RSV
    8. 返回最后一条记录
    '''
    # 1
    df_latest = df_hist.iloc[-1:]
    df_rsv = df_hist.iloc[-9:]  # why 15？
    eema = StockHistoryIndicators.objects.filter(
        ts_code=ts_code).order_by('-trade_date').values('high', 'low', 'close', 'var1', 'var2', 'var3', 'rsv', 'eema_b', 'eema_s')[:var2_ema_param*2]
    # 2
    var1 = (df_latest['close'].iloc[0] +
            df_latest['high'].iloc[0] + df_latest['low'].iloc[0]) / 3
    # 3
    df_eema = pd.DataFrame.from_records(eema)
    ser_var1 = pd.concat(
        [df_eema['var1'], pd.Series([var1])], ignore_index=True)
    # 4
    var2 = talib.EMA(ser_var1, var2_ema_param)
    var3 = pd.DataFrame(var2).shift()
    # 5
    rsv = []
    for idx, row in df_rsv.iterrows():
        v = (row['close'] - df_rsv['low'].loc[idx-rsv_param+1:idx].min()) / \
            (df_rsv['high'].loc[idx-rsv_param+1:idx].max() -
             df_rsv['low'].loc[idx-rsv_param+1:idx].min()) * 100
        rsv.append(v)
        # pass
    # 6
    # 7
    b = talib.SMA(np.array(rsv), bs_param)
    s = talib.SMA(b, bs_param)

    # new_eema = StockHistoryIndicators()
    # new_eema.var1 = var1
    # new_eema.var2 = var2.iloc[:-1]
    # new_eema.var3 = var3.iloc[:-1]
    # new_eema.rsv = rsv[-1]
    # new_eema.eema_b = b.iloc[:-1]
    # new_eema.eema_s = s.iloc[:-1]
    # new_eema.save()
    return pd.DataFrame([
        {
            'close': df_latest['close'].iloc[0],
            'high': df_latest['high'].iloc[0],
            'low': df_latest['low'].iloc[0],
            'vol':df_latest['vol'].iloc[0],
            'amount':df_latest['amount'].iloc[0],
            'trade_date':df_latest['trade_date'].iloc[0],
            'var1': var1,
            'var2': var2[-1:],
            'var3':var3[-1:],
            'rsv':rsv[-1:][0],
            'eema_b':b[-1:][0],
            'eema_s':s[-1:][0],
        }
    ])
