from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
# from investors.models import TradeStrategy
import tushare as ts
from dashboard.utils import days_between

from .models import (AnalysisEventLog, StockHistoryDaily, StockStrategyTestLog,
                     StrategyTargetPctTestQuantiles,
                     StrategyUpDownTestQuantiles, TradeStrategyStat)

strategy_dict = {'jiuzhuan_bs': {'jiuzhuan_count_b', 'jiuzhuan_count_s'}, 'dingdi': {'dingbu_s', 'dibu_b'},
                 'tupo_yali_b': {'tupo_b'}, 'diepo_zhicheng_s': {'diepo_s'},  'wm_dingdi_bs': {'m_ding', 'w_di'},
                 'junxian25_bs': {'ma25_zhicheng', 'ma25_diepo', 'ma25_yali', 'ma25_tupo'},
                 'junxian60_bs': {'ma60_zhicheng', 'ma60_diepo', 'ma60_yali', 'ma60_tupo'},
                 'junxian200_bs': {'ma200_zhicheng', 'ma200_diepo', 'ma200_yali', 'ma200_tupo', }}


def log_test_status(ts_code, event, freq, strategy_list=[]):
    for strategy in strategy_list:
        try:
            mark_log = StockStrategyTestLog.objects.get(
                ts_code=ts_code, analysis_code=strategy, event_type=event, freq=freq, is_done=False)
            mark_log.is_done = True
        except Exception as e:
            # print(e)
            mark_log = StockStrategyTestLog(ts_code=ts_code,
                                            analysis_code=strategy,
                                            event_type=event, freq=freq, is_done=True)
            # try:
            #     strategy_stat = TradeStrategyStat.objects.get(applied_period=freq, code=strategy)
            #     strategy_stat.hist_analyzed = True
            #     strategy_stat.save()
            # except Exception as e:
            #     print(e)
        mark_log.save()


def gen_analysis_event(listed_company, start_date, end_date, strategy_list, freq='D'):
    '''
    1. 分析功能最少需要历史记录
        600d - 3年
    2. 选股功能最少需要历史记录
        各个策略不同,新股需要去除前x个交易日
    怎么判断？
    更新 - 1和新建 - 0
    下载 -> 下载完成 -> 是否存在event ？ ->
    -> 存在？ or 不存在？
    -> 存在（更新），说明已经成功生成任务列表 - 计算从上一次end_date -> today的交易历史
        -> 获取从end_date -> today的交易历史
        -> 分析功能
        -> if leng > 600
            -> event [EXP_PCT_TEST, UPDOWN_PCT_TEST, QTN_TEST, RANKING?]
        -> else
            -> 为所有策略生成所有event [MARK_CP]
    -> 不存在 - 计算从上市日list_date -> today的交易历史
        -> 获取从list_date -> today的交易历史
        -> 判断交易历史长度
            -> if leng > 600
                -> 为所有策略生成所有event [MARK_CP, EXP_PCT_TEST, UPDOWN_PCT_TEST, QTN_TEST, RANKING]
            -> else
                if  60 > len > 25
                    -> 生成ma25
                if  200 > len > 60
                    -> 生成 除了MA200以外所有event
                if len > 200
                    -> 生成ma200
    '''
    # event_list = ['MARK_CP', 'PERIOD_TEST', 'EXP_PCT_TEST', 'QTN_TEST', 'RANKING']
    analysis_event_list = ['EXP_PCT_TEST', 'PERIOD_TEST',
                           'TGT_PCT_QTN', 'UPDN_PCT_QTN', 'UPDN_PCT_RK', 'TGT_PCT_RK']
    threshold_hist_fx = 600

    # 如果hist length > 600，生成分析事件

    if days_between(start_date, end_date) >= threshold_hist_fx:
        for av in analysis_event_list:
            for strategy in strategy_list:
                event = StockStrategyTestLog(ts_code=listed_company.ts_code,
                                             analysis_code=strategy,
                                             event_type=av, freq=freq, start_date=start_date, end_date=end_date)
                event.save()
        listed_company.last_analyze_date = date.today()
        listed_company.save()
    # 如果hist length < 600, >= 25, 生成MA25 标记事件
    # if len(hist) < 600 and len(hist) >= 25:
    #     pass
    # 如果hist length < 600, >= 60, 生成MA60，突破，WM底，跌破，标记事件
    # if len(hist) < 600 and len(hist) >= 60:
    #     pass
    # 如果hist length < 600, >= 200, 生成MA200 标记事件
    # if len(hist) < 600 and len(hist) >= 200:
    #     pass


