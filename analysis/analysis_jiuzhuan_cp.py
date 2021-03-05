

import logging
import time
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from investors.models import StockFollowing, TradeStrategy
from stockmarket.models import StockNameCodeMap
from dashboard.utils import days_between
from analysis.utils import (generate_task, get_analysis_task,
                            get_trade_cal_diff, init_eventlog,
                            get_event_status, set_event_completed,
                            set_task_completed, ready2proceed)

from .models import StockHistoryDaily, StockStrategyTestLog, StockIndexHistory
from .stock_hist import download_hist_data

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


def handle_jiuzhuan_cp(ts_code, freq='D'):
    exec_date = date.today()
    if ts_code is None:
        if ready2proceed('jiuzhuan_bs'):
                init_eventlog('MARK_CP',  exec_date=exec_date,
                              strategy_code='jiuzhuan_bs', freq=freq)
                process_jiuzhuan_cp(ts_code, freq,)
                set_event_completed('MARK_CP', exec_date=exec_date,
                                    strategy_code='jiuzhuan_bs', freq=freq)
    else:
        process_jiuzhuan_cp(ts_code, freq,)


def process_jiuzhuan_cp(ts_code, freq='D'):
    '''
    同步策略在交易中的使用情况
    '''
    btest_event_list = ['EXP_PCT_TEST', 'PERIOD_TEST']
    strategy_list = ['jiuzhuan_count_b', 'jiuzhuan_count_s']
    start_date = None
    end_date = None
    today = date.today()
    period = 4
    try:
        if ts_code is None:
            listed_companies = StockNameCodeMap.objects.filter().order_by('-ts_code')
        else:
            ts_code_list = ts_code.split(',')
            if ts_code_list is not None and len(ts_code_list) >= 1:
                listed_companies = StockNameCodeMap.objects.filter(
                    ts_code__in=ts_code_list)
        for listed_company in listed_companies:  # 需要优化
            tasks = get_analysis_task(
                listed_company.ts_code, 'MARK_CP', 'jiuzhuan_bs', freq)
            if tasks is not None and len(tasks) > 0:
                atype = '1'  # 标记更新的股票历史记录
                # 如何差额取之前的历史记录？9
                for task in tasks:
                    if task.start_date == listed_company.list_date:
                        print(listed_company.ts_code + '第一次处理，从上市日开始。。。')
                        atype = '0'  # 从上市日开始标记
                        start_date = task.start_date
                    else:
                        print(listed_company.ts_code +
                              ' 更新处理，从上一次更新时间-4d - 开盘日 开始...')
                        if days_between(task.start_date, listed_company.list_date) <= period:
                            # fix issue - 计算period=4的有效交易日器
                            start_date = listed_company.list_date
                        else:
                            start_date = task.start_date - \
                                timedelta(days=get_trade_cal_diff(
                                    listed_company.ts_code, task.start_date, listed_company.asset))

                    mark_jiuzhuan(listed_company.ts_code, listed_company.asset, freq, start_date,
                                  task.end_date, atype)
                    # print(task.start_date)
                    # print(task.end_date)
                    set_task_completed(listed_company.ts_code, 'MARK_CP',
                                       freq, 'jiuzhuan_bs', task.start_date, task.end_date)
                    # generate_task(listed_company.ts_code,
                    #               freq, task.start_date, task.end_date, event_list=btest_event_list, strategy_list=strategy_list)
            else:
                print(listed_company.ts_code + ' no jiuzhuan mark cp task')
    except Exception as e:
        print(e)


