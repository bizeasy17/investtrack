import calendar
import logging
import math
import time
from calendar import monthrange
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
# from investors.models import TradeStrategy
import tushare as ts
# from dashboard.utils import days_between
from django.utils import timezone
from scipy import stats

from .models import (AnalysisDateSeq, AnalysisEventLog, StockHistoryDaily,
                     StockIndexHistory, StockStrategyTestLog)

strategy_dict = {'jiuzhuan_bs': {'jiuzhuan_count_b', 'jiuzhuan_count_s'}, 'dingdi': {'dingbu_s', 'dibu_b'},
                 'tupo_yali_b': {'tupo_b'}, 'diepo_zhicheng_s': {'diepo_s'},  'wm_dingdi_bs': {'m_ding', 'w_di'},
                 'junxian25_bs': {'ma25_zhicheng', 'ma25_diepo', 'ma25_yali', 'ma25_tupo'},
                 'junxian60_bs': {'ma60_zhicheng', 'ma60_diepo', 'ma60_yali', 'ma60_tupo'},
                 'junxian200_bs': {'ma200_zhicheng', 'ma200_diepo', 'ma200_yali', 'ma200_tupo', }}


def days_between(d1, d2):
    # d1 = datetime.strptime(d1, "%Y-%m-%d")
    # d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def days_to_now(d1):
    d2 = datetime.now(tz=timezone.utc)
    return abs((d2 - d1).days)


def get_market_code(ts_code):
    indexes = {'6': '000001.SH', '0': '399001.SZ',
               '3': '399006.SZ', '688': '000688.SH'}
    try:
        if ts_code[0] == '3':
            return indexes['3']
        elif ts_code[0] == '0':
            return indexes['0']
        else:
            if ts_code[:3] == '688':
                return indexes['688']
            else:
                return indexes['6']
    except Exception as err:
        print(err)

# X-Forwarded-For:简称XFF头，它代表客户端，也就是HTTP的请求端真实的IP，只有在通过了HTTP 代理或者负载均衡服务器时才会添加该项。


def get_ip(request):
    '''获取请求者的IP信息'''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # 判断是否使用代理
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # 使用代理获取真实的ip
    else:
        ip = request.META.get('REMOTE_ADDR')  # 未使用代理获取IP
    return ip


def ready2proceed(strategy_code, freq='D'):
    exec_date = date.today()
    evt_dl_status = get_event_status(
        'HIST_DOWNLOAD', exec_date=exec_date, freq=freq)
    evt_mk_status = get_event_status(
        'MARK_CP', exec_date=exec_date, strategy_code=strategy_code, freq=freq)

    if evt_dl_status == 0:
        print("previous downloading is still ongoing")
        return False
    elif evt_dl_status == -1:
        print("history has not yet been downloaded today")
        return False
    else:
        if evt_mk_status == 0:
            print("previous marking is still ongoing")
            return False
        elif evt_mk_status == 1:
            print("marking has been done today")
            return False
    return True


def get_dict_key(dict, value):
    for (k, v) in dict.items():
        if value in v:
            return k


def set_task_completed(ts_code, event, freq, strategy_code, start_date, end_date):
    try:
        task = StockStrategyTestLog.objects.get(
            ts_code=ts_code, analysis_code=strategy_code, event_type=event, freq=freq, start_date=start_date, end_date=end_date, is_done=False)
        task.is_done = True
        task.last_mod_time = datetime.now(timezone.utc)
        task.save()
    except Exception as e:
        print(e)


