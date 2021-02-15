import logging
from datetime import date, datetime

import pandas as pd

from dashboard.utils import days_between
from investors.models import TradeStrategy
from stockmarket.models import StockNameCodeMap

from .models import (BStrategyOnFixedPctTest, BStrategyOnPctTest,
                     StrategyTestLowHigh, StockHistoryDaily,
                     TradeStrategyStat)
from .utils import get_analysis_task, set_task_completed, generate_task, ready2btest
from dashboard.utils import days_between

logger = logging.getLogger(__name__)


def btest_pct_on_period(ts_code, freq, strategy_code, ):
    try:

        if ts_code is None:
            listed_companies = StockNameCodeMap.objects.filter()
        else:
            ts_code_list = ts_code.split(',')
            if ts_code_list is not None and len(ts_code_list) >= 1:
                listed_companies = StockNameCodeMap.objects.filter(
                    ts_code__in=ts_code_list)
        for listed_company in listed_companies:
            print(listed_company)
            # print(listed_company.ts_code + ' for strategy ' +
            #       strategy_code + ' pct started')
            tasks = get_analysis_task(
                listed_company.ts_code, 'PERIOD_TEST', strategy_code, freq)
            if tasks is not None and len(tasks) > 0:
                for task in tasks:
                    # if ready2btest(listed_company.ts_code, 'MARK_CP', strategy_code, task.start_date, task.end_date, freq):
                    if days_between(task.start_date, task.end_date) >= 365 * 3: #分析至少需要三年的数据
                        test_by_period(strategy_code, listed_company.ts_code,
                                    task.start_date, task.end_date, freq)
                        set_task_completed(listed_company.ts_code, 'PERIOD_TEST',
                                        freq, strategy_code, task.start_date, task.end_date)
                        # generate_task(listed_company.ts_code,
                        #             test_freq, task.start_date, task.end_date, event_list=['UPDN_PCT_QTN'], strategy_list=[strategy_code])
            else:
                print(listed_company.ts_code + ' for strategy ' +
                      strategy_code + ' pct has tested already / no task')
    except Exception as e:
        print(e)