def mark_jiuzhuan(ts_code, asset, freq, start_date, end_date, atype):
    '''
    对于未标注九转的上市股票运行一次九转序列标记，
    每次运行只是增量上市股票标记
    '''
    run_date = date.today()
    hist_list = []

    print(' marked jiuzhuan on start code - ' + ts_code +
          ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # df = hist_since_listed(
    #     listed_company.ts_code, datetime.strptime(listed_company.list_date, '%Y%m%d'), end_date)
    if asset == 'E':
        df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=ts_code, trade_date__gte=start_date, trade_date__lte=end_date).order_by(
            'trade_date').values('id', 'close', 'chg4', 'jiuzhuan_count_b', 'jiuzhuan_count_s'))
    else:
        df = pd.DataFrame.from_records(StockIndexHistory.objects.filter(ts_code=ts_code, trade_date__gte=start_date, trade_date__lte=end_date).order_by(
            'trade_date').values('id', 'close', 'chg4', 'jiuzhuan_count_b', 'jiuzhuan_count_s'))
    # print(len(df))
    if df is not None and len(df) > 0:
        # df_close_diff4 = df['close'].diff(periods=4)
        # if df_close_diff4 is not None and len(df_close_diff4) > 0:
        #     pre_mark_b(df, df_close_diff4)
        #     pre_mark_s(df, df_close_diff4)
        #     df['chg4'] = df_close_diff4
        pre_mark_jiuzhuan(df, atype)
        # 确保处理后的数据只是更新需要更新的开始日期
        start_index = 0
        if atype != '0':
            start_index = 4
        df = df[start_index:]
        for index, row in df.iterrows():
            hist = None
            if asset == 'E':
                hist = StockHistoryDaily(pk=row['id'])
            else:
                hist = StockIndexHistory(pk=row['id'])

            # print(row['chg4'])
            hist.chg4 = round(
                row['chg4'], 3) if row['chg4'] is not np.isnan(row['chg4']) else None
            hist.jiuzhuan_count_b = row['jiuzhuan_count_b'] if row['jiuzhuan_count_b'] != 0 else None
            hist.jiuzhuan_count_s = row['jiuzhuan_count_s'] if row['jiuzhuan_count_s'] != 0 else None
            hist_list.append(hist)
        if asset == 'E':
            StockHistoryDaily.objects.bulk_update(
                hist_list, ['chg4', 'jiuzhuan_count_b', 'jiuzhuan_count_s'])
        else:
            StockIndexHistory.objects.bulk_update(
                hist_list, ['chg4', 'jiuzhuan_count_b', 'jiuzhuan_count_s'])
        hist_list.clear()
        print(' marked jiuzhuan on end code - ' + ts_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # return len(hist_list)


def pre_mark_jiuzhuan(df, atype=1):
    '''
    标记股票的九转序列
    '''
    jiuzhuan_diff_list = []
    jiuzhuan_diff_s_list = []
    # print(atype)
    # print(df['jiuzhuan_count_b'].iloc[3])
    # print(df['jiuzhuan_count_s'].iloc[3])
    # print(df['trade_date'].iloc[3])
    periods = 4 if atype == '1' else 0
    if atype == '1':  # 更新
        # print(df['jiuzhuan_count_b'].iloc[3])
        # print(df['jiuzhuan_count_s'].iloc[3])
        # 九转买点计数器
        count_b = df['jiuzhuan_count_b'].iloc[3] if df['jiuzhuan_count_b'].iloc[3] is not None else 0
        # 九转卖点计数器
        count_s = df['jiuzhuan_count_s'].iloc[3] if df['jiuzhuan_count_s'].iloc[3] is not None else 0
        print(count_b)
        print(count_s)
        for i in range(0, periods):
            jiuzhuan_diff_list.append(np.nan)
            jiuzhuan_diff_s_list.append(np.nan)
    else:  # 首次标记
        count_b = 0
        count_s = 0
    try:
        # df = pro.daily(ts_code=stock_symbol, trade_date=trade_date)
        # 与4天前的收盘价比较
        df_close_diff4 = df['close'].diff(periods=4)
        # print(len(df_close_diff4))
        # df_close_diff4_p = df_close_diff4[periods:]
        # print(df_close_diff4.head(10))
        if df_close_diff4 is not None and len(df_close_diff4) > 0:
            for close_chg4 in df_close_diff4[periods:].values:
                if close_chg4 is not np.nan:
                    # print(close_chg4)
                    if close_chg4 < 0:  # 股价与往前第四个交易日比较，如果<前值，那么开始计算九转买点，
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
                    # print(count_b)
                    # print(count_s)
                    jiuzhuan_diff_list.append(count_b)
                    jiuzhuan_diff_s_list.append(count_s)
                else:
                    jiuzhuan_diff_list.append(0)
                    jiuzhuan_diff_s_list.append(0)
        # print(jiuzhuan_diff_list)
        # print(jiuzhuan_diff_s_list)
        # df['diff'] = df_close_diff4
        # df['diff_count'] = jiuzhuan_diff_list
        # df['diff_count_s'] = jiuzhuan_diff_s_list
        df['chg4'] = df_close_diff4
        df['jiuzhuan_count_b'] = jiuzhuan_diff_list
        df['jiuzhuan_count_s'] = jiuzhuan_diff_s_list
    except Exception as e:
        print(e)
    # else:
    #     return df
