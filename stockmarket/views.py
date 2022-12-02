
import logging
import re
from datetime import date, datetime, timedelta
from mimetypes import init
from multiprocessing.resource_sharer import stop
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
# from backtesting.test import SMA
from backtesting.lib import SignalStrategy, TrailingStrategy
import json
import numpy as np
import pandas as pd
from pandas import Timedelta
import tushare as ts
import talib as ta
from analysis.models import (AnalysisDateSeq, IndustryBasicQuantileStat, StockHistory,
                             StockHistoryDaily, StockHistoryIndicators, StockIndexHistory)
from analysis.utils import get_ip
from django.views.generic import TemplateView
from django.contrib.auth.models import AnonymousUser
from django.db.models import Count, Q
from django.http import (Http404, HttpResponse, HttpResponseServerError,
                         JsonResponse)
from django.shortcuts import render
from numpy.lib.function_base import append
from rest_framework.response import Response
from rest_framework.views import APIView
from search.utils import pinyin_abbrev
from users.models import UserActionTrace, UserBackTestTrace, UserQueryTrace
from stockmarket.backtesting import get_data, get_data_since, get_ta_indicator, get_strategy_by_category
from stockmarket.models import (City, CompanyBasic, Industry, Province,
                                StockNameCodeMap)

from .models import (CompanyBasic, CompanyDailyBasic, CompanyFinIndicators, CompanyTop10FloatHoldersStat, IndexDailyBasic, Industry, ManagerRewards,
                     StockNameCodeMap)
from .serializers import (CompanyDailyBasicSerializer, CompanySerializer, CompanyTop10HoldersStatSerializer, Equity, EquitySerializer, IndexDailyBasicSerializer,
                          IndustryBasicQuantileSerializer, IndustrySerializer, OHLCSerializer,
                          StockCloseHistorySerializer, CitySerializer, ProvinceSerializer, StockHistoryOHLC, StockIndicRSVSerializer)
from .utils import collect_top10_holders, get_ind_basic, process_min_max, str_eval, collect_fin_indicators, pop_dailybasic_to_finindicator

# Create your views here.

logger = logging.getLogger(__name__)

index_list = ['000001.SH', '399001.SZ', '399006.SZ']


