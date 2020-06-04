from datetime import datetime
from .models import StockStrategyTestLog
from investors.models import TradeStrategy


def log_test_status(ts_code, event, strategy_list=[]):
    for strategy in strategy_list:
        try:
            mark_log = StockStrategyTestLog.objects.get(ts_code=ts_code, strategy=TradeStrategy.objects.get(
                code=strategy), event_type=event)
        except Exception as e:
            print(e)
            mark_log = StockStrategyTestLog(ts_code=ts_code,
                                            strategy=TradeStrategy.objects.get(
                                                code=strategy),
                                            event_type=event)
            mark_log.save()

def is_strategy_tested(ts_code, event, strategy_code):
    try:
        mark_log = StockStrategyTestLog.objects.get(ts_code=ts_code, strategy=TradeStrategy.objects.get(
            code=strategy_code), event_type=event)
        return True
    except Exception as e:
        print(e)
        return False
