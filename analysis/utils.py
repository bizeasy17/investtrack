from datetime import datetime
from .models import StockStrategyTestLog


def log_test_status(log_list, ts_code, event, strategy_list=[]):
    for strategy in strategy_list:
        mark_log = StockStrategyTestLog(ts_code=ts_code,
                                        strategy=TradeStrategy.objects.get(
                                            code=strategy),
                                        event_type=event)
        log_list.append(mark_log)
    return log_list
