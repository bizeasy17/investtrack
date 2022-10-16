'''
可选的技术指标 - TA-lib 支持的SMA, EMA etc

内置的策略
    1. 上穿下穿
    2. 均线反转（斜率）
    3. 指标quantile高位低位
    4. 

止损策略 - TrailingStrategy
'''
import talib
import pandas as pd

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
# from backtesting.test import SMA
from backtesting.lib import SignalStrategy, TrailingStrategy,resample_apply

from analysis.models import StockHistory, StockHistoryDaily
# from backtesting.lib import resample_apply


def get_data(ts_code, freq='D'):
    if freq == 'D':
        data = StockHistoryDaily.objects.filter(ts_code=ts_code, freq=freq).values(
            'close', 'high', 'low', 'open', 'trade_date', 'vol').order_by('-trade_date')
    else:
        data = StockHistory.objects.filter(
            ts_code=ts_code, freq=freq).values('close', 'high', 'low', 'open', 'trade_date', 'vol').order_by('-trade_date')

    data_df = pd.DataFrame.from_records(data)
    data_df.rename(columns={'trade_date': 'Date', 'open': 'Open',
                    'high': 'High', 'low': 'Low', 'close': 'Close', 'vol': 'Volume'}, inplace=True)
    # data_df = data_df.sort_values(by=['Date'],ascending=False)
    data_df = data_df.set_index('Date')
    return data_df

def get_ta_indicator(name):
    if name == 'SMA':
        return talib.SMA
    if name == 'EMA':
        return talib.EMA
    if name == 'RSI':
        return talib.RSI

def get_strategy_by_category(category):
    if category == 'simple_crossover':
        return SimpleCrossoverStrategy
    if category == 'system':
        return System
    if category == 'signal':
        return SignalStrategy

class SimpleCrossoverStrategy(Strategy):
    # defalt TECH indicator param
    ta_func = talib.SMA

    n1 = 5
    n2 = 10

    indic_series1 = pd.Series([])
    indic_series2 = pd.Series([])

    # indic = ''
    # buy_cond1 = ''
    # buy_cond2 = ''
    # buy_cond3 = ''
    # buy_cond4 = ''
    # buy_cond5 = ''
    # buy_cond6 = ''
    # buy_cond7 = ''
    # buy_cond8 = ''
    # buy_cond9 = ''
    # buy_cond10 = ''
    
    # sell_cond1 = ''
    # sell_cond2 = ''
    # sell_cond3 = ''
    # sell_cond4 = ''
    # sell_cond5 = ''
    # sell_cond6 = ''
    # sell_cond7 = ''
    # sell_cond8 = ''
    # sell_cond9 = ''
    # sell_cond10 = ''

    # func is a function that returns the indicator array(s) of same length as Strategy.data
    
    def init(self):
        # super.init()
        self.indic_series1 = self.I(self.ta_func, self.data.Close, self.n1)
        self.indic_series2 = self.I(self.ta_func, self.data.Close, self.n2)

        # close = self.data.Close
        # indic_name = func.__name__
        
        # # Compute moving averages the strategy demands
        # if len(kwargs) >= 1:
        #     for k,v in kwargs.items():
        #         setattr(self, indic_name+k, self.I(func, close, v))
        #         # setattr(self, indic+'2', self.I(func, close, kwargs['indic2']))   
        # else:
        #     self.indic10 = self.I(func, close, self.param10)
        #     self.indic25 = self.I(func, close, self.param25)

    def next(self):
        if crossover(self.indic_series1, self.indic_series2):
            self.position.close()
            self.buy()
        elif crossover(self.indic_series2, self.indic_series1):
            self.position.close()
            self.sell()


