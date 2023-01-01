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
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from django.db.models import F
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
# from backtesting.test import SMA
from backtesting.lib import SignalStrategy, TrailingStrategy, resample_apply
from backtesting._stats import compute_drawdown_duration_peaks, geometric_mean
from analysis.models import StockHistory, StockHistoryDaily
from stockmarket.models import StockNameCodeMap
# from backtesting.lib import resample_apply


# def get_data(ts_code, freq='D', sort='asc', adj='qfq'):
#     if freq == 'D':
#         if adj=='qfq':
#             data = StockHistoryDaily.objects.filter(ts_code=ts_code, freq=freq).values(
#                 Close = F('close_qfq'), High = F('high_qfq'), Low = F('low_qfq'), Open = F('open_qfq'), Date = F('trade_date'), Volume = F('vol')).order_by('trade_date' if sort == 'asc' else '-trade_date')
#         else:
#             data = StockHistoryDaily.objects.filter(ts_code=ts_code, freq=freq).values(
#                 Close = F('close'), High = F('high'), Low=F('low'), Open=F('open'), Date=F('trade_date'), Volume=F('vol')).order_by('trade_date' if sort == 'asc' else '-trade_date')
#     else:
#         if adj=='qfq':
#             data = StockHistory.objects.filter(ts_code=ts_code, freq=freq).values(
#                 Close = F('close_qfq'), High = F('high_qfq'), Low = F('low_qfq'), Open = F('open_qfq'), Date = F('trade_date'), Volume = F('vol')).order_by('trade_date' if sort == 'asc' else '-trade_date')
#         else:
#             data = StockHistory.objects.filter(
#                 ts_code=ts_code, freq=freq).values(Close = F('close'), High = F('high'), Low = F('low'), Open = F('open'), Date = F('trade_date'), Volume = F('vol')).order_by('trade_date' if sort == 'asc' else '-trade_date')

#     data_df = pd.DataFrame.from_records(data) 
#     # data_df.rename(columns={'trade_date': 'Date', 'open': 'Open',
#     #                         'high': 'High', 'low': 'Low', 'close': 'Close', 'vol': 'Volume'}, inplace=True)
#     # data_df = data_df.sort_values(by=['Date'],ascending=False)
#     data_df['Date'] = pd.to_datetime(data_df['Date'])
#     data_df = data_df.set_index('Date')
#     return data_df

def get_data(ts_code, freq='D', sort='asc', adj='qfq'):
    return get_data_since(ts_code=ts_code, freq=freq,sort=sort,period=99, adj=adj)