class BTView(TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'toolset/backtesting.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'huice'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        # if req_user is not None:
        #     pass
        # else:
        #     pass
        return render(request, self.template_name)


class CrossoverBacktestingList(APIView):
    def get(self, request, ts_code, tech_indicator, indicator_param, strategy_category, cash=10-000, commission=0.1, leverage=1, freq='D'):
        '''
        tech_indicator: SMA, EMA, BOLL, STOCH, KDJ, etc
        indicator_param: SMA,5,10,20,60,120,250 or EMA,5,10,20,60,120,250 or STOCH,10,25
        strategy: cross, crossover, 
        trailing_strategy: 2 * ATR
        capital: 10,000
        commission: 0.05
        leverage: 0.02 mean 50 leverage
        '''
        data_df = get_data(ts_code, freq)

        # {'SMA_10': 10,'SMA_20':20,'RSI_20':20} or SMA
        # if type(eval(tech_indicator)) == str:
        ta_func = get_ta_indicator(tech_indicator)
        # if type(eval(tech_indicator)) == str:
        #     ta_func = eval(tech_indicator)
        # strategy_param = {}
        '''
        indicator_param - indic10:10,indic20:20,buy: indic10 xover indic20,sell: indic20 xover indic10,
        indicator params example
        输入序列，{'indic5':SMA(close,5)}, {'indic5':EMA(close,5)}
        next condition example:
        b: indic10 xover indic20, or indic10.level < 10
        s: indic20 xover indic10, or indic10.level > 90
        '''

        # param_list = indicator_param.split(',')
        # for p in param_list:
        #     if p.split(':')[0][:5] == 'indic':
        #         strategy_param[p.split(':')[0]] = ta_func(
        #             data_df['Close'].values, int(p.split(':')[1]))
        #     else:
        #         strategy_param[p.split(':')[0]] = p.split(':')[1]

        # TranStrategy = type(
        #     'TranStrategy',
        #     Strategy,
        #     {
        #         ''
        #         'init': init,
        #         'next': next
        #     })
        backtesting = Backtest(data_df, get_strategy_by_category(strategy_category), cash=float(cash), commission=float(commission), margin=float(leverage), trade_on_close=False,
                               hedging=False, exclusive_orders=False)

        if strategy_category == 'simple_crossover':
            bt_results = backtesting.run(ta_func=ta_func, n1=int(
                indicator_param.split(',')[0]), n2=int(indicator_param.split(',')[1]))

        # backtesting.plot()

        print('equity')
        equity = bt_results.loc['_equity_curve']
        print(equity)
        print('trades')
        trades = bt_results.loc['_trades']
        print(trades)


class SystemBacktestingList(APIView):
    # http://127.0.0.1:8000/stockmarket/bt-system/000001.SZ/system/
    #   %7B'SMA_10':%2010,'SMA_20':20,'RSI_20':20%7D/%7B'attr':%7B'sma_level':'10','rsi_level':'20'%7D,'condition':%7B'threshold':%7B'RSI_20':'RSI_20%3E30'%7D,'crossover':%7B'a10':'cross(a(10),%20a(20))'%7D,'pair_comp':%20%7B'a10':'a(10)%20%3E%20a(20)'%7D%7D%7D/%
    #   7B'attr':%7B'sma_level':'10','rsi_level':'90'%7D,'condition':%7B'threshold':%7B'RSI_20':'RSI_20%3E90'%7D,'crossover':%7B'a20':'cross(a(20),%20a(10))'%7D,'pair_comp':%20%7B'a10':'a(20)%20%3E%20a(10)'%7D%7D%7D/.95/10000/.001/1/D/
    def get(self, request, ts_code, strategy_category, ta_indicator_dict, buy_cond_dict, sell_cond_dict, stoploss=.98, cash=10-000, commission=.001, leverage=1, trade_on_close=False, freq='D'):
        '''
        tech_indicator: SMA, EMA, BOLL, STOCH, KDJ, etc
        indicator_param: SMA,5,10,20,60,120,250 or EMA,5,10,20,60,120,250 or STOCH,10,25
        strategy: cross, crossover, 
        trailing_strategy: 2 * ATR
        capital: 10,000
        commission: 0.05
        leverage: 0.02 mean 50 leverage
        '''
        data_df = get_data(ts_code, freq, 'desc')

        # {'SMA_10': 10,'SMA_20':20,'RSI_20':20} or SMA
        if type(eval(ta_indicator_dict)) == dict:
            ta_indicator_dict = eval(ta_indicator_dict)
        else:
            raise TypeError('技术指标应为dict类型')

        if type(eval(buy_cond_dict)) == dict:
            buy_cond_dict = eval(buy_cond_dict)
        else:
            raise TypeError('买入条件应为dict类型')

        if type(eval(sell_cond_dict)) == dict:
            sell_cond_dict = eval(sell_cond_dict)
        else:
            raise TypeError('卖出条件应为dict类型')
        # strategy_param = {}
        '''
        indicator_param - indic10:10,indic20:20,buy: indic10 xover indic20,sell: indic20 xover indic10,
        indicator params example
        输入序列，{'indic5':SMA(close,5)}, {'indic5':EMA(close,5)}
        next condition example:
        b: indic10 xover indic20, or indic10.level < 10
        s: indic20 xover indic10, or indic10.level > 90
        '''
        try:
            backtesting = Backtest(data_df, get_strategy_by_category(strategy_category), cash=float(cash), commission=float(commission), margin=float(leverage),
                                   trade_on_close=True if trade_on_close == 1 else False,
                                   hedging=False, exclusive_orders=False)

            if strategy_category == 'system':
                bt_results = backtesting.run(ta_indicator_dict=ta_indicator_dict, buy_cond_dict=buy_cond_dict,
                                             sell_cond_dict=sell_cond_dict, stoploss=stoploss)

            # print('strategy')
            # print(bt_results.loc['_strategy'])
            # print('equity')
            eq_list = []
            equity = bt_results.loc['_equity_curve']
            trades = bt_results.loc['_trades']

            trades_entry = trades[[
                'EntryBar', 'EntryPrice', 'EntryTime', 'Duration', 'PnL']]
            trades_entry = trades_entry.set_index('EntryTime')

            trades_exit = trades[['ExitBar', 'ExitPrice', 'ExitTime']]
            trades_exit = trades_exit.set_index('ExitTime')

            equity = pd.concat([equity, trades_entry], axis=1)
            equity = pd.concat([equity, trades_exit], axis=1)

            for index, row in equity.iterrows():
                q = Equity(date=index, equity=row['Equity']/float(cash), drawdownpct=row['DrawdownPct'],
                           drawdownduration=row['DrawdownDuration'] if not row['DrawdownDuration'] is pd.NaT else None,
                           entry_price=row['EntryPrice'], exit_price=row['ExitPrice'], pnl=row['PnL'], duration=row['Duration'])

                if not np.isnan(row['EntryPrice']):
                    q.direction = 'b'
                if not np.isnan(row['ExitPrice']):
                    q.direction = 's'
                if not np.isnan(row['EntryPrice']) and not np.isnan(row['ExitPrice']):
                    q.direction = 'b&s'
                # q.direction = None

                eq_list.append(q)

            # print(equity)
            # print('trades')
            # print(trades)
            serializer = EquitySerializer(eq_list, many=True)
            # backtesting.plot()

            return Response(serializer.data)
        except Equity.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


def get_bt_result(request, ts_code, strategy_category, ta_indicator_dict, buy_cond_dict, sell_cond_dict, stoploss=.98, cash=10-000, commission=.001, leverage=1, trade_on_close=False, freq='D'):
    '''
    tech_indicator: SMA, EMA, BOLL, STOCH, KDJ, etc
    indicator_param: SMA,5,10,20,60,120,250 or EMA,5,10,20,60,120,250 or STOCH,10,25
    strategy: cross, crossover, 
    trailing_strategy: 2 * ATR
    capital: 10,000
    commission: 0.05
    leverage: 0.02 mean 50 leverage
    '''
    data_df = get_data(ts_code, freq, 'desc')

    # {'SMA_10': 10,'SMA_20':20,'RSI_20':20} or SMA
    if type(eval(ta_indicator_dict)) == dict:
        ta_indicator_dict = eval(ta_indicator_dict)
    else:
        raise TypeError('技术指标应为dict类型')

    if type(eval(buy_cond_dict)) == dict:
        buy_cond_dict = eval(buy_cond_dict)
    else:
        raise TypeError('买入条件应为dict类型')

    if type(eval(sell_cond_dict)) == dict:
        sell_cond_dict = eval(sell_cond_dict)
    else:
        raise TypeError('卖出条件应为dict类型')
    # strategy_param = {}
    '''
        indicator_param - indic10:10,indic20:20,buy: indic10 xover indic20,sell: indic20 xover indic10,
        indicator params example
        输入序列，{'indic5':SMA(close,5)}, {'indic5':EMA(close,5)}
        next condition example:
        b: indic10 xover indic20, or indic10.level < 10
        s: indic20 xover indic10, or indic10.level > 90
        '''
    try:
        backtesting = Backtest(data_df, get_strategy_by_category(strategy_category), cash=float(cash), commission=float(commission), margin=float(leverage),
                               trade_on_close=True if trade_on_close == 1 else False,
                               hedging=False, exclusive_orders=False)

        if strategy_category == 'system':
            bt_results = backtesting.run(ta_indicator_dict=ta_indicator_dict, buy_cond_dict=buy_cond_dict,
                                         sell_cond_dict=sell_cond_dict, stoploss=stoploss)

        # print('strategy')
        # print(bt_results.loc['_strategy'])
        # print('equity')
        eq_list = []
        equity = bt_results.loc['_equity_curve']
        trades = bt_results.loc['_trades']

        trades_entry = trades[[
            'EntryBar', 'EntryPrice', 'EntryTime', 'Duration', 'PnL']]
        trades_entry = trades_entry.set_index('EntryTime')

        trades_exit = trades[['ExitBar', 'ExitPrice', 'ExitTime']]
        trades_exit = trades_exit.set_index('ExitTime')
        # trades_exit.index.drop_duplicates()
        trades_exit = trades_exit[~trades_exit.index.duplicated(keep='first')]

        equity = pd.concat([equity, trades_entry], axis=1)
        equity = pd.concat([equity, trades_exit], axis=1)

        for index, row in equity.iterrows():
            direction = None

            if not np.isnan(row['EntryPrice']):
                direction = 'b'
            if not np.isnan(row['ExitPrice']):
                direction = 's'
            if not np.isnan(row['EntryPrice']) and not np.isnan(row['ExitPrice']):
                direction = 'b&s'

            eq_list.append({
                'dt': index,
                'eq': row['Equity']/float(cash),
                'ddp': row['DrawdownPct'],
                'ddd': row['DrawdownDuration'],
                'bs': direction,
                'en_p': row['EntryPrice'] if not np.isnan(row['EntryPrice']) else None,
                'ex_p': row['ExitPrice'] if not np.isnan(row['ExitPrice']) else None,
                'pnl': row['PnL'] if not np.isnan(row['PnL']) else None,
                'dur': row['Duration'],
            })

        eq_list.append({
            'stats': get_bt_stats_list(bt_results)
        })
        return JsonResponse(eq_list, safe=False)
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_bt_stats_list(bt_stats):
    '''
    Start                     2004-08-19 00:00:00
    End                       2013-03-01 00:00:00
    Duration                   3116 days 00:00:00
    Exposure Time [%]                     93.9944
    Equity Final [$]                      51959.9
    Equity Peak [$]                       75787.4
    Return [%]                            419.599
    Buy & Hold Return [%]                 703.458
    Return (Ann.) [%]                      21.328
    Volatility (Ann.) [%]                 36.5383
    Sharpe Ratio                         0.583718
    Sortino Ratio                         1.09239
    Calmar Ratio                         0.444518
    Max. Drawdown [%]                    -47.9801
    Avg. Drawdown [%]                    -5.92585
    Max. Drawdown Duration      584 days 00:00:00
    Avg. Drawdown Duration       41 days 00:00:00
    # Trades                                   65
    Win Rate [%]                          46.1538
    Best Trade [%]                         53.596
    Worst Trade [%]                      -18.3989
    Avg. Trade [%]                        2.35371
    Max. Trade Duration         183 days 00:00:00
    Avg. Trade Duration          46 days 00:00:00
    Profit Factor                         2.08802
    Expectancy [%]                        8.79171
    SQN                                  0.916893
    '''
    bt_result_list = []
    # bt_stats = bt_stats.rename({'Start':'开始时间','End':'结束时间','Duration':'持续时间',
    #                             'Exposure Time [%]':'开盘时间 [%]','Equity Final [￥]':'最终资产 [￥]',
    #                             'Equity Peak [$]':'资产最高值 [￥]',
    #                             'Return [%]':'收益率 [%]',
    #                             'Buy & Hold Return [%]':'买入并持有收益率 [%]',
    #                             'Return (Ann.) [%]':'年化收益率 [%]',
    #                             'Volatility (Ann.) [%]':'年化波动率 [%]',
    #                             'Sharpe Ratio':'回报风险率',
    #                             'Sortino Ratio':'索提诺比率',
    #                             'Calmar Ratio':'卡玛比率',
    #                             'Max. Drawdown [%]':'最大回撤 [%]',
    #                             'Avg. Drawdown [%]':'平均回撤 [%]',
    #                             'Max. Drawdown Duration':'最大回撤周期',
    #                             'Avg. Drawdown Duration':'平均回撤周期',
    #                             'Win Rate [%]':'胜率 [%]',
    #                             'Best Trade [%]':'最佳交易 [%]',
    #                             'Worst Trade [%]': '最差交易 [%]',
    #                             'Avg. Trade [%]':'平均交易 [%]',
    #                             'Max. Trade Duration':'最长交易周期',
    #                             'Avg. Trade Duration':'平均交易周期',
    #                             'Profit Factor':'获利因子',
    #                             'Expectancy [%]':'期望 [%]',
    #                             'SQN':'SQN'})
    for idx, item in bt_stats.iteritems():
        if idx not in ['_strategy', '_equity_curve', '_trades']:
            id_label = ''.join(re.findall(r'[A-Za-z]', idx))
            if type(item) == float:
                if not np.isnan(item):
                    item = round(item, 2) 
                else:
                    item = 'n/a'
            elif type(item) == Timedelta:
                item = Timedelta(item).days
            elif type(item) == date:
                item = item

            bt_result_list.append({
                id_label: item
            })

    return bt_result_list


class OHLCList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, ts_code, freq, period=3):
        try:
            ohlc_list = []
            data_df = get_data(ts_code, freq, )

            if period <= 10:
                start_date = date.today() - timedelta(days=365 * period)
                data_df = data_df.loc[start_date:]

            for idx, rows in data_df.iterrows():
                ohlc = StockHistoryOHLC(
                    trade_date=idx, open=rows['Open'], close=rows['Close'], high=rows['High'], low=rows['Low'], vol=rows['Volume'])
                ohlc_list.append(ohlc)

            serializer = OHLCSerializer(ohlc_list, many=True)
            return Response(serializer.data)
        except StockHistoryDaily.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


