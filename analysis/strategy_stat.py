import pandas as pd

from .models import StrategyOnDaysTest, StrategyOnPctTest, StockHistoryDaily, TradeStrategyStat

def calc_strategy_on_days(stock_symbol, strategy_name='jz', test_period=20):
    '''
    计算策略在某只股票上在某个时间周期上的最小/大，和平均涨跌幅值的统计
    1. 需要传入的参数为策略名称
    2. 遍历该股票测试策略买入或则卖出点记录
    3. 根据测试周期获取从买入点或者卖出点开始最大/小，平均涨跌幅
    4. 测试结果存入表
    '''
    if strategy_name == 'jz':
        df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=stock_symbol).values())
    
    pass


def calc_strategy_on_pct():
    pass