def gen_mark_event(ts_code, start_date, end_date, freq='D'):
    '''
    1. 分析功能最少需要历史记录
        600d - 3年
    2. 选股功能最少需要历史记录
        各个策略不同,新股需要去除前x个交易日
    怎么判断？
    更新 - 1和新建 - 0
    下载 -> 下载完成 -> 是否存在event ？ ->
    -> 存在？ or 不存在？
    -> 存在（更新），说明已经成功生成任务列表 - 计算从上一次end_date -> today的交易历史
        -> 获取从end_date -> today的交易历史
        -> 分析功能
        -> if leng > 600
            -> event [EXP_PCT_TEST, UPDOWN_PCT_TEST, QTN_TEST, RANKING?]
        -> else
            -> 为所有策略生成所有event [MARK_CP]
    -> 不存在 - 计算从上市日list_date -> today的交易历史
        -> 获取从list_date -> today的交易历史
        -> 判断交易历史长度
            -> if leng > 600
                -> 为所有策略生成所有event [MARK_CP, EXP_PCT_TEST, UPDOWN_PCT_TEST, QTN_TEST, RANKING]
            -> else
                if  60 > len > 25
                    -> 生成ma25
                if  200 > len > 60
                    -> 生成 除了MA200以外所有event
                if len > 200
                    -> 生成ma200
    '''
    # event_list = ['MARK_CP', 'PERIOD_TEST', 'EXP_PCT_TEST', 'QTN_TEST', 'RANKING']
    mark_cp_event_list = ['MARK_CP']
    strategy_cp_list = {'strategy_25': {'ma25_zhicheng', 'ma25_diepo', 'ma25_yali', 'ma25_tupo'},
                        'strategy_60': {'ma60_zhicheng', 'ma60_diepo', 'ma60_yali', 'ma60_tupo',
                                        'jiuzhuan_count_b', 'jiuzhuan_count_s', 'dingbu_s', 'dibu_b',
                                        'tupo_b', 'diepo_s', 'm_ding', 'w_di'},
                        'strategy_200': {'ma200_zhicheng', 'ma200_diepo', 'ma200_yali', 'ma200_tupo', }}
    threshold_hist_25 = 25
    threshold_hist_60 = 60
    threshold_hist_200 = 200

    # 如果hist length < 600, >= 25, 生成MA25 标记事件
    # if len(hist) < 600 and len(hist) >= 25:
    #     pass
    # 如果hist length < 600, >= 60, 生成MA60，突破，WM底，跌破，标记事件
    # if len(hist) < 600 and len(hist) >= 60:
    #     pass
    # 如果hist length < 600, >= 200, 生成MA200 标记事件
    # if len(hist) < 600 and len(hist) >= 200:
    #     pass

    if days_between(start_date, end_date) >= threshold_hist_200:
        for mv in mark_cp_event_list:
            for strategy in set.union(strategy_cp_list['strategy_200'], strategy_cp_list['strategy_60'], strategy_cp_list['strategy_25']):
                event = StockStrategyTestLog(ts_code=ts_code,
                                             analysis_code=strategy,
                                             event_type=mv, freq=freq, start_date=start_date, end_date=end_date)
                event.save()
    elif days_between(start_date, end_date) < threshold_hist_200 and days_between(start_date, end_date) >= threshold_hist_60:
        for mv in mark_cp_event_list:
            for strategy in set.union(strategy_cp_list['strategy_60'], strategy_cp_list['strategy_25']):
                event = StockStrategyTestLog(ts_code=ts_code,
                                             analysis_code=strategy,
                                             event_type=mv, freq=freq, start_date=start_date, end_date=end_date)
                event.save()
    elif days_between(start_date, end_date) < threshold_hist_60 and days_between(start_date, end_date) >= threshold_hist_25:
        for mv in mark_cp_event_list:
            for strategy in strategy_cp_list['strategy_25']:
                event = StockStrategyTestLog(ts_code=ts_code,
                                             analysis_code=strategy,
                                             event_type=mv, freq=freq, start_date=start_date, end_date=end_date)
                event.save()


def generate_event(listed_company, download_type=1, freq='D'):
    strategy_list = ['jiuzhuan_bs', 'dingdi', 'tupo_yali_b', 'diepo_zhicheng_s',
                     'wm_dingdi_bs', 'junxian25_bs', 'junxian60_bs', 'junxian200_bs']
    end_date = date.today()
    start_date = listed_company.last_analyze_date if listed_company.last_analyze_date is not None else listed_company.list_date
    mark_start_date = listed_company.list_date
    gen_analysis_event(listed_company, start_date,
                       end_date, strategy_list, freq)
    gen_mark_event(listed_company.ts_code, mark_start_date,
                   end_date, freq)


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