def to_ohlc_list(df):
    ohlc_list = []
    get_ma_df(df)
    get_ema_df(df)
    get_bbi_df(df)
    get_boll_df(df)
    get_rsi_df(df)
    get_macd_df(df)
    get_kdj_df(df)

    for idx, rows in df.iterrows():
        ohlc_list.append({
            'o': rows['Open'],
            'h': rows['High'],
            'l': rows['Low'],
            'c': rows['Close'],
            'v': rows['Volume'],
            'ma10': rows['ma_10'] if not np.isnan(rows['ma_10']) else None,
            'ma20': rows['ma_20'] if not np.isnan(rows['ma_20']) else None,
            'ma60': rows['ma_60'] if not np.isnan(rows['ma_60']) else None,
            'ma120': rows['ma_120'] if not np.isnan(rows['ma_120']) else None,
            'ma200': rows['ma_200'] if not np.isnan(rows['ma_200']) else None,
            'ema10': rows['ema_10'] if not np.isnan(rows['ema_10']) else None,
            'ema20': rows['ema_20'] if not np.isnan(rows['ema_20']) else None,
            'ema60': rows['ema_60'] if not np.isnan(rows['ema_60']) else None,
            'ema120': rows['ema_120'] if not np.isnan(rows['ema_120']) else None,
            'ema200': rows['ema_200'] if not np.isnan(rows['ema_200']) else None,
            'rsi6': rows['rsi_6'] if not np.isnan(rows['rsi_6']) else None,
            'rsi12': rows['rsi_12'] if not np.isnan(rows['rsi_12']) else None,
            'rsi24': rows['rsi_24'] if not np.isnan(rows['rsi_24']) else None,
            'bollupper': rows['boll_upper'] if not np.isnan(rows['boll_upper']) else None,
            'bollmid': rows['boll_mid'] if not np.isnan(rows['boll_mid']) else None,
            'bolllower': rows['boll_lower'] if not np.isnan(rows['boll_lower']) else None,
            'bbi': rows['bbi'] if not np.isnan(rows['bbi']) else None,
            'kdjk': rows['k'] if not np.isnan(rows['k']) else None,
            'kdjd': rows['d'] if not np.isnan(rows['d']) else None,
            'kdjj': rows['j'] if not np.isnan(rows['j']) else None,
            'macddif': rows['dif'] if not np.isnan(rows['dif']) else None,
            'macddea': rows['dea'] if not np.isnan(rows['dea']) else None,
            'macdbar': rows['bar'] if not np.isnan(rows['bar']) else None,
            'eq': 1.0,
            'd': idx,
        })
    return ohlc_list