def test_by_period(strategy_code, ts_code, start_date, end_date, freq, list_days=200):
    '''
    计算策略在某只股票上在某个时间周期上的最小/大，和平均涨跌幅值的统计
    1. 需要传入的参数为策略名称
    2. 遍历该股票测试策略买入或则卖出点记录
    3. 根据测试周期获取从买入点或者卖出点开始最大/小，平均涨跌幅
    4. 测试结果存入表
    '''
    # end_date = date.today()
    periods = [10, 20, 30, 50, 80, 130, 210, 350, 560]
    # periods = [130, 210, 350, 560]

    # if strategy_code.startswith('jiuzhuan_'):
    print(' test on low/high for ' + strategy_code + ' start - ' +
          ts_code + ' at ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    df = pd.DataFrame()
    idx_list = []
    idx_list_period = []
    strategy_test_list = []
    # if strategy_code.endswith('_b'): not needed, 20200617
    if freq == 'D':
        df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(
            ts_code=ts_code).order_by('trade_date').values())
    else:
        pass
    if df is not None and len(df) >= list_days:
        # 根据策略获取标注的关键点index
        if strategy_code.startswith('jiuzhuan_'):
            # split = strategy_code.split('_')
            idx_list = df.loc[df[strategy_code] == 9].index
        else:
            idx_list = df.loc[df[strategy_code] == 1].index

        # if strategy_code == 'jiuzhuan_b':
        #     idx_list = df.loc[df['jiuzhuan_count_b'] == 9].index
        # elif strategy_code == 'jiuzhuan_s':
        #     idx_list = df.loc[df['jiuzhuan_count_s'] == 9].index
        # elif strategy_code == 'dibu_b':
        #     idx_list = df.loc[df['di_min'] == 1].index
        # elif strategy_code == 'dingbu_s':
        #     idx_list = df.loc[df['ding_max'] == 1].index
        # elif strategy_code == 'w_di':
        #     idx_list = df.loc[df['w_di'] == 1].index
        # elif strategy_code == 'm_ding':
        #     idx_list = df.loc[df['m_ding'] == 1].index
        # elif strategy_code == 'tupo_yali_b':
        #     idx_list = df.loc[df['tupo_b'] == 1].index
        # elif strategy_code == 'diepo_zhicheng_s':
        #     idx_list = df.loc[df['diepo_s'] == 1].index
        # elif strategy_code == 'ma25_zhicheng_b':
        #     idx_list = df.loc[df['ma25_zhicheng_b'] == 1].index
        # elif strategy_code == 'ma25_tupo_b':
        #     idx_list = df.loc[df['ma25_tupo_b'] == 1].index
        # elif strategy_code == 'ma25_diepo_s':
        #     idx_list = df.loc[df['ma25_diepo_s'] == 1].index
        # elif strategy_code == 'ma25_yali_s':
        #     idx_list = df.loc[df['ma25_yali_s'] == 1].index

        for test_period in periods:
            for idx in idx_list:
                idx_list_period = [id for id in range(
                    idx, idx + int(test_period))]
                if idx + int(test_period) <= len(df.index):
                    cp_close = df.iloc[idx]['close']
                    critical_point = df.iloc[idx]
                    idx_max = df.iloc[idx_list_period]['close'].idxmax(
                        axis=0)
                    idx_min = df.iloc[idx_list_period]['close'].idxmin(
                        axis=0)
                    max_c = df.iloc[idx_list_period]['close'].max(
                        axis=0)
                    min_c = df.iloc[idx_list_period]['close'].min(
                        axis=0)
                    pct_up = round(
                        (max_c - cp_close) / cp_close * 100, 3)
                    pct_down = round(
                        (min_c - cp_close) / cp_close * 100, 3)

                    # print('Jiu zhuan buy...')
                    # print(b)
                    # print('Jiu zhuan min...')
                    # print(df.iloc[idx_min])
                    # print('Jiu zhuan max...')mayiant
                    # print(df.iloc[idx_max])

                    # 买入点
                    # for v in b.values:
                    # 	ts_code	trade_date	open	high	low	close	pre_close	change	pct_chg	vol	amount
                    # b_tnx = BStrategyTestResultOnDays(ts_code=b.ts_code, trade_date=b.trade_date, test_period=test_period,
                    #                                     # open=b.open, high=b.high, low=b.low, close=b.close, pre_close=b.pre_close,
                    #                                     # change=b.change, pct_chg=b.pct_chg, vol=b.vol, amount=b.amount,
                    #                                     tnx_point=True, strategy_code=strategy_code)
                    # 查询周期内最高价
                    found_max = df.iloc[idx_max]
                    # 查询周期内最低价
                    found_min = df.iloc[idx_min]
                    # 	ts_code	trade_date	open	high	low	close	pre_close	change	pct_chg	vol	amount
                    test_by_day = StrategyTestLowHigh(ts_code=critical_point.ts_code, trade_date=critical_point.trade_date, test_period=test_period,
                                                      stage_high_date=found_max.trade_date, stage_high_pct=pct_up, stage_low_date=found_min.trade_date, 
                                                      stage_low_pct=pct_down, strategy_code=strategy_code, ma25_slope=df.iloc[idx]['ma25_slope'], 
                                                      ma60_slope=df.iloc[idx]['ma60_slope'], ma200_slope=df.iloc[idx]['ma200_slope'], 
                                                      vol=df.iloc[idx]['vol'], amount=df.iloc[idx]['amount'], freq= freq)
                    # test_min = BStrategyTestResultOnDays(ts_code=min.ts_code, trade_date=min.trade_date, test_period=test_period,
                    #                                         # open=min.open, high=min.high, low=min.low, close=min.close, pre_close=min.pre_close,
                    #                                         # change=min.change, pct_chg=min.pct_chg, vol=min.vol, amount=min.amount,
                    #                                         stage_low=True, stage_low_pct=pct_down, strategy_code=strategy_code)
                    # strategy_test_list.append(b_tnx)
                    # strategy_test_list.append(test_min)
                    strategy_test_list.append(test_by_day)
        if len(strategy_test_list) > 0:
            StrategyTestLowHigh.objects.bulk_create(strategy_test_list)
    else:
        print('not enough data, list days less than 1 year for ' +
              ts_code + ' at ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(' test end on low/high strategy ' + strategy_code + ' , for ' +
          ts_code + ' at ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
