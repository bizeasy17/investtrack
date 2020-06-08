from datetime import datetime
from .models import StockStrategyTestLog, TradeStrategyStat
# from investors.models import TradeStrategy


def log_test_status(ts_code, event, freq, strategy_list=[]):
    for strategy in strategy_list:
        try:
            mark_log = StockStrategyTestLog.objects.get(
                ts_code=ts_code, analysis_code=strategy, event_type=event, freq=freq)
        except Exception as e:
            print(e)
            mark_log = StockStrategyTestLog(ts_code=ts_code,
                                            analysis_code=strategy,
                                            event_type=event, freq=freq)
            # try:
            #     strategy_stat = TradeStrategyStat.objects.get(applied_period=freq, code=strategy)
            #     strategy_stat.hist_analyzed = True
            #     strategy_stat.save()
            # except Exception as e:
            #     print(e)
            mark_log.save()


def is_strategy_tested(ts_code, event, strategy_code, freq):
    try:
        mark_log = StockStrategyTestLog.objects.get(
            ts_code=ts_code, analysis_code=strategy_code, event_type=event, freq=freq)
        return True
    except Exception as e:
        print(e)
        return False
