import pandas as pd
import numpy as np
import time
import math
import logging
from scipy import stats
from datetime import date, datetime, timedelta


def mark_mv_avg(ts_code, df, ma_freq):
    '''
    标记股票的ma
    '''
    print('pre mark ma' + ma_freq + ' started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        df['ma'+ma_freq] = round(df['close'].rolling(window=int(ma_freq)).mean(), 3)
        print('pre ma' + ma_freq + ' end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        print(e)


def mark_slope(df, offset_df, ts_code, day_offset=2, col='close', slope_col='slope'):
    try:
        for index, row in offset_df.iterrows():
            # 股价与往前第四个交易日比较，如果<前值，那么开始计算九转买点，
            df_let = df[[col]].iloc[index -
                                        day_offset: index + day_offset]
            df_let.reset_index(level=0, inplace=True)
            df_let.columns = ['ds', 'y']
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                df_let.ds, df_let.y)
            # slope_list.append(slope)
            df.loc[index, slope_col] = round(slope, 3)
    except Exception as e:
        print(e)