def get_data_since(ts_code, freq='D', sort='asc', period=3, adj='qfq'):
    start_date = None
    if period <= 10:
        start_date = date.today() - timedelta(days=365 * period)

    if start_date is None:
        company = StockNameCodeMap.objects.get(ts_code=ts_code)
        start_date = company.list_date

    dow = start_date.weekday()
    start_date = start_date - timedelta(days=dow)

        # data_df = data_df.loc[start_date:]

    # if start_date is None:
    #     if adj=='qfq':
    #         data = StockHistoryDaily.objects.filter(ts_code=ts_code,).values(
    #             Close = F('close_qfq'), High = F('high_qfq'), Low = F('low_qfq'), Open = F('open_qfq'), Date = F('trade_date'), Volume = F('vol'), PctChg = F('pct_chg')).order_by('trade_date' if sort == 'asc' else '-trade_date')
    #     else:
    #         data = StockHistoryDaily.objects.filter(ts_code=ts_code).values(
    #             Close = F('close'), High = F('high'), Low = F('low'), Open = F('open'), Date = F('trade_date'), Volume = F('vol'), PctChg = F('pct_chg')).order_by('trade_date' if sort == 'asc' else '-trade_date')
    # else:
    if adj=='qfq':
        data = StockHistoryDaily.objects.filter(ts_code=ts_code, trade_date__gte=start_date).values(
            Close = F('close_qfq'), High = F('high_qfq'), Low = F('low_qfq'), Open = F('open_qfq'), Date = F('trade_date'), Volume = F('vol'), PctChg = F('pct_chg')).order_by('trade_date' if sort == 'asc' else '-trade_date')
    else:
        data = StockHistoryDaily.objects.filter(ts_code=ts_code, trade_date__gte=start_date).values(
            Close = F('close'), High = F('high'), Low = F('low'), Open = F('open'), Date = F('trade_date'), Volume = F('vol'), PctChg = F('pct_chg')).order_by('trade_date' if sort == 'asc' else '-trade_date')
    # else:
    #     if start_date is None:
    #         if adj=='qfq':
    #             data = StockHistory.objects.filter(ts_code=ts_code, freq=freq).values(
    #                 Close = F('close_qfq'), High = F('high_qfq'), Low = F('low_qfq'), Open = F('open_qfq'), Date = F('trade_date'), Volume = F('vol'), PctChg = F('pct_chg')).order_by('trade_date' if sort == 'asc' else '-trade_date')
    #         else:
    #             data = StockHistory.objects.filter(
    #                 ts_code=ts_code, freq=freq).values(Close = F('close'), High = F('high'), Low = F('low'), Open = F('open'), Date = F('trade_date'), Volume = F('vol'), PctChg = F('pct_chg')).order_by('trade_date' if sort == 'asc' else '-trade_date')
    #     else:
    #         if adj=='qfq':
    #             data = StockHistory.objects.filter(ts_code=ts_code, freq=freq, trade_date__gte=start_date).values(
    #                 Close = F('close_qfq'), High = F('high_qfq'), Low = F('low_qfq'), Open = F('open_qfq'), Date = F('trade_date'), Volume = F('vol'), PctChg = F('pct_chg')).order_by('trade_date' if sort == 'asc' else '-trade_date')
    #         else:
    #             data = StockHistory.objects.filter(
    #                 ts_code=ts_code, freq=freq, trade_date__gte=start_date).values(Close = F('close'), High = F('high'), Low = F('low'), Open = F('open'), Date = F('trade_date'), Volume = F('vol'), PctChg = F('pct_chg')).order_by('trade_date' if sort == 'asc' else '-trade_date')

    data_df = pd.DataFrame.from_records(data)
    data_df['Date'] = pd.to_datetime(data_df['Date'])
    data_df.set_index('Date', inplace=True)

    # data_df.rename(columns={'trade_date': 'Date', 'open': 'Open',
    #                         'high': 'High', 'low': 'Low', 'close': 'Close', 'vol': 'Volume'}, inplace=True)
    # data_df = data_df.sort_values(by=['Date'],ascending=False)
    if freq in ['W', 'M']:
        data_df = resample(data_df, freq + '-FRI' if freq == 'W' else freq)
    return data_df

def resample(stk_history, freq='W-FRI'):
    if freq == 'W-FRI':
        # 如果第一条交易历史不是从周一开始的，就用NaN补全，为了防止做resample的时候从下周一开始取样导致的周线计算错误
        ohlc_NaN = {
            'Open':stk_history['Open'].iloc[0], 
            'Close': stk_history['Close'].iloc[0], 
            'High': stk_history['High'].iloc[0], 
            'Low': stk_history['Low'].iloc[0], 
            'Volume':stk_history['Volume'].iloc[0], 
            'PctChg': stk_history['PctChg'].iloc[0], 
        }
        dow = stk_history.index[0].weekday()
        for i in range(dow):
            date_idx = stk_history.index[0] - timedelta(days=dow-i)
            df = pd.DataFrame(ohlc_NaN, index=[date_idx])
            stk_history = stk_history.append(df)

        resampled_start = stk_history.resample("W-MON").bfill().ffill()
    if freq == 'M':
        resampled_start = stk_history.resample("BMS").bfill().ffill()

    resampled = stk_history.resample(freq).ffill()
    if resampled_start['Open'].size == resampled['Open'].size:
        resampled['Open'] = resampled_start['Open'].values
    else:
        resampled['Open'] = resampled_start['Open'].values[:resampled_start['Open'].size-1]
    resampled['Volume'] = stk_history.resample(freq)['Volume'].sum()
    resampled['High'] = stk_history.resample(freq)['High'].max().ffill()
    resampled['Low'] = stk_history.resample(freq)['Low'].min().ffill()
    resampled['PctChg'] = round(resampled['Close'].diff() / resampled['Close'], 2)
    
    return resampled.drop_duplicates()