def get_ohlc(request, ts_code, freq, period=3):
    try:
        # ohlc_list = []
        ohlc_df = get_data_since(ts_code, freq, period=period)
        ohlc_data = to_ohlc_list(ohlc_df)

        return JsonResponse(ohlc_data, safe=False)
    except StockHistoryDaily.DoesNotExist:
        raise Http404
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_ma_df(data_df):
    try:
        # df_ma = pd.DataFrame()
        data_df['ma_10'] = ta.MA(data_df['Close'], timeperiod=10, matype=0)
        data_df['ma_20'] = ta.MA(data_df['Close'], timeperiod=20, matype=0)
        data_df['ma_60'] = ta.MA(data_df['Close'], timeperiod=60, matype=0)
        data_df['ma_120'] = ta.MA(data_df['Close'], timeperiod=120, matype=0)
        data_df['ma_200'] = ta.MA(data_df['Close'], timeperiod=200, matype=0)

        return data_df
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_ema_df(data_df):
    try:
        # df_ema = pd.DataFrame()
        data_df['ema_10'] = ta.MA(data_df['Close'], timeperiod=10, matype=1)
        data_df['ema_20'] = ta.MA(data_df['Close'], timeperiod=20, matype=1)
        data_df['ema_60'] = ta.MA(data_df['Close'], timeperiod=60, matype=1)
        data_df['ema_120'] = ta.MA(data_df['Close'], timeperiod=120, matype=1)
        data_df['ema_200'] = ta.MA(data_df['Close'], timeperiod=200, matype=1)

        return data_df
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_boll_df(data_df):
    try:
        data_df['boll_upper'], data_df['boll_mid'], data_df['boll_lower'] = ta.BBANDS(data_df['Close'], timeperiod=20,
                                                                                      nbdevup=2, nbdevdn=2, matype=0)

        return data_df
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_bbi_df(data_df):
    try:
        df_ma = pd.DataFrame()
        df_ma['ma_3'] = ta.MA(data_df['Close'], timeperiod=3)
        df_ma['ma_6'] = ta.MA(data_df['Close'], timeperiod=6)
        df_ma['ma_12'] = ta.MA(data_df['Close'], timeperiod=12)
        df_ma['ma_24'] = ta.MA(data_df['Close'], timeperiod=24)

        # df_bbi = pd.DataFrame()
        data_df['bbi'] = (df_ma['ma_3'] + df_ma['ma_6'] +
                          df_ma['ma_12']+df_ma['ma_24'])/4
        return data_df
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_rsi_df(data_df):
    try:
        # df_rsi = pd.DataFrame()
        data_df['rsi_6'] = ta.RSI(data_df['Close'], timeperiod=6)
        data_df['rsi_12'] = ta.RSI(data_df['Close'], timeperiod=12)
        data_df['rsi_24'] = ta.RSI(data_df['Close'], timeperiod=24)

        return data_df
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_kdj_df(data_df):
    try:
        # df_kdj = pd.DataFrame()
        data_df['k'], data_df['d'] = ta.STOCH(data_df['High'],
                                              data_df['Low'],
                                              data_df['Close'],
                                              fastk_period=9,
                                              slowk_period=3,
                                              slowk_matype=0,
                                              slowd_period=3,
                                              slowd_matype=0)
        data_df['j'] = list(
            map(lambda x, y: 3*x-2*y, data_df['k'], data_df['d']))
        return data_df
    except StockHistoryDaily.DoesNotExist:
        raise Http404
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_macd_df(data_df):
    try:
        # df_macd = pd.DataFrame()
        data_df['dif'], data_df['dea'], data_df['bar'] = ta.MACD(
            data_df['Close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
        return data_df
    except StockHistoryDaily.DoesNotExist:
        raise Http404
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_ema(request, ts_code, freq, period=3):
    try:
        ohlc_list = []
        data_df = get_data(ts_code, freq, )

        if period <= 10:
            start_date = date.today() - timedelta(days=365 * period)
            data_df = data_df.loc[start_date:]

        df_ema = pd.DataFrame()
        df_ema['ema_10'] = ta.EMA(data_df['Close'], timeperiod=10)
        df_ema['ema_20'] = ta.EMA(data_df['Close'], timeperiod=20)
        df_ema['ema_60'] = ta.EMA(data_df['Close'], timeperiod=60)
        df_ema['ema_120'] = ta.EMA(data_df['Close'], timeperiod=120)
        df_ema['ema_200'] = ta.EMA(data_df['Close'], timeperiod=200)

        # rsi_list = []
        # rsi_list.append({
        #     'rsi_6': df_rsi['rsi_6'],
        #     'rsi_12': df_rsi['rsi_12'],
        #     'rsi_24': df_rsi['rsi_24'],
        # })
        # parsed = json.load(df_rsi.to_json())

        # return HttpResponse(df_rsi.to_json(), 200) #JsonResponse({'results': rsi_list}, safe=False)
        return JsonResponse(df_ema.to_json(), safe=False)
    except StockHistoryDaily.DoesNotExist:
        raise Http404
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_ma(request, ts_code, freq, period=3):
    try:
        ohlc_list = []
        data_df = get_data(ts_code, freq, )

        if period <= 10:
            start_date = date.today() - timedelta(days=365 * period)
            data_df = data_df.loc[start_date:]

        df_ma = pd.DataFrame()
        df_ma['ma_10'] = ta.MA(data_df['Close'], timeperiod=10)
        df_ma['ma_20'] = ta.MA(data_df['Close'], timeperiod=20)
        df_ma['ma_60'] = ta.MA(data_df['Close'], timeperiod=60)
        df_ma['ma_120'] = ta.MA(data_df['Close'], timeperiod=120)
        df_ma['ma_200'] = ta.MA(data_df['Close'], timeperiod=200)

        # rsi_list = []
        # rsi_list.append({
        #     'rsi_6': df_rsi['rsi_6'],
        #     'rsi_12': df_rsi['rsi_12'],
        #     'rsi_24': df_rsi['rsi_24'],
        # })
        # parsed = json.load(df_rsi.to_json())

        # return HttpResponse(df_rsi.to_json(), 200) #JsonResponse({'results': rsi_list}, safe=False)
        return JsonResponse(df_ma.to_json(), safe=False)
    except StockHistoryDaily.DoesNotExist:
        raise Http404
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_sma(request, ts_code, freq, period=3):
    try:
        ohlc_list = []
        data_df = get_data(ts_code, freq, )

        if period <= 10:
            start_date = date.today() - timedelta(days=365 * period)
            data_df = data_df.loc[start_date:]

        df_sma = pd.DataFrame()
        df_sma['sma_10'] = ta.SMA(data_df['Close'], 10)
        df_sma['sma_20'] = ta.SMA(data_df['Close'], 20)
        df_sma['sma_60'] = ta.SMA(data_df['Close'], 60)
        df_sma['sma_120'] = ta.SMA(data_df['Close'], 120)
        df_sma['sma_200'] = ta.SMA(data_df['Close'], 200)

        # rsi_list = []
        # rsi_list.append({
        #     'rsi_6': df_rsi['rsi_6'],
        #     'rsi_12': df_rsi['rsi_12'],
        #     'rsi_24': df_rsi['rsi_24'],
        # })
        # parsed = json.load(df_rsi.to_json())

        # return HttpResponse(df_rsi.to_json(), 200) #JsonResponse({'results': rsi_list}, safe=False)
        return JsonResponse(df_sma.to_json(), safe=False)
    except StockHistoryDaily.DoesNotExist:
        raise Http404
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_boll(request, ts_code, freq, period=3):
    try:
        data_df = get_data(ts_code, freq, )

        if period <= 10:
            start_date = date.today() - timedelta(days=365 * period)
            data_df = data_df.loc[start_date:]

        boll = ta.BBANDS(data_df['Close'], timeperiod=20,
                         nbdevup=2, nbdevdn=2, matype=0)
        return JsonResponse({'high': boll[0].to_json(), 'mid': boll[1].to_json(), 'low': boll[2].to_json()}, safe=False)

    except StockHistoryDaily.DoesNotExist:
        raise Http404
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_bbi(request, ts_code, freq, period=3):
    try:
        data_df = get_data(ts_code, freq, )

        if period <= 10:
            start_date = date.today() - timedelta(days=365 * period)
            data_df = data_df.loc[start_date:]

        df_ma = pd.DataFrame()
        df_ma['ma_3'] = ta.MA(data_df['Close'], timeperiod=3)
        df_ma['ma_6'] = ta.MA(data_df['Close'], timeperiod=6)
        df_ma['ma_12'] = ta.MA(data_df['Close'], timeperiod=12)
        df_ma['ma_24'] = ta.MA(data_df['Close'], timeperiod=24)

        df_bbi = pd.DataFrame()
        df_bbi['bbi'] = (df_ma['ma_3'] + df_ma['ma_6'] +
                         df_ma['ma_12']+df_ma['ma_24'])/4
        return JsonResponse(df_bbi.to_json(), safe=False)

    except StockHistoryDaily.DoesNotExist:
        raise Http404
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_rsi(request, ts_code, freq, period=3):
    try:
        ohlc_list = []
        data_df = get_data(ts_code, freq, )

        if period <= 10:
            start_date = date.today() - timedelta(days=365 * period)
            data_df = data_df.loc[start_date:]

        df_rsi = pd.DataFrame()
        df_rsi['rsi_6'] = ta.RSI(data_df['Close'], timeperiod=6)
        df_rsi['rsi_12'] = ta.RSI(data_df['Close'], timeperiod=12)
        df_rsi['rsi_24'] = ta.RSI(data_df['Close'], timeperiod=24)

        rsi_list = []
        # rsi_list.append({
        #     'rsi_6': df_rsi['rsi_6'],
        #     'rsi_12': df_rsi['rsi_12'],
        #     'rsi_24': df_rsi['rsi_24'],
        # })
        # parsed = json.load(df_rsi.to_json())

        # return HttpResponse(df_rsi.to_json(), 200) #JsonResponse({'results': rsi_list}, safe=False)
        return JsonResponse(df_rsi.to_json(), safe=False)
    except StockHistoryDaily.DoesNotExist:
        raise Http404
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_kdj(request, ts_code, freq, period=3):
    try:
        data_df = get_data(ts_code, freq, )

        if period <= 10:
            start_date = date.today() - timedelta(days=365 * period)
            data_df = data_df.loc[start_date:]

        df_kdj = pd.DataFrame()
        df_kdj['k'], df_kdj['d'] = ta.STOCH(data_df['High'],
                                            data_df['Low'],
                                            data_df['Close'],
                                            fastk_period=9,
                                            slowk_period=3,
                                            slowk_matype=0,
                                            slowd_period=3,
                                            slowd_matype=0)
        df_kdj['j'] = list(map(lambda x, y: 3*x-2*y, df_kdj['k'], df_kdj['d']))
        return JsonResponse(df_kdj.to_json(), safe=False)
    except StockHistoryDaily.DoesNotExist:
        raise Http404
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def get_macd(request, ts_code, freq, period=3):
    try:
        ohlc_list = []
        data_df = get_data(ts_code, freq, )

        if period <= 10:
            start_date = date.today() - timedelta(days=365 * period)
            data_df = data_df.loc[start_date:]

        df_macd = pd.DataFrame()
        df_macd['dif'], df_macd['dea'], df_macd['bar'] = ta.MACD(
            data_df['Close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
        # dif[np.isnan(dif)], dea[np.isnan(dea)], bar[np.isnan(bar)] = 0, 0, 0

        rsi_list = []
        # rsi_list.append({
        #     'rsi_6': df_rsi['rsi_6'],
        #     'rsi_12': df_rsi['rsi_12'],
        #     'rsi_24': df_rsi['rsi_24'],
        # })
        # parsed = json.load(df_rsi.to_json())

        # return HttpResponse(df_rsi.to_json(), 200) #JsonResponse({'results': rsi_list}, safe=False)
        return JsonResponse(df_macd.to_json(), safe=False)
    except StockHistoryDaily.DoesNotExist:
        raise Http404
    except Exception as err:
        print(err)
        raise HttpResponseServerError


def realtime_quotes(request, symbols):
    '''
    根据请求的股票代码列表，获得实时报价
    '''
    if request.method == 'GET':
        quote_list = []
        symbol_list = symbols.split(',')
        try:
            realtime_df = ts.get_realtime_quotes(symbol_list)
            realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                                       'high', 'low', 'bid', 'ask', 'volume', 'amount', 'date', 'time']]
            for quote in realtime_df.values:
                quote_list.append(
                    {
                        'code': quote[0],
                        'open': quote[1],
                        'pre_close': round(float(quote[2]), 2),
                        'price': round(float(quote[3]), 2),
                        'high': quote[4],
                        'low': quote[5],
                        'bid': quote[6],
                        'volume': quote[8],
                        'amount': quote[9],
                        'datetime': datetime.strptime(quote[10] + ' ' + quote[11], "%Y-%m-%d %H:%M:%S"),
                    }
                )
            return JsonResponse(quote_list, safe=False)
        except Exception as err:
            logging.error(err)
            return HttpResponse(status=500)


class IndustryList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, industry):
        industry_filter = industry.split(',')
        industry_list = []
        try:
            stocks = StockNameCodeMap.objects.filter(
                asset='E', industry__in=industry_filter).values('industry').annotate(total=Count('ts_code')).order_by('industry')

            for stock in stocks:
                ibqs = get_ind_basic(
                    stock['industry'], ['pe', 'pb', 'ps'])

                si = Industry(industry=stock['industry'], stock_count=stock['total'], pe_10pct=ibqs['pe0.1'] if 'pe0.1' in ibqs else 0,
                              pe_50pct=ibqs['pe0.5'] if 'pe0.5' in ibqs else 0, pe_90pct=ibqs['pe0.9'] if 'pe0.9' in ibqs else 0,
                              pb_10pct=ibqs['pb0.1'] if 'pb0.1' in ibqs else 0, pb_50pct=ibqs['pb0.5'] if 'pb0.5' in ibqs else 0,
                              pb_90pct=ibqs['pb0.9'] if 'pb0.9' in ibqs else 0, ps_10pct=ibqs['ps0.1'] if 'ps0.1' in ibqs else 0,
                              ps_50pct=ibqs['ps0.5'] if 'ps0.5' in ibqs else 0, ps_90pct=ibqs['ps0.9'] if 'ps0.9' in ibqs else 0,)
                industry_list.append(si)
            serializer = IndustrySerializer(industry_list, many=True)
            return Response(serializer.data)
        except Industry.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


class IndustryBasicList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, industry, basic_type, quantile, start_date, end_date):
        try:
            ibqs = IndustryBasicQuantileStat.objects.filter(industry=industry, basic_type=basic_type, quantile=float(quantile),
                                                            snap_date__lte=datetime.strptime(
                                                                end_date, '%Y%m%d'),
                                                            snap_date__gte=datetime.strptime(
                                                                start_date, '%Y%m%d')).values('industry', 'snap_date', 'basic_type',
                                                                                              'stk_quantity', 'quantile', 'quantile_val').order_by('snap_date')
            serializer = IndustryBasicQuantileSerializer(
                ibqs, many=True)
            return Response(serializer.data)
        except Industry.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