def generate_task(listed_company, start_date, end_date, freq='D', ):
    threshold_hist_fx = 365 * 3
    threshold_hist_25 = 25
    threshold_hist_60 = 60
    threshold_hist_200 = 200

    analysis_start_date = listed_company.last_analyze_date if listed_company.last_analyze_date is not None else listed_company.list_date
    mark_start_date = listed_company.list_date

    # analysis_event_list = ['EXP_PCT_TEST', 'PERIOD_TEST',
    #                        'TGT_PCT_QTN', 'UPDN_PCT_QTN', 'UPDN_PCT_RK', 'TGT_PCT_RK']
    analysis_event_list = []
    # analysis_strategy_list = ['ma25_zhicheng', 'ma25_diepo', 'ma25_yali', 'ma25_tupo',
    #                           'ma60_zhicheng', 'ma60_diepo', 'ma60_yali', 'ma60_tupo',
    #                           'jiuzhuan_count_b', 'jiuzhuan_count_s', 'dingbu_s', 'dibu_b',
    #                           'tupo_b', 'diepo_s', 'm_ding', 'w_di',
    #                           'ma200_zhicheng', 'ma200_diepo', 'ma200_yali', 'ma200_tupo']
    analysis_strategy_list = ['jiuzhuan_count_b', 'jiuzhuan_count_s']
    mark_cp_event_list = ['MARK_CP']
    # dl_daily_event_list = ['DAILY_DOWNLOAD']
    dl_daily_event_list = []

    mark_strategy_set = {}
    # mark_strategy_dict = {
    #     '25': {'junxian25_bs', 'jiuzhuan_bs'},
    #     '60': {'junxian60_bs', 'dingdi', 'tupo_yali_b', 'diepo_zhicheng_s',
    #            'wm_dingdi_bs', },
    #     '200': {'junxian200_bs'}
    # }
    mark_strategy_dict = {
        '25': {'junxian25_bs', 'jiuzhuan_bs'}
    }

    # analysis_hist = StockHistoryDaily.objects.filter(
    #     ts_code=listed_company.ts_code, trade_date__gte=analysis_start_date, trade_date__lte=end_date)
    # mark_hist = StockHistoryDaily.objects.filter(
    #     ts_code=listed_company.ts_code, trade_date__gte=mark_start_date, trade_date__lte=end_date)

    # 如果hist length > 600，生成分析事件
    # tasks = get_analysis_task(ts_code, event, )
    for event in analysis_event_list:
        for strategy in analysis_strategy_list:
            try:
                task = StockStrategyTestLog.objects.get(
                    ts_code=listed_company.ts_code, analysis_code=strategy, event_type=event, freq=freq, end_date=start_date - timedelta(days=1), is_done=False)
                task.end_date = end_date
                listed_company.last_analyze_date = end_date
                task.save()
            except Exception as e:
                # print(e)
                # 未找到运行记录
                if days_between(mark_start_date, end_date) >= threshold_hist_fx:
                    # mark_strategy_set = set.union(
                    #     mark_strategy_dict['200'], mark_strategy_dict['60'], mark_strategy_dict['25'])
                    task = StockStrategyTestLog(ts_code=listed_company.ts_code,
                                                analysis_code=strategy,
                                                event_type=event, freq=freq, start_date=start_date, end_date=end_date)
                    listed_company.last_analyze_date = end_date
                    task.save()
                    # listed_company.save()
                # else:
                #     # 如果hist length < 600, >= 25, 生成MA25 标记事件
                #     # if len(hist) < 600 and len(hist) >= 25:
                #     #     pass
                #     # 如果hist length < 600, >= 60, 生成MA60，突破，WM底，跌破，标记事件
                #     # if len(hist) < 600 and len(hist) >= 60:
                #     #     pass
                #     # 如果hist length < 600, >= 200, 生成MA200 标记事件
                #     # if len(hist) < 600 and len(hist) >= 200:
                #     #     pass
                #     if days_between(mark_start_date, end_date) >= threshold_hist_200:
                #         mark_strategy_set = set.union(
                #             mark_strategy_dict['200'], mark_strategy_dict['60'], mark_strategy_dict['25'])
                #     else:
                #         if days_between(mark_start_date, end_date) >= threshold_hist_60:
                #             mark_strategy_set = set.union(
                #                 mark_strategy_dict['25'], mark_strategy_dict['60'])
                #         else:
                #             if days_between(mark_start_date, end_date) >= threshold_hist_25:
                #                 mark_strategy_set = mark_strategy_dict['25']

    mark_strategy_set = set.union(
        # mark_strategy_dict['200'], mark_strategy_dict['60'], mark_strategy_dict['25'])
        mark_strategy_dict['25'])

    for event in mark_cp_event_list:
        for strategy in mark_strategy_set:
            try:
                # tasks = get_analysis_task(ts_code, event, )
                task = StockStrategyTestLog.objects.get(
                    ts_code=listed_company.ts_code, analysis_code=strategy, event_type=event, freq=freq, end_date=start_date - timedelta(days=1), is_done=False)
                task.end_date = end_date
                # mark_log.save()
            except Exception as e:  # 未找到运行记录
                # print(e)
                # 未找到运行记录
                task = StockStrategyTestLog(ts_code=listed_company.ts_code,
                                            analysis_code=strategy,
                                            event_type=event, freq=freq, start_date=start_date, end_date=end_date)
            task.save()

    for event in dl_daily_event_list:
        try:
            # tasks = get_analysis_task(ts_code, event, )
            task = StockStrategyTestLog.objects.get(
                ts_code=listed_company.ts_code, event_type=event, freq=freq, end_date=start_date - timedelta(days=1), is_done=False)
            task.end_date = end_date
            # mark_log.save()
        except Exception as e:  # 未找到运行记录
            # print(e)
            # 未找到运行记录
            task = StockStrategyTestLog(ts_code=listed_company.ts_code,
                                        event_type=event, freq=freq, start_date=start_date, end_date=end_date)
        task.save()


