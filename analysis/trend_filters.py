'''
results = StrategyTestLowHigh.objects.filter(
                strategy_code=strategy, ts_code=ts_code, test_period=test_period).order_by('trade_date')
1. 获得回测关键点的trade_date (make it index?)
2. 根据filter类型，大盘 or 个股 (创建大盘历史数据表 - done)
3. 根据输入的过滤条件创建filter
4. 对dataframe进行过滤(在low high, expected pct加字段：vol，amount，ma25，ma60，ma200 - )
    譬如：df[df['ma25_slope']>0],df[df['ma60_slope']>0],df[df['ma200_slope']>0],df[df['vol']>?]
5. 得到过滤后的trade_date
6. 使用第5步中的trade_date过滤low high或者expected pct
'''
import pandas as pd
from analysis.models import StockIndexHistory,StrategyTestLowHigh, BStrategyOnFixedPctTest
from .utils import get_market_code

def build_condition(filter_params=[]):
    # column = cond_list[0] #['vol', 'ma25_slope', 'ma60_slope']
    # ops = cond_list[1] #['>', '>', '<']
    # condition = cond_list[2] # [4, 0, '0']
    c = ' & '.join(filter_params)
    return c 
 
def pct_on_period_filter(ts_code, trade_date_list, filter_params=[]):
    '''
    filter_param_list = {'ma25':'1','ma60':'0','ma200':'1','vol':'25670'}
    指数
    index   trade_date  ma25_slope  ma60_slope  ma200_slope vol
    0       20200101    0.23        0.1         -0.123      234244
    1       20200219    0.23        0.1         -0.123      234244
    
    个股
    index   trade_date  ma25_slope  ma60_slope  ma200_slope vol
    0       20200101    0.23        0.1         -0.123      234244
    1       20200219    0.23        0.1         -0.123      234244

    e.g.
    limits_dic = {"A" : 0, "B" : 2, "C" : 0}
    query = ' & '.join(['{}>{}'.format(k, v) for k, v in limits_dic.items()])
    temp = df.query(query)
    temp

    e.g 2
    df = pd.DataFrame({'gender':list('MMMFFF'),
                   'height':[4,5,4,5,5,4],
                   'age':[70,80,90,40,2,3]})
    df

    column = ['height', 'age', 'gender']
    equal = ['>', '>', '==']
    condition = [4, 20, 'M']

    query = ' & '.join(f'{i} {j} {repr(k)}' for i, j, k in zip(column, equal, condition))
    df.query(query)

    idx1 = pd.Index([1, 2, 3, 4])
    idx2 = pd.Index([3, 4, 5, 6])
    idx1.intersection(idx2)

    {'I': }
    '''
    df_index = None
    df_stock = None
    for key in filter_params:
        if key == 'I':
            if len(filter_params[key]) > 0:
                results = StockIndexHistory.objects.filter(ts_code=get_market_code(ts_code), trade_date__in=trade_date_list).order_by('trade_date')
                df = pd.DataFrame(results.values('trade_date','ma25_slope','ma60_slope','ma200_slope','vol','amount'))
                if df is not None and len(df) > 0:
                    query = build_condition(filter_params[key])
                    df_index = df.query(query)

        if key == 'E':
            if len(filter_params[key]) > 0:
                results = StrategyTestLowHigh.objects.filter(ts_code=ts_code, trade_date__in=trade_date_list).order_by('trade_date')
                df = pd.DataFrame(results.values(
                    'trade_date', 'ma25_slope', 'ma60_slope', 'ma200_slope', 'vol', 'amount'))
                if df is not None and len(df) > 0:
                    query = build_condition(filter_params[key])
                    df_stock = df.query(query)
    
    if df_index is not None and df_stock is not None:
        return list(set(df_index['trade_date']).intersection(set(df_stock['trade_date'])))
    else:
        return df_index['trade_date'].tolist() if df_index is not None else df_stock['trade_date'].tolist()

def period_on_pct_filter(trade_date_list, filter_params=[]):
    df_index = None
    df_stock = None
    for key in filter_params:
        if key == 'I':
            results = StockIndexHistory.objects.filter(trade_date__in=trade_date_list).order_by('trade_date')
            df = pd.DataFrame(results)
            if df is not None and len(df) > 0:
                query = build_condition(filter_params[key])
                df_index = df.query(query)

        if key == 'E':
            results = BStrategyOnFixedPctTest.objects.filter(trade_date__in=trade_date_list).order_by('trade_date')
            df = pd.DataFrame(results)
            if df is not None and len(df) > 0:
                query = build_condition(filter_params[key])
                df_stock = df.query(query) 
    
    return list(set(df_index['trade_date']).intersection(set(df_stock['trade_date'])))