class CityList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, province, top):
        try:
            if province != '-1':
                cities = City.objects.filter(
                    province__name=province).values('name')[0:top]
            else:  # period = 0 means all stock history
                cities = City.objects.all().values('name')[0:top]

            serializer = CitySerializer(cities, many=True)
            return Response(serializer.data)
        except StockHistoryDaily.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


class ProvinceList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, country):
        try:
            if country != '-1':
                provinces = Province.objects.filter(
                    country=country).values('name')
            else:  # period = 0 means all stock history
                provinces = Province.objects.all().values('name')

            serializer = ProvinceSerializer(provinces, many=True)
            return Response(serializer.data)
        except StockHistoryDaily.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


class CompanyList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    queryset = StockNameCodeMap.objects.filter(asset='E')
    # def get_queryset(self):
    #     queryset = StockNameCodeMap.objects.all()
    #     # serializer_class = CompanySerializer
    #     return queryset

    def get(self, request, input_text=None):
        try:
            companies = StockNameCodeMap.objects.filter(
                Q(ts_code__contains=input_text)
                | Q(stock_name__contains=input_text)
                | Q(stock_name_pinyin__icontains=input_text)).order_by('list_date')[:10]
            serializer = CompanySerializer(companies, many=True)
            return Response(serializer.data)
        except StockNameCodeMap.DoesNotExist:
            raise Http404
        except Exception as err:
            raise HttpResponseServerError


