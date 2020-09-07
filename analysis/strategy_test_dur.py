import logging
from datetime import date, datetime

import pandas as pd

from dashboard.utils import days_between
from investors.models import TradeStrategy
from stockmarket.models import StockNameCodeMap

from .models import FocusAreaDuration, StockHistoryDaily
from .utils import has_analysis_task, log_test_status

logger = logging.getLogger(__name__)


def test_duration(strategy_code, ts_code_list=[], freq='D'):
    '''
    计算策略在某只股票涨幅达到10%，20% 。。。最小/大/平均时间
    1. 需要传入的参数为策略名称
    2. 遍历该股票测试策略买入
    3. 测试结果存入表
    '''
    # if strategy_code.startswith('jiuzhuan_'):
    if len(ts_code_list) == 0:
        listed_companies = StockNameCodeMap.objects.filter(
            is_marked_jiuzhuan=True)
    else:
        listed_companies = StockNameCodeMap.objects.filter(
            is_marked_jiuzhuan=True, ts_code__in=ts_code_list)
    for listed_company in listed_companies:
        print(' test on pct start - ' + listed_company.ts_code + ' - ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        df = pd.DataFrame()
        idx_list = []
        strategy_test_list = []
        # if strategy_code.endswith('_b'): not used
        # 获得所有九转序列买点
        # 循环所有九转序列（时间顺序）
        # 获取当前买点往后所有交易记录（日）
        # 和当前买点比较，
        if not has_analysis_task(listed_company.ts_code, 'DURATION_TEST', strategy_code, freq):
            all_pct_list = []
            log_list = []

            if freq == 'D':
                df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(
                    ts_code=listed_company.ts_code).order_by('trade_date').values())
            else:
                pass
            # 根据策略获取标注的关键点index
            if strategy_code in ['dibu_b', 'dingbu_s']:
                idx_list = df.loc[df['is_dingdi_end'] == 1].index
                        
            for idx in idx_list:
                df_row = df.iloc[idx]
                # 顶底点
                # 	ts_code	trade_date	open	high	low	close	pre_close	change	pct_chg	vol	amount
                duration = FocusAreaDuration(ts_code=df_row.ts_code, trade_date=df_row.trade_date, 
                                                vol=df_row.vol, amount=df_row.amount, duration=df_row.dingdi_count, strategy_code=strategy_code, freq=freq)
                strategy_test_list.append(duration)
            if len(strategy_test_list) > 0:
                FocusAreaDuration.objects.bulk_create(strategy_test_list)
                log_test_status(listed_company.ts_code,
                                'DURATION_TEST', freq, [strategy_code])
            print(' test on period end - '  + listed_company.ts_code + ' - ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))        