def ready2btest(ts_code, event, strategy_code, start_date, end_date, freq='D'):
    exec_date = date.today()
    completed = is_task_completed(
        ts_code, event, strategy_code=get_dict_key(strategy_dict, strategy_code) if event == 'MARK_CP' else strategy_code, start_date=start_date, end_date=end_date, freq=freq)

    if completed:
        print('previous '+event+' is completed')
        return True
    print('previous '+event+' is still ongoing/ not exist')
    return False


def set_task_completed(ts_code, event, freq, strategy_code, start_date, end_date):
    try:
        task = StockStrategyTestLog.objects.get(
            ts_code=ts_code, analysis_code=strategy_code, event_type=event, freq=freq, start_date=start_date, end_date=end_date, is_done=False)
        task.is_done = True
        task.last_mod_time = datetime.now()
        task.save()
    except Exception as e:
        print(e)


def generate_task(listed_company, start_date, end_date, freq='D', ):
    threshold_hist_fx = 600
    threshold_hist_25 = 25
    threshold_hist_60 = 60
    threshold_hist_200 = 200

    analysis_start_date = listed_company.last_analyze_date if listed_company.last_analyze_date is not None else listed_company.list_date
    mark_start_date = listed_company.list_date

    analysis_event_list = ['EXP_PCT_TEST', 'PERIOD_TEST',
                           'TGT_PCT_QTN', 'UPDN_PCT_QTN', 'UPDN_PCT_RK', 'TGT_PCT_RK']
    analysis_strategy_list = ['ma25_zhicheng', 'ma25_diepo', 'ma25_yali', 'ma25_tupo',
                              'ma60_zhicheng', 'ma60_diepo', 'ma60_yali', 'ma60_tupo',
                              'jiuzhuan_count_b', 'jiuzhuan_count_s', 'dingbu_s', 'dibu_b',
                              'tupo_b', 'diepo_s', 'm_ding', 'w_di',
                              'ma200_zhicheng', 'ma200_diepo', 'ma200_yali', 'ma200_tupo']
    mark_cp_event_list = ['MARK_CP']
    mark_strategy_set = {}
    mark_strategy_dict = {
        '25': {'junxian25_bs', 'jiuzhuan_bs'},
        '60': {'junxian60_bs', 'dingdi', 'tupo_yali_b', 'diepo_zhicheng_s',
               'wm_dingdi_bs', },
        '200': {'junxian200_bs'}
    }

    analysis_hist = StockHistoryDaily.objects.filter(
        ts_code=listed_company.ts_code, trade_date__gte=analysis_start_date, trade_date__lte=end_date)
    mark_hist = StockHistoryDaily.objects.filter(
        ts_code=listed_company.ts_code, trade_date__gte=mark_start_date, trade_date__lte=end_date)

    # 如果hist length > 600，生成分析事件
    if len(analysis_hist) >= threshold_hist_fx:
        mark_strategy_set = set.union(
            mark_strategy_dict['200'], mark_strategy_dict['60'], mark_strategy_dict['25'])

        for event in analysis_event_list:
            for strategy in analysis_strategy_list:
                try:
                    # tasks = get_analysis_task(ts_code, event, )
                    task = StockStrategyTestLog.objects.get(
                        ts_code=listed_company.ts_code, analysis_code=strategy, event_type=event, freq=freq, end_date=start_date - timedelta(days=1), is_done=False)
                    task.end_date = end_date
                    # mark_log.save()
                except Exception as e:  # 未找到运行记录
                    print(e)
                    task = StockStrategyTestLog(ts_code=listed_company.ts_code,
                                                analysis_code=strategy,
                                                event_type=event, freq=freq, start_date=start_date, end_date=end_date)
                task.save()
        listed_company.last_analyze_date = end_date
        # listed_company.save()
    else:
        # 如果hist length < 600, >= 25, 生成MA25 标记事件
        # if len(hist) < 600 and len(hist) >= 25:
        #     pass
        # 如果hist length < 600, >= 60, 生成MA60，突破，WM底，跌破，标记事件
        # if len(hist) < 600 and len(hist) >= 60:
        #     pass
        # 如果hist length < 600, >= 200, 生成MA200 标记事件
        # if len(hist) < 600 and len(hist) >= 200:
        #     pass
        if len(mark_hist) >= threshold_hist_200:
            mark_strategy_set = set.union(
                mark_strategy_dict['200'], mark_strategy_dict['60'], mark_strategy_dict['25'])
        else:
            if len(mark_hist) >= threshold_hist_60:
                mark_strategy_set = set.union(
                    mark_strategy_dict['25'], mark_strategy_dict['60'])
            else:
                if len(mark_hist) >= threshold_hist_25:
                    mark_strategy_set = mark_strategy_dict['25']

    for event in mark_cp_event_list:
        for strategy in mark_strategy_set:
            try:
                # tasks = get_analysis_task(ts_code, event, )
                task = StockStrategyTestLog.objects.get(
                    ts_code=listed_company.ts_code, analysis_code=strategy, event_type=event, freq=freq, end_date=start_date - timedelta(days=1), is_done=False)
                task.end_date = end_date
                # mark_log.save()
            except Exception as e:  # 未找到运行记录
                print(e)
                task = StockStrategyTestLog(ts_code=listed_company.ts_code,
                                            analysis_code=strategy,
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
        event.last_mod_time = datetime.now()
        event.save()
        return True
    except Exception as e:  # 未找到event log记录
        print(e)
        return False


def set_event_exception(event, exec_date, strategy_code=None, freq='D'):
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
        event.status = -1
        event.save()
    except Exception as e:  # 未找到event log记录
        print(e)


def is_task_completed(ts_code, event, strategy_code, start_date, end_date, freq):
    try:
        task = StockStrategyTestLog.objects.get(
            ts_code=ts_code, analysis_code=strategy_code, event_type=event,
            start_date=start_date, end_date=end_date, freq=freq)
        return task.is_done
    except Exception as e:
        # print(e)
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


def last_download_date(ts_code, event, freq):
    try:
        # 获得上一次下载记录
        log = StockStrategyTestLog.objects.filter(
            ts_code=ts_code, event_type=event, freq=freq).order_by('-end_date')[0]
        # print(log.start_date)
        # print(log.end_date)
        return [log.start_date, log.end_date]
    except Exception as e:
        print(e)
        return None


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


def get_trade_cal_diff(ts_code, last_trade, exchange='SSE', period=4):
    count = 0
    offset = 0
    # pro = ts.pro_api()
    while count < period:
        # df = pro.trade_cal(exchange=exchange, start_date=(last_trade -
        #                                                   timedelta(days=offset+1)).strftime('%Y%m%d'), end_date=(last_trade-timedelta(days=offset+1)).strftime('%Y%m%d'))
        # if df['is_open'].iloc[0] == 1:
        #     count += 1
        try:
            StockHistoryDaily.objects.get(
                ts_code=ts_code, trade_date=last_trade-timedelta(days=offset+1))
            count += 1
        except Exception as e:
            print(ts_code)
            print(e)
        offset += 1
    # print(last_trade-timedelta(days=offset))
    return offset


def get_closest_trade_cal(cur_date, exchange='SSE'):
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


def get_trade_cal_by_attr(ts_code, last_trade, attr='jiuzhuan_count_b'):
    hist = None
    it_is = False
    offset = 0
    # pro = ts.pro_api()
    while it_is:
        # df = pro.trade_cal(exchange=exchange, start_date=(last_trade -
        #                                                   timedelta(days=offset+1)).strftime('%Y%m%d'), end_date=(last_trade-timedelta(days=offset+1)).strftime('%Y%m%d'))
        # if df['is_open'].iloc[0] == 1:
        #     count += 1
        try:
            hist = StockHistoryDaily.objects.get(
                ts_code=ts_code, trade_date=last_trade-timedelta(days=offset+1))
            if getattr(hist, attr) == 1:
                it_is = True
        except Exception as e:
            print(ts_code)
            print(e)
        offset += 1
    # print(last_trade-timedelta(days=offset))
    return hist


def get_pct_val_from(pct_str):
    pct_arr = pct_str.split('_')
    pct_val = pct_arr[0][3:]
    return pct_val


def get_qt_updownpct(ts_code, strategy_code, period, test_type):
    result_qt = []
    results = StrategyUpDownTestQuantiles.objects.filter(
        strategy_code=strategy_code, ts_code=ts_code, test_period=period, test_type=test_type).order_by('test_period')
    for result in results:
        result_qt.append(
            {
                'period': result.test_period,
                'qt25ile': round(result.qt_10pct, 2),
                'qt50ile': round(result.qt_50pct, 2),
                'qt75ile': round(result.qt_75pct, 2),
                'max': round(result.max_val, 2),
                'min': round(result.min_val, 2),
                'mean': round(result.mean_val, 2),
            }
        )
    return result_qt


def get_qt_period_on_exppct(ts_code, strategy_code, exp_pct):
    result_qt = []
    results = StrategyTargetPctTestQuantiles.objects.filter(
        strategy_code=strategy_code, ts_code=ts_code, target_pct=exp_pct).order_by('test_freq')
    for result in results:
        result_qt.append(
            {
                'pct': get_pct_val_from(result.target_pct) + '%',
                'qt25ile': round(result.qt_10pct, 2),
                'qt50ile': round(result.qt_50pct, 2),
                'qt75ile': round(result.qt_75pct, 2),
                'min': round(result.min_val, 2),
                'mean': round(result.mean_val, 2),
            }
        )
    return result_qt


def get_pkdays_by_year_month(year, month):
    pass
