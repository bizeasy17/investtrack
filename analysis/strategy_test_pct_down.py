import logging
from datetime import date, datetime

import pandas as pd

from dashboard.utils import days_between
from investors.models import TradeStrategy
from stockmarket.models import StockNameCodeMap

from .models import (StrategyOnFixedDownPctTest, StrategyOnDownPctTest, StockHistoryDaily,
                     TradeStrategyStat)
from .utils import log_test_status, is_strategy_tested

logger = logging.getLogger(__name__)


def test_exp_down_pct(strategy_code, ts_code_list=[], test_freq='D'):
    '''
    计算策略在某只股票涨幅达到10%，20% 。。。最小/大/平均时间
    1. 需要传入的参数为策略名称
    2. 遍历该股票测试策略买入
    3. 测试结果存入表
    '''
    # if strategy_code.startswith('jiuzhuan_'):
    # print(ts_code_list)
    if len(ts_code_list) == 0:
        listed_companies = StockNameCodeMap.objects.filter(is_hist_downloaded=True)
    else:
        listed_companies = StockNameCodeMap.objects.filter(is_hist_downloaded=True, ts_code__in=ts_code_list)
    # print(len(listed_companies))
    for listed_company in listed_companies:
        print(' test on down pct start - ' + listed_company.ts_code + ' - ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        df = pd.DataFrame()
        idx_list = []
        strategy_test_list = []
        # if strategy_code.endswith('_b'): not used
        # 获得所有九转序列买点
        # 循环所有九转序列（时间顺序）
        # 获取当前买点往后所有交易记录（日）
        # 和当前买点比较，
        if not is_strategy_tested(listed_company.ts_code, 'EXP_DOWN_PCT_TEST', strategy_code, test_freq):
            all_pct_list = []
            log_list = []

            if test_freq == 'D':
                df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(
                    ts_code=listed_company.ts_code).order_by('trade_date').values())
            else:
                pass
            # 根据策略获取标注的关键点index
            if strategy_code == 'jiuzhuan_s':
                idx_list = df.loc[df['jiuzhuan_count_s'] == 9].index
            elif strategy_code == 'dingbu_s':
                idx_list = df.loc[df['ding_max'] == 1].index
            elif strategy_code == 'm_ding':
                idx_list = df.loc[df['m_ding'] == 1].index
            elif strategy_code == 'diepo_zhicheng_s': 
                idx_list = df.loc[df['diepo_s'] == 1].index
            elif strategy_code == 'ma25_diepo_s':
                idx_list = df.loc[df['ma25_diepo_s'] == 1].index
            elif strategy_code == 'ma25_yali_s':
                idx_list = df.loc[df['ma25_yali_s'] == 1].index
            
            # print(len(idx_list))

            for idx in idx_list:
                critical_point = df.iloc[idx]
                pct_list = get_fixed_pct_list(df, critical_point, strategy_code)
                all_pct_list.append(pct_list)
                # 买入点
                # 	ts_code	trade_date	open	high	low	close	pre_close	change	pct_chg	vol	amount
                b_tnx = StrategyOnFixedDownPctTest(ts_code=critical_point.ts_code, trade_date=critical_point.trade_date, 
                                                # open=b.open, high=b.high, low=b.low, close=b.close, pre_close=b.pre_close, 
                                                # change=b.change, pct_chg=b.pct_chg, vol=b.vol, amount=b.amount, 
                                                pct10_period=pct_list[0], pct20_period=pct_list[1], pct30_period=pct_list[2],
                                                pct50_period=pct_list[3], pct80_period=pct_list[4], strategy_code=strategy_code, 
                                                test_freq=test_freq)
                strategy_test_list.append(b_tnx)
            if len(strategy_test_list) > 0:
                StrategyOnFixedDownPctTest.objects.bulk_create(strategy_test_list)
                post_exp_days_pct_test(all_pct_list)
                log_test_status(listed_company.ts_code,
                                'EXP_DOWN_PCT_TEST', test_freq, [strategy_code])
            print(' test on down pct end - '  + listed_company.ts_code + ' - ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))        
        else:
            print(listed_company.ts_code + ' for strategy ' + strategy_code + ' down pct has tested already')

def post_exp_days_pct_test(pct_list):
    '''
    计算在测试的策略下，达到10%，20%。。。的最大，最小，平均天数
    '''
    labels = ['pct10', 'pct20',
              'pct30', 'pct50', 'pct80', 'ts_code', 'strategy', ]
    df = pd.DataFrame.from_records(pct_list, columns=labels)
    ts_code = pct_list[0][5]
    test_strategy = pct_list[0][6]
    print(df.head(50))
    return
    pct10_min = df[not df['pct10'].isnull()]['pct10'].min(axis=0)
    pct10_mean = df[not df['pct10'].isnull()]['pct10'].mean(axis=0)
    pct10_max = df[not df['pct10'].isnull()]['pct10'].max(axis=0)
    pct20_min = df[not df['pct20'].isnull()]['pct20'].min(axis=0)
    pct20_mean = df[not df['pct20'].isnull()]['pct20'].mean(axis=0)
    pct20_max = df[not df['pct20'].isnull()]['pct20'].max(axis=0)
    pct30_min = df[not df['pct30'].isnull()]['pct30'].min(axis=0)
    pct30_mean = df[not df['pct30'].isnull()]['pct30'].mean(axis=0)
    pct30_max = df[not df['pct30'].isnull()]['pct30'].max(axis=0)
    pct50_min = df[not df['pct50'].isnull()]['pct50'].min(axis=0)
    pct50_mean = df[not df['pct50'].isnull()]['pct50'].mean(axis=0)
    pct50_max = df[not df['pct50'].isnull()]['pct50'].max(axis=0)
    pct80_min = df[not df['pct80'].isnull()]['pct80'].min(axis=0)
    pct80_mean = df[not df['pct80'].isnull()]['pct80'].mean(axis=0)
    pct80_max = df[not df['pct80'].isnull()]['pct80'].max(axis=0)
    pct_test = StrategyOnDownPctTest(ts_code=ts_code,
                                  down_10pct_min=pct10_min, down_10pct_mean=round(pct10_mean,2), down_10pct_pct_max=pct10_max,
                                  down_20pct_min=pct20_min, down_20pct_mean=round(pct20_mean,2), down_20pct_max=pct20_max,
                                  down_30pct_min=pct30_min, down_30pct__mean=round(pct30_mean,2), down_30pct_max=pct30_max,
                                  down_50pct_min=pct50_min, down_50pct_mean=round(pct50_mean,2), down_50pct_max=pct50_max,
                                  down_80pct_min=pct80_min, down_80pct_mean=round(pct80_mean,2), down_80pct_max=pct80_max,
                                  strategy_code=test_strategy)
    pct_test.save()


def get_pct_days_between(df, b, trade_date, pct_down):
    try:
        closest_date = df[(df['close'] <= b['close'] * pct_down) &
                          (df['close'] >= b['close'] * (pct_down - 0.01)) & (df['trade_date'] > b['trade_date'])].head(1).trade_date.values  # ??方法是否对？
        # pct_date = closest_date[0].strptime('%Y%m%d')
        pct_days = days_between(closest_date[0], trade_date)
    except Exception as e:
        # logger.error(e)
        pct_days = None
    return pct_days


def get_fixed_pct_list(df, critical_point, strategy_code):
    '''
    计算并返回10%，20% 。。。最小/大/平均时间
    '''
    fixed_pct_list = []
    try:
        trade_date = critical_point['trade_date']  # .strftime('%Y%m%d')
        # 实际达到15% - 20%，才能保证
        fixed_pct_list.append(get_pct_days_between(df, critical_point, trade_date, -1.10))
        # 实际达到28% - 29%，才能保证
        fixed_pct_list.append(get_pct_days_between(df, critical_point, trade_date, -1.20))
        # 实际达到40% - 41%，才能保证
        fixed_pct_list.append(get_pct_days_between(df, critical_point, trade_date, -1.30))
        # 50% - 51%
        fixed_pct_list.append(get_pct_days_between(df, critical_point, trade_date, -1.50))
        # 80% - 81%
        fixed_pct_list.append(get_pct_days_between(df, critical_point, trade_date, -1.80))
        # code
        fixed_pct_list.append(critical_point['ts_code'])
        # fixed_pct_list.append(TradeStrategy.objects.get(code='jiuzhuan_b'))
        fixed_pct_list.append(strategy_code)
    except Exception as e:
        # logger.error(e)
        pass
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
