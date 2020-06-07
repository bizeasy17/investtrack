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


def test_exp_pct(strategy_code, ts_code_list=[], test_freq='D'):
    '''
    计算策略在某只股票涨幅达到10%，20% 。。。最小/大/平均时间
    1. 需要传入的参数为策略名称
    2. 遍历该股票测试策略买入
    3. 测试结果存入表
    '''
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
            df = pd.DataFrame()
            if test_freq == 'D':
                df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(
                    ts_code=listed_company.ts_code).order_by('trade_date').values())
            else:
                pass
            idx_list = []
            strategy_test_list = []
            if strategy_code.endswith('_b'):
                # 获得所有九转序列买点
                # 循环所有九转序列（时间顺序）
                # 获取当前买点往后所有交易记录（日）
                # 和当前买点比较，
                if not is_strategy_tested(listed_company.ts_code, 'EXP_PCT_TEST', 'jiuzhuan_b', test_freq):
                    idx_list = df.loc[df['jiuzhuan_count_b'] == 9].index
                    all_pct_list = []
                    log_list = []
                    for idx in idx_list:
                        b = df.iloc[idx]
                        pct_list = get_fixed_pct_list(df, b, strategy_code)
                        all_pct_list.append(pct_list)
                        # 买入点
                        # 	ts_code	trade_date	open	high	low	close	pre_close	change	pct_chg	vol	amount
                        b_tnx = BStrategyOnFixedPctTest(ts_code=b.ts_code, trade_date=b.trade_date, open=b.open, high=b.high,
                                                        low=b.low, close=b.close, pre_close=b.pre_close, change=b.change, pct_chg=b.pct_chg, vol=b.vol,
                                                        amount=b.amount, pct10_period=pct_list[
                                                            0], pct20_period=pct_list[1], pct30_period=pct_list[2],
                                                        pct50_period=pct_list[3], pct80_period=pct_list[4], pct100_period=pct_list[5],
                                                        pct130_period=pct_list[6], test_strategy=TradeStrategy.objects.get(code='jiuzhuan_b'), test_freq=test_freq)
                        strategy_test_list.append(b_tnx)
                    BStrategyOnFixedPctTest.objects.bulk_create(strategy_test_list)
                    post_exp_days_pct_test(all_pct_list)
                    log_test_status(listed_company.ts_code,
                                    'EXP_PCT_TEST', test_freq, ['jiuzhuan_b'])
            elif strategy_code.endswith('_b'):
                pass
    print(' test on period end - ' +
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'))        


def test_expected_pct(strategy_name, test_freq):
    log_list = []
    listed_companies = StockNameCodeMap.objects.filter
    for company in listed_companies:
        test_exp_pct(company.stock_symbol,
                              strategy_name, test_freq)
        log_test_status(company.stock_symbol, 'MARK_EXP_PCT',
                        test_freq, ['jiuzhuan_b'])
    # StockStrategyTestLog.objects.bulk_create(log_list)


def post_exp_days_pct_test(pct_list):
    '''
    计算在测试的策略下，达到10%，20%。。。的最大，最小，平均天数
    '''
    labels = ['pct10', 'pct20',
              'pct30', 'pct50', 'pct80', 'pct100', 'pct130',  'ts_code', 'strategy', ]
    df = pd.DataFrame.from_records(pct_list, columns=labels)
    ts_code = pct_list[0][7]
    test_strategy = pct_list[0][8]
    pct10_min = df[df['pct10'] != -1]['pct10'].min(axis=0)
    pct10_mean = df[df['pct10'] != -1]['pct10'].mean(axis=0)
    pct10_max = df[df['pct10'] != -1]['pct10'].max(axis=0)
    pct20_min = df[df['pct20'] != -1]['pct20'].min(axis=0)
    pct20_mean = df[df['pct20'] != -1]['pct20'].mean(axis=0)
    pct20_max = df[df['pct20'] != -1]['pct20'].max(axis=0)
    pct30_min = df[df['pct30'] != -1]['pct30'].min(axis=0)
    pct30_mean = df[df['pct30'] != -1]['pct30'].mean(axis=0)
    pct30_max = df[df['pct30'] != -1]['pct30'].max(axis=0)
    pct50_min = df[df['pct50'] != -1]['pct50'].min(axis=0)
    pct50_mean = df[df['pct50'] != -1]['pct50'].mean(axis=0)
    pct50_max = df[df['pct50'] != -1]['pct50'].max(axis=0)
    pct80_min = df[df['pct80'] != -1]['pct80'].min(axis=0)
    pct80_mean = df[df['pct80'] != -1]['pct80'].mean(axis=0)
    pct80_max = df[df['pct80'] != -1]['pct80'].max(axis=0)
    pct100_min = df[df['pct100'] != -1]['pct100'].min(axis=0)
    pct100_mean = df[df['pct100'] != -1]['pct100'].mean(axis=0)
    pct100_max = df[df['pct100'] != -1]['pct100'].max(axis=0)
    pct130_min = df[df['pct130'] != -1]['pct130'].min(axis=0)
    pct130_mean = df[df['pct130'] != -1]['pct130'].mean(axis=0)
    pct130_max = df[df['pct130'] != -1]['pct130'].max(axis=0)
    pct_test = BStrategyOnPctTest(ts_code=ts_code,
                                  b_10_pct_min=pct10_min, b_10_pct_mean=pct10_mean, b_10_pct_max=pct10_max,
                                  b_20_pct_min=pct20_min, b_20_pct_mean=pct20_mean, b_20_pct_max=pct20_max,
                                  b_30_pct_min=pct30_min, b_30_pct_mean=pct30_mean, b_30_pct_max=pct30_max,
                                  b_50_pct_min=pct50_min, b_50_pct_mean=pct50_mean, b_50_pct_max=pct50_max,
                                  b_80_pct_min=pct80_min, b_80_pct_mean=pct80_mean, b_80_pct_max=pct80_max,
                                  b_100_pct_min=pct100_min, b_100_pct_mean=pct100_mean, b_100_pct_max=pct100_max,
                                  b_130_pct_min=pct130_min, b_130_pct_mean=pct130_mean, b_130_pct_max=pct130_max,
                                  test_strategy=test_strategy)
    pct_test.save()


def get_pct_days_between(df, b, b_date, pct_incr):
    try:
        closest_date = df[(df['close'] >= b['close'] * pct_incr) &
                          (df['close'] <= b['close'] * (pct_incr + 0.05)) & (df['trade_date'] > b['trade_date'])].head(1).trade_date.values  # ??方法是否对？
        # pct_date = closest_date[0].strptime('%Y%m%d')
        pct_days = days_between(closest_date[0], b_date)
    except Exception as e:
        logger.error(e)
        pct_days = -1
    return pct_days


def get_fixed_pct_list(df, b, strategy_code):
    '''
    计算并返回10%，20% 。。。最小/大/平均时间
    '''
    fixed_pct_list = []
    try:
        b_date = b['trade_date']  # .strftime('%Y%m%d')
        # 实际达到15% - 20%，才能保证
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 1.10))
        # 实际达到28% - 29%，才能保证
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 1.20))
        # 实际达到40% - 41%，才能保证
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 1.30))
        # 50% - 51%
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 1.50))
        # 80% - 81%
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 1.80))
        # 100% - 101%
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 2.00))
        # 130% - 131%
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 2.30))
        # code
        fixed_pct_list.append(b['ts_code'])
        fixed_pct_list.append(TradeStrategy.objects.get(code='jiuzhuan_b'))
    except Exception as e:
        logger.err(e)
    return fixed_pct_list


def test_transaction_strategy():
    '''
    1. 获得股票交易历史
    get_stock_hist()
    2. 应用策略分析所有历史交易记录
    apply_given_strategy()
    3. 标记临界点（买，卖，加仓，减仓，平仓）
    mark_critical_point()
    4. 测试策略
    test_strategy()
    5. 记录策略测试结果
        - 方法1：给定测试周期，标记周期内最高最低点的涨幅%
        cal_low_high_pct()
        - 方法2：无输入值，测试达到涨幅10%。。。，130%需要的最大，最小和平均天数
        cal_exp_pct()
    '''
    pass
