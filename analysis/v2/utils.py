import pandas as pd
import numpy as np
import time
import math
import logging
from scipy import stats
from datetime import date, datetime, timedelta


def mark_mov_avg(ts_code, df, ma_freq):
    '''
    标记股票的ma
    '''
    print('mark mov avg' + ma_freq + ' started on code - ' + ts_code + ',' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        df['ma' +
            ma_freq] = round(df['close'].rolling(window=int(ma_freq)).mean(), 3)
        print('mark ma' + ma_freq + ' end on code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        print(e)
    print('mark mov avg end')


def calculate_slope(df, ts_code, day_offset=2, ma_freq='25', atype='1'):
    # df.loc[:int(ma_freq)-1, 'ma'+ma_freq+"_slope"] = np.nan
    # col='ma' + ma_freq, slope_col='ma'+ma_freq+'_slope',
    print('mark slope' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        # if atype == '0':
        #     pass
        # else:
        #     pass
        for index, row in df.iterrows():
            try:
                df_let = df[['ma' + ma_freq]].iloc[index -
                                                   day_offset: index + day_offset]

                df_let.reset_index(level=0, inplace=True)
                df_let.columns = ['ds', 'y']
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    df_let.ds, df_let.y)
                # slope_list.append(slope)
                df.loc[index, 'ma'+ma_freq +
                       '_slope'] = round(slope, 3) if slope is not np.nan else np.nan
            except Exception as e:
                print(e)
                df.loc[index, 'ma'+ma_freq +
                       '_slope'] = np.nan
    except Exception as e:
        print(e)
    print('mark slope end' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