def calibrate_annual_return(s:pd.Series, equity_df: pd.DataFrame, ohlc_data: pd.DataFrame, freq, risk_free_rate: float = 0,):
    assert -1 < risk_free_rate < 1
    
    index = ohlc_data.index
    dd = equity_df['DrawdownPct']

    gmean_day_return: float = 0
    day_returns = np.array(np.nan)
    annual_trading_days = np.nan
    if isinstance(index, pd.DatetimeIndex):
        day_returns = equity_df['Equity'].resample('D').last().dropna().pct_change()
        gmean_day_return = geometric_mean(day_returns)
        annual_trading_days = float(
            52 if freq=='W' else
            12)

     # Annualized return and risk metrics are computed based on the (mostly correct)
    # assumption that the returns are compounded. See: https://dx.doi.org/10.2139/ssrn.3054517
    # Our annualized return matches `empyrical.annual_return(day_returns)` whereas
    # our risk doesn't; they use the simpler approach below.
    annualized_return = (1 + gmean_day_return)**annual_trading_days - 1
    s.loc['Return (Ann.) [%]'] = annualized_return * 100
    s.loc['Volatility (Ann.) [%]'] = np.sqrt((day_returns.var(ddof=int(bool(day_returns.shape))) + (1 + gmean_day_return)**2)**annual_trading_days - (1 + gmean_day_return)**(2*annual_trading_days)) * 100  # noqa: E501
    # s.loc['Return (Ann.) [%]'] = gmean_day_return * annual_trading_days * 100
    # s.loc['Risk (Ann.) [%]'] = day_returns.std(ddof=1) * np.sqrt(annual_trading_days) * 100

    # Our Sharpe mismatches `empyrical.sharpe_ratio()` because they use arithmetic mean return
    # and simple standard deviation
    s.loc['Sharpe Ratio'] = np.clip((s.loc['Return (Ann.) [%]'] - risk_free_rate) / (s.loc['Volatility (Ann.) [%]'] or np.nan), 0, np.inf)  # noqa: E501
    # Our Sortino mismatches `empyrical.sortino_ratio()` because they use arithmetic mean return
    s.loc['Sortino Ratio'] = np.clip((annualized_return - risk_free_rate) / (np.sqrt(np.mean(day_returns.clip(-np.inf, 0)**2)) * np.sqrt(annual_trading_days)), 0, np.inf)  # noqa: E501
    max_dd = -np.nan_to_num(dd.max())
    s.loc['Calmar Ratio'] = np.clip(annualized_return / (-max_dd or np.nan), 0, np.inf)
    


def BBI(close_df):
    try:
        df_ma = pd.DataFrame()
        df_ma['ma_3'] = talib.MA(close_df, timeperiod=3)
        df_ma['ma_6'] = talib.MA(close_df, timeperiod=6)
        df_ma['ma_12'] = talib.MA(close_df, timeperiod=12)
        df_ma['ma_24'] = talib.MA(close_df, timeperiod=24)

        df_bbi = pd.DataFrame()
        df_bbi['bbi'] = (df_ma['ma_3'] + df_ma['ma_6'] +
                         df_ma['ma_12']+df_ma['ma_24'])/4
        return df_bbi
    except Exception as err:
        print(err)


def get_ta_indicator(name):
    if name == 'SMA':
        return talib.SMA
    if name == 'EMA':
        return talib.EMA
    if name == 'RSI':
        return talib.RSI
    if name == 'KDJ':
        return talib.STOCH
    if name == 'MACD':
        return talib.MACD
    if name == 'BOLL':
        return talib.BBANDS
    if name == 'BBI':
        return BBI


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
        b = crossover(self.indic_series1, self.indic_series2)
        s = crossover(self.indic_series2, self.indic_series1)
        if b:
            # self.position.close()
            self.buy()
        elif s:
            self.position.close()
            # self.sell()


DEBUG = True