class System(Strategy):
    # {'SMA_10': 10,'SMA_20':20,'RSI_20':20}
    ta_indicator_dict = {}
    '''
    e.g. self.daily_rsi[-1] > self.level and
            self.weekly_rsi[-1] > self.level and
            self.weekly_rsi[-1] > self.daily_rsi[-1] and
            self.ma10[-1] > self.ma20[-1] > self.ma50[-1] > self.ma100[-1] and
            price > self.ma10[-1]
        需要判断是否有这个类属性?
        给属性赋值
        setattr(System, )
        getattr(System, self.SMA_10) > getattr(System, 'level')
    condition的类型
    [x] 1. 某个指标高于或者低于某个阈值 threshold - e.g. RSI(10) > 45, VOL > 10,000
    [x] 2. 某个指标的不同参数上穿或者下穿 cross - e.g. cross(a(10), a(20))
    [x] 3. 某个指标的不同参数之间的比较 pc (pair compare) - e.g. a(10) > a(20), a(20) > a(30)
    [ ] 4. 某个指标出现signal, 譬如买或者卖? signal - e.g. crossover, 
    {
        'attr':{'sma_level':'10','rsi_level':'20'},
        'condition':{
            'threshold':{'RSI_20':'RSI_20>30'},
            'crossover':{'a10':'cross(a(10), a(20))'},
            'pair_comp': {'a10':'a(10) > a(20)'},
        }
    }
    '''
    _long_order = False
    buy_cond_dict = {}
    # {'attr':{'sma_level':'eq:10','rsi_level':'lte:20'},'condition':{}}
    '''
    {
        'attr':{'sma_level':'90','rsi_level':'20'},
        'condition':{
            'threshold':{'RSI_20':'RSI_20>90'},
            'crossover':{'a10':'cross(a(20), a(10))'},
            'pair_comp': {'a10':'a(20) > a(10)'},
        }
    }
    '''
    _short_order = False
    sell_cond_dict = {}
    # 只能存在一次的crossover条件
    _crossover_cond = None

    stoploss = None
    # stoploss = .92
    
    def init(self):
        # Compute moving averages the strategy demands
        for k,v in self.ta_indicator_dict.items():
            setattr(System, k, self.I(get_ta_indicator(k.split('_')[0]), self.data.Close, v))
        
        for k,v in self.buy_cond_dict['attr'].items():
            setattr(System, k, v)

        for k,v in self.sell_cond_dict['attr'].items():
            setattr(System, k, v)

        # Compute daily RSI(30)
        # self.daily_rsi = self.I(RSI, self.data.Close, self.d_rsi)
        
        # To construct weekly RSI, we can use `resample_apply()`
        # helper function from the library
        # self.weekly_rsi = resample_apply(
        #     'W-FRI', RSI, self.data.Close, self.w_rsi)
        
        
    def next(self):
        price = self.data.Close[-1]
        # 判断属性是否存在？
        for k,v in self.buy_cond_dict['condition'].items():
            for kk,vv in self.buy_cond_dict['condition'][k].items():
                self._long_order = eval(vv)
            # sign = v.split(':')[0]
            # threshhold = v.split(':')[1]
            # if k == 'threshold':
            #     for kk,vv in self.buy_cond_dict['condition'][k].items():
            #         self.long_order = eval(vv)
            # if k == 'cross':
            #     for kk,vv in self.buy_cond_dict['condition'][k].items():
            #         self.crossover_cond = eval(vv)
            # if k == 'pair_comp':
            #     for kk,vv in self.buy_cond_dict['condition'][k].items():
            #         self.long_order = eval(vv)
        
            # if sign == 'gt':
            #     self.long_order = eval('getattr(System, k)' + sign + 'threshhold')
            # if sign == 'gte':
            #     self.long_order = getattr(System, k) >= threshhold
            # if sign == 'lt':
            #     self.long_order = getattr(System, k) < threshhold
            # if sign == 'lte':
            #     self.long_order = getattr(System, k) <= threshhold
            # if sign == 'eq':
            #     self.long_order = getattr(System, k) == threshhold

        for k,v in self.sell_cond_dict['condition'].items():
            for kk,vv in self.sell_cond_dict['condition'][k].items():
                self.short_order = eval(vv)
            # sign = v.split(':')[0]
            # threshhold = v.split(':')[1]
            # if sign == 'gt':
            #     self.short_order = getattr(System, k) > threshhold
            # if sign == 'gte':
            #     self.short_order = getattr(System, k) >= threshhold
            # if sign == 'lt':
            #     self.short_order = getattr(System, k) < threshhold
            # if sign == 'lte':
            #     self.short_order = getattr(System, k) <= threshhold
            # if sign == 'eq':
            #     self.short_order = getattr(System, k) == threshhold

        # If we don't already have a position, and
        # if all conditions are satisfied, enter long.
        if self._long_order and not self.position:
            if self.stoploss:
                self.buy(sl=float(self.stoploss) * price)
            else:
                self.buy()
        
        # if self.crossover_cond:
        #     if self.stoploss:
        #         self.buy(sl=self.stoploss * price)
        #     else:
        #         self.buy()

        # If the price closes 2% or more below 10-day MA
        # close the position, if any.
        elif self.short_order:
            self.position.close()


class SignalStrategy(SignalStrategy, TrailingStrategy):
    n1 = 10
    n2 = 25
    
    def init(self):
        # In init() and in next() it is important to call the
        # super method to properly initialize the parent classes
        super().init()
        
        # Precompute the two moving averages
        ema1 = self.I(talib.EMA, self.data.Close, self.n1)
        ema2 = self.I(talib.EMA, self.data.Close, self.n2)
        
        # Where sma1 crosses sma2 upwards. Diff gives us [-1,0, *1*]
        signal = (pd.Series(ema1) > ema2).astype(int).diff().fillna(0)
        signal = signal.replace(-1, 0)  # Upwards/long only
        
        # Use 95% of available liquidity (at the time) on each order.
        # (Leaving a value of 1. would instead buy a single share.)
        entry_size = signal * .95
                
        # Set order entry sizes using the method provided by 
        # `SignalStrategy`. See the docs.
        self.set_signal(entry_size=entry_size)
        
        # Set trailing stop-loss to 2x ATR using
        # the method provided by `TrailingStrategy`
        self.set_trailing_sl(2)


# bt = Backtest(stock_hist, SmaCross,
#               cash=10000, commission=.002,
#               exclusive_orders=True)

# output = bt.run()
# bt.plot()
