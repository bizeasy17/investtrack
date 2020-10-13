from datetime import datetime, date, timedelta
from .models import StockStrategyTestLog, TradeStrategyStat
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


def generate_systask(ts_code, freq, start_date, end_date, event_list=[]):
    strategy_list = ['jiuzhuan_bs', 'dingdi', 'tupo_yali_b', 'diepo_zhicheng_s',
                     'wm_dingdi_bs', 'junxian25_bs', 'junxian60_bs', 'junxian200_bs']
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
        task = StockStrategyTestLog.objects.get(
            ts_code=ts_code, analysis_code=strategy_code, event_type=event, freq=freq, is_done=False)
        return task
    except Exception as e:
        # print(e)
        return None


def get_trade_cal_diff(last_trade, exchange='SSE', period=4):
    count = 0
    offset = 0
    pro = ts.pro_api()
    while count < period:
        df = pro.trade_cal(exchange=exchange, start_date=(last_trade -
                                                          timedelta(days=offset+1)).strftime('%Y%m%d'), end_date=(last_trade-timedelta(days=offset+1)).strftime('%Y%m%d'))
        if df['is_open'].iloc[0] == 1:
            count += 1
        offset += 1
    print(last_trade-timedelta(days=offset))
    return offset


def pre_mark_b(df, df_close_diff4):
    pre_mark(df, df_close_diff4, 'b')


def pre_mark_s(df, df_close_diff4):
    pre_mark(df, df_close_diff4, 's')


def pre_mark(df, df_close_diff4, direction):
    '''
    标记股票的九转序列
    '''
    count = 0  # 九转买/卖计数器
    jiuzhuan_diff_list = []
    try:
        # 与4天前的收盘价比较
        for stock_hist in df_close_diff4.values:
            if stock_hist is not None:
                if direction == 'b':
                    if stock_hist < 0:  # 股价与往前第四个交易日比较，如果<前值，那么开始计算九转买点，
                        # 同时九转卖点设置为0
                        if count < 9:
                            count += 1
                        else:
                            count = 1
                    else:
                        count = 0
                else:
                    if stock_hist > 0:
                        # 同时九转卖点设置为0
                        if count < 9:
                            count += 1
                        else:
                            count = 1
                    else:
                        count = 0
                jiuzhuan_diff_list.append(count if count != 0 else np.nan)
            else:
                jiuzhuan_diff_list.append(np.nan)

        if direction == 'b':
            df['jiuzhuan_count_b'] = jiuzhuan_diff_list
        else:
            df['jiuzhuan_count_s'] = jiuzhuan_diff_list
    except:
        time.sleep(1)
    else:
        return df