def get_event_status(event, exec_date, strategy_code=None, freq='D'):
    '''
    前提，已经存在，在处理过程中in progress, 或已经结束finished 。。。。
    1. 如果存在，就更新end date
    2. 如果不存在，就创建新的
    '''
    # event_list = ['MARK_CP', 'PERIOD_TEST', 'EXP_PCT_TEST']
    try:
        if strategy_code is not None:  # Mark CP
            event = AnalysisEventLog.objects.get(
                analysis_code=strategy_code, event_type=event, freq=freq, exec_date=exec_date)
        else:
            event = AnalysisEventLog.objects.get(
                event_type=event, freq=freq, exec_date=exec_date)
        return event.status
    except Exception as e:  # 未找到event log记录
        print(e)
        return -1


def init_eventlog(event, exec_date, strategy_code=None, freq='D'):
    '''
    前提，已经存在，在处理过程中in progress, 或已经结束finished 。。。。
    1. 如果存在，就更新end date
    2. 如果不存在，就创建新的
    '''
    # event_list = ['MARK_CP', 'PERIOD_TEST', 'EXP_PCT_TEST']
    try:
        if strategy_code is not None:  # Mark CP
            AnalysisEventLog.objects.get(
                analysis_code=strategy_code, event_type=event, freq=freq, status__in=[0, -1], exec_date=exec_date)
        else:
            AnalysisEventLog.objects.get(
                event_type=event, freq=freq, status__in=[0, -1], exec_date=exec_date)
    except Exception as e:  # 未找到event log记录
        print(e)
        eventlog = AnalysisEventLog(
            analysis_code=strategy_code,
            event_type=event, freq=freq, exec_date=exec_date)
        eventlog.save()


def set_event_completed(event, exec_date, strategy_code=None, freq='D'):
    '''
    前提，已经存在，在处理过程中in progress, 或已经结束finished 。。。。
    1. 如果存在，就更新end date
    2. 如果不存在，就创建新的
    '''
    # event_list = ['MARK_CP', 'PERIOD_TEST', 'EXP_PCT_TEST']
    try:
        if strategy_code is not None:  # Mark CP
            event = AnalysisEventLog.objects.get(
                analysis_code=strategy_code, event_type=event, freq=freq, exec_date=exec_date)
        else:
            event = AnalysisEventLog.objects.get(
                event_type=event, freq=freq, exec_date=exec_date)
        event.status = 1
        event.last_mod_time = datetime.now(timezone.utc)
        event.save()
        return True
    except Exception as e:  # 未找到event log记录
        print(e)
        return False


