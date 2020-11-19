

import logging
import time
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from investors.models import StockFollowing, TradeStrategy
from stockmarket.models import StockNameCodeMap

from analysis.utils import (generate_task, get_analysis_task,
                            get_trade_cal_diff, init_eventlog,
                            get_event_status, set_event_completed,
                            set_task_completed)

from .models import StockHistoryDaily, StockStrategyTestLog
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
    evt_dl_status = get_event_status(
        'HIST_DOWNLOAD', exec_date=exec_date, freq=freq)
    evt_mk_status = get_event_status(
        'MARK_CP', exec_date=exec_date, strategy_code='jiuzhuan_bs', freq=freq)
    
    if ts_code is None:
        if evt_dl_status == 0:
            print("previous downloading is still ongoing")
        elif evt_dl_status == -1:
            print("history has not yet been downloaded today")
        else:
            if evt_mk_status == 0:
                print("previous marking is still ongoing")
            elif evt_mk_status == 1:
                print("marking has been done today")
            else:
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
    strategy_list = ['jiuzhuan_b', 'jiuzhuan_s']
    start_date = None
    end_date = None
    today = date.today()

    try:
        if ts_code is None:
            listed_companies = StockNameCodeMap.objects.filter()
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
                        print('第一次处理，从上市日开始。。。')
                        atype = '0'  # 从上市日开始标记
                        start_date = task.start_date
                    else:
                        print('更新处理，从上一次更新时间-4d - 开盘日 开始...')
                        start_date = task.start_date - \
                            timedelta(days=get_trade_cal_diff(
                                listed_company.ts_code, task.start_date))

                    mark_jiuzhuan(listed_company.ts_code, freq, start_date,
                                  task.end_date, atype)
                    # print(task.start_date)
                    # print(task.end_date)
                    set_task_completed(listed_company.ts_code, 'MARK_CP',
                                       freq, 'jiuzhuan_bs', task.start_date, task.end_date)
                    generate_task(listed_company.ts_code,
                                  freq, task.start_date, task.end_date, event_list=btest_event_list, strategy_list=strategy_list)
            else:
                print('no jiuzhuan mark cp task')
    except Exception as e:
        print(e)


def test_mark(ts_code, start_date, end_date):
    try:
        hist_list = []
        end_date = date.today()
        df = download_hist_data(ts_code, start_date, end_date)
        marked_df = pre_mark_jiuzhuan(df)
        for v in marked_df.values:
            hist_D = StockHistoryDaily(ts_code=v[0], trade_date=datetime.strptime(v[1], '%Y%m%d'), open=v[2], high=v[3],
                                       low=v[4], close=v[5], pre_close=v[6], change=v[7], pct_chg=v[8], vol=v[9],
                                       amount=v[10], chg4=v[11], jiuzhuan_count_b=v[12], jiuzhuan_count_s=v[13])
            '''
            ts_code	str	股票代码
            trade_date	str	交易日期
            open	float	开盘价
            high	float	最高价
            low	float	最低价
            close	float	收盘价
            pre_close	float	昨收价
            change	float	涨跌额
            pct_chg	float	涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
            vol	float	成交量 （手）
            amount	float	成交额 （千元）
            '''
            # hist_D.save()
            hist_list.append(hist_D)
        StockHistoryDaily.objects.bulk_create(hist_list)
    except Exception as e:
        logger.error(e)
        return False
    else:
        return True


def mark_jiuzhuan(ts_code, freq, start_date, end_date, atype):
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
    df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=ts_code, trade_date__gte=start_date, trade_date__lte=end_date).order_by(
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
            if freq == 'D':
                hist = StockHistoryDaily(pk=row['id'])
            else:
                pass
            # print(row['chg4'])
            hist.chg4 = round(
                row['chg4'], 3) if row['chg4'] is not None else None
            hist.jiuzhuan_count_b = row['jiuzhuan_count_b'] if row['jiuzhuan_count_b'] != 0 else None
            hist.jiuzhuan_count_s = row['jiuzhuan_count_s'] if row['jiuzhuan_count_s'] != 0 else None
            hist_list.append(hist)
        if freq == 'D':
            StockHistoryDaily.objects.bulk_update(
                hist_list, ['chg4', 'jiuzhuan_count_b', 'jiuzhuan_count_s'])
        else:
            pass
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
        count_b = df['jiuzhuan_count_b'].iloc[3] if df['jiuzhuan_count_b'].iloc[3] is not np.nan else 0
        # 九转卖点计数器
        count_s = df['jiuzhuan_count_s'].iloc[3] if df['jiuzhuan_count_s'].iloc[3] is not np.nan else 0
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
