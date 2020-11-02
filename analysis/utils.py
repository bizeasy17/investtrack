from datetime import datetime, date, timedelta
from .models import StockStrategyTestLog, TradeStrategyStat,  StockHistoryDaily
# from investors.models import TradeStrategy
import tushare as ts


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


def set_task_completed(ts_code, event, freq, strategy_code, start_date, end_date):
    try:
        task = StockStrategyTestLog.objects.get(
            ts_code=ts_code, analysis_code=strategy_code, event_type=event, freq=freq, start_date=start_date, end_date=end_date, is_done=False)
        task.is_done = True
        task.last_mod_time = datetime.now()
    except Exception as e:
        print(e)
    task.save()


def generate_task(ts_code, freq, start_date, end_date, event_list=[], strategy_list=['jiuzhuan_bs', 'dingdi', 'tupo_yali_b', 'diepo_zhicheng_s',
                                                                                     'wm_dingdi_bs', 'junxian25_bs', 'junxian60_bs', 'junxian200_bs']):
    # event_list = ['MARK_CP', 'PERIOD_TEST', 'EXP_PCT_TEST']
    for event in event_list:
        for strategy in strategy_list:
            try:
                log = StockStrategyTestLog.objects.get(
                    ts_code=ts_code, analysis_code=strategy, event_type=event, freq=freq, end_date=start_date - timedelta(days=1), is_done=False)
                log.end_date = end_date
                # mark_log.save()
            except Exception as e:  # 未找到运行记录
                print(e)
                log = StockStrategyTestLog(ts_code=ts_code,
                                           analysis_code=strategy,
                                           event_type=event, freq=freq, start_date=start_date, end_date=end_date)
            log.save()


def has_analysis_task(ts_code, event, strategy_code, freq):
    try:
        mark_log = StockStrategyTestLog.objects.get(
            ts_code=ts_code, analysis_code=strategy_code, event_type=event, freq=freq, is_done=False)
        return True
    except Exception as e:
        # print(e)
        return False


def is_analyzed(ts_code, event, strategy_code, freq='D', is_done=True):
    try:
        mark_log = StockStrategyTestLog.objects.get(
            ts_code=ts_code, analysis_code=strategy_code, event_type=event, freq=freq, is_done=is_done)
        return True
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
                ts_code=ts_code, analysis_code=strategy_code, event_type=event, freq=freq, is_done=False)
        else:
            tasks = StockStrategyTestLog.objects.filter(
                ts_code=ts_code, event_type=event, freq=freq, is_done=False)
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
            print(e)
        offset += 1
    # print(last_trade-timedelta(days=offset))
    return offset


def get_closest_trade_cal(cur_date, exchange='SSE'):
    count = 0
    offset = 0
    pro = ts.pro_api()
    while count == 0:
        df = pro.trade_cal(exchange=exchange, start_date=(cur_date -
                                                          timedelta(days=offset)).strftime('%Y%m%d'), end_date=(cur_date-timedelta(days=offset)).strftime('%Y%m%d'))
        if df['is_open'].iloc[0] == 1:
            count += 1
        offset += 1
    # print(last_trade-timedelta(days=offset))
    return (cur_date - timedelta(days=offset))


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
            print(e)
        offset += 1
    # print(last_trade-timedelta(days=offset))
    return hist
