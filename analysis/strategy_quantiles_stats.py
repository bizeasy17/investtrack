import pandas as pd
import logging

from .models import BStrategyOnFixedPctTest, StrategyTestLowHigh


def target_pct_stat(strategy, stock_symbol):
    try:
        quantile = []
        results = BStrategyOnFixedPctTest.objects.filter(
            strategy_code=strategy, ts_code=stock_symbol,
            test_freq=freq).order_by('trade_date').values('trade_date', exp_pct)  # [:int(freq_count)]
        df = pd.DataFrame(results.values())
        qtiles = df[exp_pct].quantile([0.25, 0.5, 0.75])
        # for qtile in qtiles.values():
        for index, value in qtiles.items():
            quantile.append(value)
        quantile.append(round(df[exp_pct].mean(), 3))
    except Exception as err:
        print(err)
        logging.error(err)


def updown_pct_stat(request, strategy, stock_symbol, test_period):
    try:
        result_pct = []
        result_label = []
        quantile = []
        results = StrategyTestLowHigh.objects.filter(
            strategy_code=strategy, ts_code=stock_symbol, test_period=test_period).order_by('trade_date')
        df = pd.DataFrame(results.values('stage_high_pct', 'stage_low_pct'))
        qtiles = df.stage_high_pct.quantile([0.25, 0.5, 0.75])
        for qtile in qtiles:
            quantile.append(round(qtile, 3))
        quantile.append(round(df.mean().stage_high_pct, 3))
    except IndexError as err:
        logging.error(err)
