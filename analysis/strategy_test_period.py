import logging
from datetime import date, datetime

import pandas as pd

from dashboard.utils import days_between
from investors.models import TradeStrategy
from stockmarket.models import StockNameCodeMap

from .models import (BStrategyOnFixedPctTest, BStrategyOnPctTest,
                     BStrategyTestResultOnDays, StockHistoryDaily,
                     TradeStrategyStat)
from .utils import log_test_status, is_strategy_tested

logger = logging.getLogger(__name__)


def test_by_period(ts_code_list, strategy_code):
    '''
    计算策略在某只股票上在某个时间周期上的最小/大，和平均涨跌幅值的统计
    1. 需要传入的参数为策略名称
    2. 遍历该股票测试策略买入或则卖出点记录
    3. 根据测试周期获取从买入点或者卖出点开始最大/小，平均涨跌幅
    4. 测试结果存入表
    '''
    # end_date = date.today()
    periods = [10, 20, 30, 50, 80]
    print(' test on period start - ' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    if strategy_code.startswith('jiuzhuan_'):
        if len(ts_code_list) == 0:
            listed_companies = StockNameCodeMap.objects.filter(
                is_marked_jiuzhuan=True)
        else:
            listed_companies = StockNameCodeMap.objects.filter(
                is_marked_jiuzhuan=True, ts_code__in=ts_code_list)
        for listed_company in listed_companies:
            df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(
                ts_code=listed_company.ts_code).order_by('trade_date').values())
            idx_list = []
            idx_list_period = []
            strategy_test_list = []
            if strategy_code.endswith('_b'):
                if not is_strategy_tested(listed_company.ts_code, 'PERIOD_TEST', 'jiuzhuan_b'):
                    idx_list = df.loc[df['jiuzhuan_count_b'] == 9].index
                    for test_period in periods:
                        for idx in idx_list:
                            idx_list_period = [id for id in range(
                                idx, idx + int(test_period))]
                            if idx + int(test_period) <= len(df.index):
                                b_close = df.iloc[idx]['close']
                                b = df.iloc[idx]
                                idx_max = df.iloc[idx_list_period]['close'].idxmax(
                                    axis=0)
                                idx_min = df.iloc[idx_list_period]['close'].idxmin(
                                    axis=0)
                                max_c = df.iloc[idx_list_period]['close'].max(
                                    axis=0)
                                min_c = df.iloc[idx_list_period]['close'].min(
                                    axis=0)
                                pct_incr = round(
                                    (max_c - b_close) / b_close * 100, 3)
                                pct_drop = round(
                                    (min_c - b_close) / b_close * 100, 3)

                                # print('Jiu zhuan buy...')
                                # print(b)
                                # print('Jiu zhuan min...')
                                # print(df.iloc[idx_min])
                                # print('Jiu zhuan max...')
                                # print(df.iloc[idx_max])

                                # 买入点
                                # for v in b.values:
                                # 	ts_code	trade_date	open	high	low	close	pre_close	change	pct_chg	vol	amount
                                b_tnx = BStrategyTestResultOnDays(ts_code=b.ts_code, trade_date=b.trade_date, test_period=test_period, open=b.open, high=b.high,
                                                                  low=b.low, close=b.close, pre_close=b.pre_close, change=b.change, pct_chg=b.pct_chg, vol=b.vol,
                                                                  amount=b.amount, tnx_point=True, test_strategy=TradeStrategy.objects.get(code='jiuzhuan_b'))
                                # 查询周期内最高价
                                max = df.iloc[idx_max]
                                # 	ts_code	trade_date	open	high	low	close	pre_close	change	pct_chg	vol	amount
                                test_max = BStrategyTestResultOnDays(ts_code=max.ts_code, trade_date=max.trade_date, test_period=test_period, open=max.open, high=max.high,
                                                                     low=max.low, close=max.close, pre_close=max.pre_close, change=max.change, pct_chg=max.pct_chg, vol=max.vol,
                                                                     amount=max.amount, stage_high=True, stage_high_pct=pct_incr, test_strategy=TradeStrategy.objects.get(code='jiuzhuan_b'))
                                # 查询周期内最低价
                                min = df.iloc[idx_min]
                                test_min = BStrategyTestResultOnDays(ts_code=min.ts_code, trade_date=min.trade_date, test_period=test_period, open=min.open, high=min.high,
                                                                     low=min.low, close=min.close, pre_close=min.pre_close, change=min.change, pct_chg=min.pct_chg, vol=min.vol,
                                                                     amount=min.amount, stage_low=True, stage_low_pct=pct_drop, test_strategy=TradeStrategy.objects.get(code='jiuzhuan_b'))
                                strategy_test_list.append(b_tnx)
                                strategy_test_list.append(test_min)
                                strategy_test_list.append(test_max)
            log_test_status(listed_company.ts_code,
                            'PERIOD_TEST', ['jiuzhuan_b'])
            BStrategyTestResultOnDays.objects.bulk_create(strategy_test_list)
    else:
        idx_list = df.loc[df['jiuzhuan_s'] == 9]
        # idx = df.loc[df['close'] > 16.66].index
        # df.iloc[idx]
    print(' test on period end - ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def test_by_period1(stock_symbol, strategy_code, test_period):
    '''
    计算策略在某只股票上在某个时间周期上的最小/大，和平均涨跌幅值的统计
    1. 需要传入的参数为策略名称
    2. 遍历该股票测试策略买入或则卖出点记录
    3. 根据测试周期获取从买入点或者卖出点开始最大/小，平均涨跌幅
    4. 测试结果存入表
    '''
    # end_date = date.today()
    periods = [10, 20, 30, 50, 80]
    if len(ts_code_list) == 0:
        listed_companies = StockNameCodeMap.objects.filter(
            is_marked_jiuzhuan=False)
    else:
        listed_companies = StockNameCodeMap.objects.filter(
            is_marked_jiuzhuan=False, ts_code__in=ts_code_list)

    if strategy_code.startswith('jiuzhuan_'):
        df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(
            ts_code=stock_symbol).order_by('trade_date').values())
        idx_list = []
        idx_list_period = []
        strategy_test_list = []
        if strategy_code.endswith('_b'):
            idx_list = df.loc[df['jiuzhuan_count_b'] == 9].index
            for idx in idx_list:
                idx_list_period = [id for id in range(
                    idx, idx + int(test_period))]
                b_close = df.iloc[idx]['close']
                b = df.iloc[idx]
                idx_max = df.iloc[idx_list_period]['close'].idxmax(axis=0)
                idx_min = df.iloc[idx_list_period]['close'].idxmin(axis=0)
                max_c = df.iloc[idx_list_period]['close'].max(axis=0)
                min_c = df.iloc[idx_list_period]['close'].min(axis=0)
                pct_incr = round((max_c - b_close) / b_close * 100, 3)
                pct_drop = round((min_c - b_close) / b_close * 100, 3)

                # print('Jiu zhuan buy...')
                # print(b)
                # print('Jiu zhuan min...')
                # print(df.iloc[idx_min])
                # print('Jiu zhuan max...')
                # print(df.iloc[idx_max])

                # 买入点
                # for v in b.values:
                # 	ts_code	trade_date	open	high	low	close	pre_close	change	pct_chg	vol	amount
                b_tnx = BStrategyTestResultOnDays(ts_code=b.ts_code, trade_date=b.trade_date, test_period=test_period, open=b.open, high=b.high,
                                                  low=b.low, close=b.close, pre_close=b.pre_close, change=b.change, pct_chg=b.pct_chg, vol=b.vol,
                                                  amount=b.amount, tnx_point=True, test_strategy=TradeStrategy.objects.get(code='jiuzhuan_b'))
                # 查询周期内最高价
                max = df.iloc[idx_max]
                # 	ts_code	trade_date	open	high	low	close	pre_close	change	pct_chg	vol	amount
                test_max = BStrategyTestResultOnDays(ts_code=max.ts_code, trade_date=max.trade_date, test_period=test_period, open=max.open, high=max.high,
                                                     low=max.low, close=max.close, pre_close=max.pre_close, change=max.change, pct_chg=max.pct_chg, vol=max.vol,
                                                     amount=max.amount, stage_high=True, stage_high_pct=pct_incr, test_strategy=TradeStrategy.objects.get(code='jiuzhuan_b'))
                # 查询周期内最低价
                min = df.iloc[idx_min]
                test_min = BStrategyTestResultOnDays(ts_code=min.ts_code, trade_date=min.trade_date, test_period=test_period, open=min.open, high=min.high,
                                                     low=min.low, close=min.close, pre_close=min.pre_close, change=min.change, pct_chg=min.pct_chg, vol=min.vol,
                                                     amount=min.amount, stage_low=True, stage_low_pct=pct_drop, test_strategy=TradeStrategy.objects.get(code='jiuzhuan_b'))
                strategy_test_list.append(b_tnx)
                strategy_test_list.append(test_min)
                strategy_test_list.append(test_max)
            BStrategyTestResultOnDays.objects.bulk_create(strategy_test_list)
        else:
            idx_list = df.loc[df['jiuzhuan_s'] == 9]
        # idx = df.loc[df['close'] > 16.66].index
        # df.iloc[idx]
