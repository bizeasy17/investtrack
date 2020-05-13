import pandas as pd

from .models import StockHistoryDaily, TradeStrategyStat, BStrategyTestResultOnDays


def calc_strategy_on_days(stock_symbol, test_period, strategy_name='jz'):
    '''
    计算策略在某只股票上在某个时间周期上的最小/大，和平均涨跌幅值的统计
    1. 需要传入的参数为策略名称
    2. 遍历该股票测试策略买入或则卖出点记录
    3. 根据测试周期获取从买入点或者卖出点开始最大/小，平均涨跌幅
    4. 测试结果存入表
    '''
    if strategy_name.startswith('jz_'):
        df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=stock_symbol).order_by('trade_date').values())
        idx_list = []
        idx_list_period = []
        strategy_test_list = []
        if strategy_name.endswith('_b'):
            idx_list = df.loc[df['jiuzhuan_b'] == 9].index
            for idx in idx_list:
                idx_list_period = [id in range(idx, idx + test_period)]
                b = df[idx]['close']
                df_max = df.iloc[idx_list_period]['close'].idxmax(axis=0)
                df_min = df.iloc[idx_list_period]['close'].idxmin(axis=0)
                max_c = df.iloc[idx_list_period]['close'].max(axis=0)
                min_c = df.iloc[idx_list_period]['close'].min(axis=0)
                pct_incr = round((max_c - b) / b, 2)
                pct_drop = round((min_c - b) / b, 2)
                # 买入点
                for v in b.values:
                    # 	ts_code	trade_date	open	high	low	close	pre_close	change	pct_chg	vol	amount
                    b_tnx = BStrategyTestResultOnDays(ts_code = v[0], trade_date=v[1], open=v[2], high=v[3],
                        low=v[4], close=v[5], pre_close=v[6], change=v[7], pct_chg=v[8], vol=v[9],
                        amount=v[10], tnx_point=True, test_strategy='jz_b')
                # 查询周期内最高价
                for v in df_max.values:
                    # 	ts_code	trade_date	open	high	low	close	pre_close	change	pct_chg	vol	amount
                    test_max = BStrategyTestResultOnDays(ts_code = v[0], trade_date=v[1], open=v[2], high=v[3],
                        low=v[4], close=v[5], pre_close=v[6], change=v[7], pct_chg=v[8], vol=v[9],
                        amount=v[10], stage_high=True, stage_high_pct=pct_incr, test_strategy='jz_b')
                # 查询周期内最低价
                for v in df_min.values:
                    test_min = BStrategyTestResultOnDays(ts_code = v[0], trade_date=v[1], open=v[2], high=v[3],
                        low=v[4], close=v[5], pre_close=v[6], change=v[7], pct_chg=v[8], vol=v[9],
                        amount=v[10], stage_low=True, stage_low_pct=pct_drop, test_strategy='jz_b')
                strategy_test_list.append(b_tnx)
                strategy_test_list.append(test_min)
                strategy_test_list.append(test_max)
            BStrategyTestResultOnDays.objects.bulk_create(strategy_test_list)
        else:
            idx_list = df.loc[df['jiuzhuan_s'] == 9]

        # idx = df.loc[df['close'] > 16.66].index
        # df.iloc[idx]
    pass


def calc_strategy_on_pct():
    pass