def hist_downloaded(ts_code, event, freq):
    today = date.today()
    try:
        #
        mark_log = StockStrategyTestLog.objects.get(
            ts_code=ts_code, end_date__event_type=event, freq=freq, is_done=True)
    except Exception as e:
        # print(e)
        return False


def log_download_hist(ts_code, event, start_date, end_date, freq):
    try:
        mark_log = StockStrategyTestLog(ts_code=ts_code,
                                        event_type=event, start_date=start_date, end_date=end_date, freq=freq, is_done=True)
        mark_log.save()
    except Exception as e:
        print(e)


def get_analysis_task(ts_code, event, strategy_code, freq='D'):
    try:
        if strategy_code is not None:
            task = StockStrategyTestLog.objects.filter(
                ts_code=ts_code, analysis_code=strategy_code, event_type=event, freq=freq, is_done=False).order_by('start_date')
        else:
            task = StockStrategyTestLog.objects.filter(
                ts_code=ts_code, event_type=event, freq=freq, is_done=False).order_by('start_date')
        return task
    except Exception as e:
        # print(e)
        return None


def get_trade_cal_diff(ts_code, last_trade, asset='E', exchange='SSE', period=4):
    count = 0
    offset = 0
    # pro = ts.pro_api()
    while count < period:
        # df = pro.trade_cal(exchange=exchange, start_date=(last_trade -
        #                                                   timedelta(days=offset+1)).strftime('%Y%m%d'), end_date=(last_trade-timedelta(days=offset+1)).strftime('%Y%m%d'))
        # if df['is_open'].iloc[0] == 1:
        #     count += 1
        try:
            if asset == 'E':
                StockHistoryDaily.objects.get(
                    ts_code=ts_code, trade_date=last_trade-timedelta(days=offset+1))
            else:
                StockIndexHistory.objects.get(
                    ts_code=ts_code, trade_date=last_trade-timedelta(days=offset+1))
            count += 1
        except Exception as e:
            pass
        offset += 1
    # print(last_trade-timedelta(days=offset))
    return offset


def get_nearest_trade_cal(cur_date, exchange='SSE'):
    # count = 0
    offset = 0
    pro = ts.pro_api()
    while True:
        df = pro.trade_cal(exchange=exchange, start_date=(cur_date -
                                                          timedelta(days=offset)).strftime('%Y%m%d'), end_date=(cur_date-timedelta(days=offset)).strftime('%Y%m%d'))
        if df['is_open'].iloc[0] == 1:
            return (cur_date - timedelta(days=offset))
        offset += 1
    # print(last_trade-timedelta(days=offset))

# 20210918


def init_log(ts_code, start_date, end_date, freq, log_type):
    '''
    exec_date = today()
    opt1:

    opt2:
    opt3:
    '''
    # exec_date = date.today()
    try:
        log = StockStrategyTestLog.objects.get(
            ts_code=ts_code, start_date=start_date, end_date=end_date, event_type=log_type, freq=freq)
    except:  # 下载任务全部完成，创建新任务
        log = StockStrategyTestLog(ts_code=ts_code,
                                   event_type=log_type, freq=freq, start_date=start_date, end_date=end_date)
        log.save()
    return log