class StockCloseHistoryList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, ts_code, freq='D', period=3):
        try:
            if period <= 10:
                start_date = date.today() - timedelta(days=365 * period)
                if ts_code in index_list:
                    close_history = StockIndexHistory.objects.filter(
                        ts_code=ts_code, freq=freq, trade_date__gte=start_date,
                        trade_date__lte=date.today()).values('close', 'trade_date').order_by('trade_date')
                else:
                    if freq == 'D':
                        close_history = StockHistoryDaily.objects.filter(
                            ts_code=ts_code, freq=freq, trade_date__gte=start_date,
                            trade_date__lte=date.today()).values('close', 'trade_date').order_by('trade_date')
                    if freq in ['W', 'M']:
                        close_history = StockHistory.objects.filter(
                            ts_code=ts_code, freq=freq, trade_date__gte=start_date,
                            trade_date__lte=date.today()).values('close', 'trade_date').order_by('trade_date')
            else:  # period = 0 means all stock history
                if ts_code in index_list:
                    close_history = StockIndexHistory.objects.filter(
                        ts_code=ts_code, freq=freq, trade_date__lte=date.today()).values('close', 'trade_date').order_by('trade_date')
                else:
                    if freq == 'D':
                        close_history = StockHistoryDaily.objects.filter(
                            ts_code=ts_code, freq=freq, trade_date__lte=date.today()).values('close', 'trade_date').order_by('trade_date')
                    if freq in ['W', 'M']:
                        close_history = StockHistory.objects.filter(
                            ts_code=ts_code, freq=freq, trade_date__lte=date.today()).values('close', 'trade_date').order_by('trade_date')
            # df = pd.DataFrame(close_history, columns=['close','trade_date'])
            # close_qtiles = df.close.quantile(
            #     [0.1, 0.25, 0.5, 0.75, 0.9])

            # df['close_10pct'] = close_qtiles[.1]
            # df['close_50pct'] = close_qtiles[.5]
            # df['close_90pct'] = close_qtiles[.9]

            serializer = StockCloseHistorySerializer(close_history, many=True)
            return Response(serializer.data)
        except StockHistoryDaily.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


