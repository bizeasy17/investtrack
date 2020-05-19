import pandas as pd
import logging
from datetime import datetime, date
from dashboard.utils import days_between
from .models import StockHistoryDaily, TradeStrategyStat, BStrategyTestResultOnDays, BStrategyOnFixedPctTest, BStrategyOnPctTest
from investors.models import TradeStrategy

logger = logging.getLogger(__name__)


def test_strategy_on_days(stock_symbol, strategy_name, test_period):
    '''
    计算策略在某只股票上在某个时间周期上的最小/大，和平均涨跌幅值的统计
    1. 需要传入的参数为策略名称
    2. 遍历该股票测试策略买入或则卖出点记录
    3. 根据测试周期获取从买入点或者卖出点开始最大/小，平均涨跌幅
    4. 测试结果存入表
    '''
    if strategy_name.startswith('jz_'):
        df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(
            ts_code=stock_symbol).order_by('trade_date').values())
        idx_list = []
        idx_list_period = []
        strategy_test_list = []
        if strategy_name.endswith('_b'):
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
                b_tnx = BStrategyTestResultOnDays(ts_code=b.ts_code, trade_date=b.trade_date, open=b.open, high=b.high,
                                                  low=b.low, close=b.close, pre_close=b.pre_close, change=b.change, pct_chg=b.pct_chg, vol=b.vol,
                                                  amount=b.amount, tnx_point=True, test_strategy=TradeStrategy.objects.get(code='jz_b'))
                # 查询周期内最高价
                max = df.iloc[idx_max]
                # 	ts_code	trade_date	open	high	low	close	pre_close	change	pct_chg	vol	amount
                test_max = BStrategyTestResultOnDays(ts_code=max.ts_code, trade_date=max.trade_date, open=max.open, high=max.high,
                                                     low=max.low, close=max.close, pre_close=max.pre_close, change=max.change, pct_chg=max.pct_chg, vol=max.vol,
                                                     amount=max.amount, stage_high=True, stage_high_pct=pct_incr, test_strategy=TradeStrategy.objects.get(code='jz_b'))
                # 查询周期内最低价
                min = df.iloc[idx_min]
                test_min = BStrategyTestResultOnDays(ts_code=min.ts_code, trade_date=min.trade_date, open=min.open, high=min.high,
                                                     low=min.low, close=min.close, pre_close=min.pre_close, change=min.change, pct_chg=min.pct_chg, vol=min.vol,
                                                     amount=min.amount, stage_low=True, stage_low_pct=pct_drop, test_strategy=TradeStrategy.objects.get(code='jz_b'))
                strategy_test_list.append(b_tnx)
                strategy_test_list.append(test_min)
                strategy_test_list.append(test_max)
            BStrategyTestResultOnDays.objects.bulk_create(strategy_test_list)
        else:
            idx_list = df.loc[df['jiuzhuan_s'] == 9]
        # idx = df.loc[df['close'] > 16.66].index
        # df.iloc[idx]
    pass


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


def get_fixed_pct_list(df, b):
    '''
    计算并返回10%，20% 。。。最小/大/平均时间
    '''
    fixed_pct_list = []
    try:
        b_date = b['trade_date']  # .strftime('%Y%m%d')
        # 15% - 20%
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 1.15))
        # 28% - 29%
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 1.28))
        # 40% - 41%
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 1.40))
        # 50% - 51%
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 1.50))
        # 80% - 81%
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 1.80))
        # 100% - 101%
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 2.00))
        # 130% - 131%
        fixed_pct_list.append(get_pct_days_between(df, b, b_date, 2.30))
    except Exception as e:
        logger.err(e)
    return fixed_pct_list


def test_strategy_on_pct(stock_symbol, strategy_code, test_freq):
    '''
    计算策略在某只股票涨幅达到10%，20% 。。。最小/大/平均时间
    1. 需要传入的参数为策略名称
    2. 遍历该股票测试策略买入
    3. 测试结果存入表
    '''
    if strategy_code.startswith('jz_'):
        df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(
            ts_code=stock_symbol).order_by('trade_date').values())
        idx_list = []
        strategy_test_list = []
        if strategy_code.endswith('_b'):
            # 获得所有九转序列买点
            # 循环所有九转序列（时间顺序）
            # 获取当前买点往后所有交易记录（日）
            # 和当前买点比较，
            idx_list = df.loc[df['jiuzhuan_count_b'] == 9].index
            for idx in idx_list:
                b = df.iloc[idx]
                pct_list = get_fixed_pct_list(df, b)
                # 买入点
                # 	ts_code	trade_date	open	high	low	close	pre_close	change	pct_chg	vol	amount
                b_tnx = BStrategyOnFixedPctTest(ts_code=b.ts_code, trade_date=b.trade_date, open=b.open, high=b.high,
                                                low=b.low, close=b.close, pre_close=b.pre_close, change=b.change, pct_chg=b.pct_chg, vol=b.vol,
                                                amount=b.amount, pct10_period=pct_list[
                                                    0], pct20_period=pct_list[1], pct30_period=pct_list[2],
                                                pct50_period=pct_list[3], pct80_period=pct_list[4], pct100_period=pct_list[5],
                                                pct130_period=pct_list[6], test_strategy=TradeStrategy.objects.get(code='jz_b'), test_freq=test_freq)
                strategy_test_list.append(b_tnx)
            BStrategyOnFixedPctTest.objects.bulk_create(strategy_test_list)