def complete_download(ts_code, exec_date, log_type, freq='D'):
    '''
    前提，已经存在，在处理过程中in progress, 或已经结束finished 。。。。
    1. 如果存在，就更新end date
    2. 如果不存在，就创建新的
    '''
    # event_list = ['MARK_CP', 'PERIOD_TEST', 'EXP_PCT_TEST']
    exec_date = date.today()

    try:
        log = StockStrategyTestLog.objects.get(
            ts_code=ts_code, log_type=log_type, freq=freq, exec_date=exec_date)
        log.is_done = True
        log.save()
    except Exception as e:  # 未找到event log记录
        return False


def ready2_download(ts_code, end_date, log_type, freq='D'):
    exec_date = date.today()

    try:
        StockStrategyTestLog.objects.get(
            ts_code=ts_code, event_type=log_type, end_date__gte=end_date, freq=freq, is_done=True)
        return False
    except:
        return True


def last_download_date(ts_code, log_type, freq):
    try:
        # 获得上一次下载记录
        log = StockStrategyTestLog.objects.filter(
            ts_code=ts_code, event_type=log_type, freq=freq, is_done=True).order_by('-end_date')[0]
        # print(log.start_date)
        # print(log.end_date)
        return [log.start_date, log.end_date]
    except Exception as e:
        print(e)
        return None

# 20210925


def next_month(date):
    """add one month to date, maybe falling to last day of month
    :param datetime.datetime date: the date
    ::
      >>> add_month(datetime(2014,1,31))
      datetime.datetime(2014, 2, 28, 0, 0)
      >>> add_month(datetime(2014,12,30))
      datetime.datetime(2015, 1, 30, 0, 0)
    """
    # number of days this month
    month_days = calendar.monthrange(date.year, date.month)[1]
    # print(month_days)
    candidate = date + timedelta(days=month_days)
    # but maybe we are a month too far
    if candidate.day != date.day:
        # go to last day of next month,
        # by getting one day before begin of candidate month
        return candidate.replace(day=1) - timedelta(days=1)
    else:
        return candidate


def monthdelta(d1, d2):
    delta = 0
    while True:
        mdays = monthrange(d1.year, d1.month)[1]
        d1 += timedelta(days=mdays)
        if d1 <= d2:
            delta += 1
        else:
            break
    return delta


def generate_date_seq(type, freq, list_date):
    now = date.today()
    last_dateseq = AnalysisDateSeq.objects.filter(
        seq_type=type).order_by('-analysis_date')
    last_snap_date = last_dateseq[0].analysis_date if last_dateseq is not None and len(
        last_dateseq) > 0 else list_date

    try:
        if freq == 'Y':
            pass
        elif freq == 'M':
            print(last_snap_date)
            md = monthdelta(last_snap_date, now)
            print(md)
            if md == 0:
                return False
            else:
                for i in range(0, md):
                    nearest_cal = get_nearest_trade_cal(
                        next_month(last_snap_date))
                    print(nearest_cal)
                    date_seq = AnalysisDateSeq(
                        seq_type=type, analysis_date=nearest_cal)
                    date_seq.save()
                    last_snap_date = nearest_cal
                    time.sleep(2)
                return True
        elif freq == 'D':
            pass
    except Exception as err:
        print(err)
        return False


def next_date(type='INDUSTRY_BASIC_QUANTILE'):
    last_dateseq = AnalysisDateSeq.objects.filter(
        seq_type=type, applied=False).order_by('-analysis_date')

    if last_dateseq is not None and len(last_dateseq) > 0:
        return last_dateseq

    return None


def last_date_seq(type='INDUSTRY_BASIC_QUANTILE'):
    last_dateseq = AnalysisDateSeq.objects.filter(
        seq_type=type, applied=True).order_by('-analysis_date').first()

    if last_dateseq is not None:
        return last_dateseq.analysis_date

    return None


def apply_analysis_date(type, date):
    try:
        dateseq = AnalysisDateSeq.objects.get(
            seq_type=type, analysis_date=date, applied=False)
        # if dateseq is not None and len(dateseq) > 0:
        dateseq.applied = True
        dateseq.save()
    except Exception as err:
        print(err)


# 20210930


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
