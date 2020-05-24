from datetime import datetime
from .models import StockStrategyTestLog


def log_test_status(ts_code, event, strategy_list=[]):
    for strategy in strategy_list:
        mark_log = StockStrategyTestLog(ts_code=ts_code,
                                        strategy=TradeStrategy.objects.get(
                                            code=strategy),
                                        event_type=event)
        mark_log.save()