class StockRSVPlusList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, ts_code, freq='D', period=3):
        try:
            if period <= 10:
                start_date = date.today() - timedelta(days=365 * period)
                if ts_code in index_list:
                    indic_rsvp = StockHistoryIndicators.objects.filter(
                        ts_code=ts_code, freq=freq, trade_date__gte=start_date,
                        trade_date__lte=date.today()).values('vol', 'trade_date', 'amount', 'rsv', 'eema_b', 'eema_s', 'var1', 'var2', 'var3').order_by('trade_date')
                else:
                    indic_rsvp = StockHistoryIndicators.objects.filter(
                        ts_code=ts_code, freq=freq, trade_date__gte=start_date,
                        trade_date__lte=date.today()).values('vol', 'trade_date', 'amount', 'rsv', 'eema_b', 'eema_s', 'var1', 'var2', 'var3').order_by('trade_date')
            else:  # period = 0 means all stock history
                if ts_code in index_list:
                    indic_rsvp = StockHistoryIndicators.objects.filter(
                        ts_code=ts_code, freq=freq, trade_date__lte=date.today()).values('vol', 'trade_date', 'amount', 'rsv', 'eema_b', 'eema_s', 'var1', 'var2', 'var3').order_by('trade_date')
                else:
                    indic_rsvp = StockHistoryIndicators.objects.filter(
                        ts_code=ts_code, freq=freq, trade_date__lte=date.today()).values('vol', 'trade_date', 'amount', 'rsv', 'eema_b', 'eema_s', 'var1', 'var2', 'var3').order_by('trade_date')
            temp = []
            for indic in indic_rsvp:
                temp.append(indic['vol'])

            scaled_vol = process_min_max(temp)
            i = 0
            for item in indic_rsvp:
                item['vol'] = scaled_vol[i]
                i += 1
            # df = pd.DataFrame(close_history, columns=['close','trade_date'])
            # close_qtiles = df.close.quantile(
            #     [0.1, 0.25, 0.5, 0.75, 0.9])

            # df['close_10pct'] = close_qtiles[.1]
            # df['close_50pct'] = close_qtiles[.5]
            # df['close_90pct'] = close_qtiles[.9]

            serializer = StockIndicRSVSerializer(indic_rsvp, many=True)
            return Response(serializer.data)
        except StockHistoryIndicators.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


class StockDailyBasicHistoryList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, ts_code, start_date, end_date):
        try:
            if ts_code in index_list:
                cdb = IndexDailyBasic.objects.filter(
                    ts_code=ts_code, trade_date__gte=datetime.strptime(
                        start_date, '%Y%m%d'),
                    trade_date__lte=datetime.strptime(end_date, '%Y%m%d'),).values('trade_date', 'pe', 'pe_ttm',
                                                                                   'pb', 'turnover_rate',
                                                                                   ).order_by('trade_date')
                serializer = IndexDailyBasicSerializer(cdb, many=True)

            else:
                cdb = CompanyDailyBasic.objects.filter(
                    ts_code=ts_code, trade_date__gte=datetime.strptime(
                        start_date, '%Y%m%d'),
                    trade_date__lte=datetime.strptime(end_date, '%Y%m%d'),).values('trade_date', 'pe', 'pe_ttm',
                                                                                   'pb', 'ps', 'ps_ttm', 'turnover_rate',
                                                                                   'volume_ratio').order_by('trade_date')

                serializer = CompanyDailyBasicSerializer(cdb, many=True)
            # serializer.fields = basic_type.split(',')
            return Response(serializer.data)
        except CompanyDailyBasic.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


class StockTop10HoldersStatList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, ts_code, period=18):
        try:
            start_date = date.today() - timedelta(days=365 * period)
            ctfshs = CompanyTop10FloatHoldersStat.objects.filter(
                ts_code=ts_code, end_date__gte=start_date,
                end_date__lte=date.today(),).order_by('end_date')

            serializer = CompanyTop10HoldersStatSerializer(ctfshs, many=True)
            # serializer.fields = basic_type.split(',')
            return Response(serializer.data)
        except CompanyTop10FloatHoldersStat.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


class StockFinanceIndicatorStatList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, ts_code, period=18):
        try:
            start_date = date.today() - timedelta(days=365 * period)
            ctfshs = CompanyFinIndicators.objects.filter(
                ts_code=ts_code, end_date__gte=start_date,
                end_date__lte=date.today(),).order_by('end_date').values(
                    # neg current_ratio
                    'total_revenue_ps', 'revenue_ps', 'surplus_rese_ps', 'undist_profit_ps', 'current_ratio',
                    'ar_turn', 'interst_income', 'daa', 'ebit', 'ebitda', 'current_exint', 'noncurrent_exint', 'interestdebt',
                    'fcff', 'fcfe', 'netdebt', 'tangible_asset', 'working_capital', 'invest_capital', 'retained_earnings',
                    # neg roa2_yearly,ca_to_assets
                    'bps', 'retainedps', 'roa2_yearly', 'assets_to_eqt', 'dp_assets_to_eqt', 'ca_to_assets', 'nca_to_assets',
                    # neg tangibleasset_to_debt,tbassets_to_totalassets,tangibleasset_to_debt
                    'tbassets_to_totalassets', 'eqt_to_talcapital', 'debt_to_eqt', 'tangibleasset_to_debt',
                    # neg roa_yearly,total_fa_trun
                    'longdebt_to_workingcapital', 'fixed_assets', 'total_fa_trun', 'q_opincome', 'q_investincome', 'q_dtprofit', 'q_eps',
                    # '','','','','','','','','','',
            )

            serializer = CompanyTop10HoldersStatSerializer(ctfshs, many=True)
            # serializer.fields = basic_type.split(',')
            return Response(serializer.data)
        except CompanyTop10FloatHoldersStat.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


