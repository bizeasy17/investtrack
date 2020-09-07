from datetime import datetime
from .models import StockStrategyTestLog, TradeStrategyStat
# from investors.models import TradeStrategy


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

def gen_cp_task(ts_code, freq, start_date, end_date):
    strategy_list = ['jiuzhuan_bs','dingdi','tupo_yali_b','diepo_zhicheng_s','wm_dingdi_bs','junxian25_bs']
    event_list = ['MARK_CP','PERIOD_TEST','EXP_PCT_TEST']
    for event in event_list:
        for strategy in strategy_list:
            try:
                mark_log = StockStrategyTestLog.objects.get(
                    ts_code=ts_code, analysis_code=strategy, event_type=event, freq=freq, is_done=True)
                mark_log.start_date = start_date
                mark_log.end_date = end_date
                mark_log.is_done = False
                # mark_log.save()
            except Exception as e: # 未找到运行记录
                # print(e)
                mark_log = StockStrategyTestLog(ts_code=ts_code,
                                                analysis_code=strategy,
                                                event_type=event, freq=freq, start_date=start_date, end_date=end_date)
                # try:
                #     strategy_stat = TradeStrategyStat.objects.get(applied_period=freq, code=strategy)
                #     strategy_stat.hist_analyzed = True
                #     strategy_stat.save()
                # except Exception as e:
                #     print(e)
            mark_log.save()

def has_analysis_task(ts_code, event, strategy_code, freq):
    try:
        mark_log = StockStrategyTestLog.objects.get(
            ts_code=ts_code, analysis_code=strategy_code, event_type=event, freq=freq, is_done=False)
        return True
    except Exception as e:
        # print(e)
        return False

def get_analysis_task(ts_code, event, strategy_code, freq):
    try:
        mark_log = StockStrategyTestLog.objects.get(
            ts_code=ts_code, analysis_code=strategy_code, event_type=event, freq=freq, is_done=False)
        return mark_log
    except Exception as e:
        # print(e)
        return None