class System(SignalStrategy, TrailingStrategy):
    # {'SMA_10': 10,'SMA_20':20,'RSI_20':20}
    # SMA_10 = None
    # SMA_20 = None
    ta_type_a = ['SMA', 'EMA', 'RSI']
    ta_type_b = ['KDJ', 'MACD', 'BOLL']
    ta_type_c = ['BBI']

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
        super().init()
        # Compute moving averages the strategy demands
        for k, v in self.ta_indicator_dict.items():
            # 需要重构一下
            if k.split('_')[0] in self.ta_type_a:  # SMA, EMA, RSI
                setattr(self, k, self.I(get_ta_indicator(
                    k.split('_')[0]), self.data.Close, v))

            if k.split('_')[0] in self.ta_type_b:  # KDJ, MACD, BOLL
                # KDJ
                if k.split('_')[0] == 'KDJ':
                    setattr(self, k, self.I(get_ta_indicator(k.split('_')[0]), self.data.High,
                                            self.data.Low,
                                            self.data.Close,
                                            fastk_period=9,
                                            slowk_period=3,
                                            slowk_matype=0,
                                            slowd_period=3,
                                            slowd_matype=0,
                                            ))
                    setattr(self, k+'_K', getattr(self, k)[0])
                    setattr(self, k+'_D', getattr(self, k)[1])
                    setattr(self, k+'_J',
                            list(map(lambda x, y: 3*x-2*y, getattr(self, k)[0], getattr(self, k)[1])))

                    # setattr(self, k, talib.STOCH(self.data.High,
                    #                             self.data.Low,
                    #                             self.data.Close,
                    #                             fastk_period=9,
                    #                             slowk_period=3,
                    #                             slowk_matype=0,
                    #                             slowd_period=3,
                    #                             slowd_matype=0))
                    # setattr(self, k+'_K', getattr(self, k)[0])
                    # setattr(self, k+'_D', getattr(self, k)[1])
                    # setattr(self, k+'_J',
                    #         list(map(lambda x, y: 3*x-2*y, getattr(self, k)[0], getattr(self, k)[1])))

                # MACD
                if k.split('_')[0] == 'MACD':
                    setattr(self, k, self.I(get_ta_indicator(k.split('_')[0]),
                                            self.data.Close, fastperiod=12, slowperiod=26, signalperiod=9))
                    setattr(self, k+'_DIFF', getattr(self, k)[0])
                    setattr(self, k+'_DEA', getattr(self, k)[1])
                    setattr(self, k+'_MACD', getattr(self, k)[2])

                    # setattr(self, k, talib.MACD(
                    #     self.data.Close, fastperiod=12, slowperiod=26, signalperiod=9))
                    # setattr(self, k+'_DIFF', getattr(self, k)[0])
                    # setattr(self, k+'_DEA', getattr(self, k)[1])
                    # setattr(self, k+'_MACD', getattr(self, k)[2])

                # BOLL
                # upper,middle,lower=talib.BBANDS(closed, matype=talib.MA_Type.T3)
                if k.split('_')[0] == 'BOLL':
                    setattr(self, k, self.I(get_ta_indicator(k.split('_')[0]),
                                            self.data.Close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0))
                    setattr(self, k+'_UPPER', getattr(self, k)[0])
                    setattr(self, k+'_MID', getattr(self, k)[1])
                    setattr(self, k+'_LOWER', getattr(self, k)[2])

            if k.split('_')[0] in self.ta_type_c:  # BBI
                setattr(self, k, self.I(get_ta_indicator(
                    k.split('_')[0]), self.data.Close))
        
        if float(self.stoploss) > 1.0:
            self.set_trailing_sl(int(self.stoploss))

    def next(self):
        # super().next()

        price = self.data.Close[-1]

        # b = crossover(getattr(self, 'SMA_10'), getattr(self, 'SMA_20'))
        for k, v in self.buy_cond_dict['condition'].items():
            for kk, vv in self.buy_cond_dict['condition'][k].items():
                # crossover(getattr(self, vv.split(',')[0]), getattr(self, vv.split(',')[1]))
                self._long_order = eval(vv)

                # if k == 'crossover':
                #     self._long_order = eval(vv) #crossover(getattr(self, vv.split(',')[0]), getattr(self, vv.split(',')[1]))
                # if k == 'pair_comp':
                #     self._long_order = crossover(getattr(self, vv.split(',')[0]), getattr(self, vv.split(',')[1]))
                # if k == 'threshold':
                #     self._long_order = crossover(getattr(self, vv.split(',')[0]), getattr(self, vv.split(',')[1]))

        # s = crossover(getattr(self, 'SMA_20'), getattr(self, 'SMA_10'))
        for k, v in self.sell_cond_dict['condition'].items():
            for kk, vv in self.sell_cond_dict['condition'][k].items():
                # crossover(getattr(self, vv.split(',')[0]), getattr(self, vv.split(',')[1])) #eval(vv)
                self._short_order = eval(vv)
        
        if self._long_order:
            if not self.position:
                if float(self.stoploss) > 0.0 and float(self.stoploss) < 1.0:
                    self.buy(sl=float(self.stoploss) * price)
                else:
                    self.buy()
        elif self._short_order:
            if self.position:
                self.position.close()


class SimpleSignalStrategy(SignalStrategy, TrailingStrategy):
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