def get_companies(request, input_text):
    '''
    根据输入获得上市公司信息
    需要更新板块，SQL如下
    update public.stockmarket_stocknamecodemap
    set market='SHZB'
    where market='ZB'

    update  public.stockmarket_stocknamecodemap
    set market='SZZB'
    where market='ZXB'

    update  public.stockmarket_stocknamecodemap
    set market='ZXB'
    where stock_code like '002%'
    '''

    if request.method == 'GET':
        try:
            if not input_text.isnumeric():
                companies = StockNameCodeMap.objects.filter(
                    Q(stock_name__contains=input_text) | Q(stock_name_pinyin__icontains=input_text)).order_by('list_date')[:10]
            elif input_text.isnumeric():
                companies = StockNameCodeMap.objects.filter(
                    stock_code__contains=input_text).order_by('list_date')[:10]
            else:  # 输入条件是拼音首字母
                pass
            company_list = []
            if companies is not None and companies.count() > 0:
                for c in companies:
                    # 获得ts_code
                    company_list.append({
                        'id': c.stock_code,
                        'ts_code': c.ts_code,
                        'text': c.stock_name,
                        'market': board_list[c.market],
                        'industry': c.industry,
                        'list_date': c.list_date,
                        'area': c.area,
                    })
                # c_str = 'results:[' + c_str + ']'
                # c_dict = json.loads(c_str)
                return JsonResponse({'results': company_list}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as e:
            logger.error(e)
            return HttpResponse(status=500)


def get_company_basic(request, ts_code):
    if request.method == 'GET':
        company_basic_list = []
        req_user = request.user
        try:
            pro = ts.pro_api()
            ts_code_list = ts_code.split(',')
            if len(ts_code_list) > 0:
                for code in ts_code_list:
                    if req_user.is_anonymous:
                        req_user = None
                    query_trace = UserQueryTrace(
                        query_string=code, request_url=request.environ['HTTP_REFERER'], ip_addr=get_ip(request), uid=req_user)
                    query_trace.save()

                    company_basic = StockNameCodeMap.objects.filter(
                        ts_code=code)
                    if company_basic is not None and len(company_basic) > 0:
                        df = pro.stock_company(
                            ts_code=code, fields='ts_code,chairman,manager,reg_capital,setup_date,province,city,website,employees,main_business')
                        if df is not None and len(df) > 0:
                            company_basic_list.append(
                                {
                                    'ts_code': code,
                                    'company_name': company_basic[0].fullname,
                                    'chairman': df['chairman'][0],
                                    'manager': df['manager'][0],
                                    'reg_capital': df['reg_capital'][0],
                                    'setup_date': df['setup_date'][0],
                                    'province': df['province'][0],
                                    'city': df['city'][0],
                                    'website': df['website'][0],
                                    'employees': int(df['employees'][0]),
                                    'main_business': df['main_business'][0],
                                }
                            )
                return JsonResponse(company_basic_list, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)


def get_industry_basic(request, industry, type):
    ind_dict = {}
    ind_basic = []
    industries = industry.split(',')
    basic_types = type.split(',')

    try:
        req_user = request.user
        last_analysis = AnalysisDateSeq.objects.filter(
            applied=True, seq_type='INDUSTRY_BASIC_QUANTILE').order_by('-analysis_date').first()

        for ind in industries:
            ibqs = IndustryBasicQuantileStat.objects.filter(industry=ind, basic_type__in=basic_types, snap_date=last_analysis.analysis_date).exclude(
                quantile=.25).exclude(quantile=.75).order_by('-snap_date')

            if ibqs is not None and len(ibqs) > 0:
                for ibq in ibqs:
                    ind_basic.append(
                        {
                            'type': ibq.basic_type,
                            'qt': ibq.quantile,
                            'val': ibq.quantile_val
                        }
                    )
                ind_dict[ind] = ind_basic
        return JsonResponse({'content': ind_dict}, safe=False)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)
    pass


def get_latest_daily_basic(request, ts_code):
    basic_list = []
    try:
        cdb = CompanyDailyBasic.objects.filter(
            ts_code=ts_code,).order_by('-trade_date').first()
        if cdb is not None:
            basic_list.append({
                'pe': round(cdb.pe, 2) if cdb.pe is not None else 0,
                'pe_ttm': round(cdb.pe_ttm, 2) if cdb.pe_ttm is not None else 0,
                'pb': round(cdb.pb, 2) if cdb.pb is not None else 0,
                'ps': round(cdb.ps, 2) if cdb.ps is not None else 0,
                'ps_ttm': round(cdb.ps_ttm, 2) if cdb.ps_ttm is not None else 0,
            })
        return JsonResponse({'latest_basic': basic_list}, safe=False)
    except Exception as err:
        return HttpResponse(status=500)
    pass


def command_test(request):
    try:
        companies_bef = CompanyBasic.objects.filter(
        ).order_by().values('province', 'city').distinct()
        # print(len(companies_bef))
        # companies = StockNameCodeMap.objects.all()
        for c in companies_bef:
            print(c['province'])
            print(c['city'])
            prov = Province(name=c['province'], province_pinyin=pinyin_abbrev(
                c['province']))
            prov.save()
            city = City(name=c['city'], proince=c['province'], city_pinyin=pinyin_abbrev(
                c['city']))
            city.save()

            print(c['province'] + ' created.')
            print(c['city'] + ' created.')

            cb = CompanyBasic.objects.filter(
                province=c['province'])
            for b in cb:
                b.shengfen = prov
                b.chengshi = city
                b.save()
                print(prov.name + ',' + city.name + ' FK updated for ' +
                      b.ts_code + ' CompanyBasic.')

            companies = StockNameCodeMap.objects.filter(
                area=c['province'])
            for company in companies:
                company.province = prov
                company.save()
                print(prov.name + ' FK updated for ' +
                      company.ts_code + ' StockNameCode.')
    except Exception as err:
        print(err)


# Create your views here.
def analysis_command(request, cmd, params):
    p = params.split(',')

    try:
        plist = params.split(',')
        if cmd == 'ibq':
            # quantile = [.1, .25, .5, .75, .9]
            # # get last end date
            # next_dates = next_date()
            # process_industrybasic_quantile(
            #     quantile, next_dates,)
            pass
        if cmd == 'cfi':
            collect_fin_indicators(plist[0])
        if cmd == 'popdb2fin':
            pop_dailybasic_to_finindicator(plist[0])
        if cmd == 'coltop10holders':
            collect_top10_holders(plist[0] if plist[0] != '' else None)
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=500)
