import decimal
import logging
from calendar import monthrange
from datetime import date, datetime, timedelta

import pandas as pd
import pytz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from investors.models import StockFollowing, TradeStrategy
from stockmarket.models import StockNameCodeMap
from stockmarket.utils import get_realtime_quotes, get_stocknames

from analysis.analysis_dingdi import pre_handle_dd
from analysis.analysis_jiuzhuan_cp import handle_jiuzhuan_cp
from analysis.analysis_junxian_bs_cp import mark_junxian_bs_listed
from analysis.analysis_tupo_b_cp import handle_tupo_cp
from analysis.dl_daily_basic import handle_daily_basic
from analysis.stock_hist import process_stock_download
from analysis.strategy_quantiles_stats import (StrategyTargetPctTestRanking,
                                               StrategyUpDownTestRanking)
from analysis.utils import (get_pct_val_from, get_qt_period_on_exppct,
                            get_qt_updownpct)
from analysis.v2.mark_junxian_cp_v2 import pre_handle_jx
from analysis.xuangu.pick_stocks import handle_stocks_pick
from analysis.strategy_test_period import btest_pct_on_period

from .models import (BStrategyOnFixedPctTest, BStrategyOnPctTest,
                     PickedStocksMeetStrategy, StockHistoryDaily,
                     StrategyTestLowHigh, TradeStrategyStat)

logger = logging.getLogger(__name__)

# Create your views here.


class AnalysisHomeView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'analysis/index.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'analysis'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        if req_user is not None:
            ts_code = '000001.SH'
            stock_name = '上证指数'
            ts_code_no_surfix = '000001.SH'
            code_map = None
            if len(kwargs) > 0:
                # ts_code = kwargs['ts_code']
                try:
                    code_map = StockNameCodeMap.objects.get(
                        ts_code=kwargs['ts_code'])
                    ts_code = code_map.ts_code
                    ts_code_no_surfix = ts_code.split('.')[0]
                    stock_name = code_map.stock_name
                except Exception as e:
                    print(e)
            strategie_ctgs = TradeStrategyStat.objects.all().order_by(
                'category').distinct('category')
            stocks_following = StockFollowing.objects.filter(
                trader=req_user.id,)
            queryset = {
                'strategy_ctgs': strategie_ctgs,
                'followings': stocks_following,
                'ts_code': ts_code,
                'ts_code_only': ts_code_no_surfix,
                'stock_name': stock_name,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})


class PaimingHomeView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'analysis/paiming.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'paiming'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        if req_user is not None:
            strategie_ctgs = TradeStrategyStat.objects.all().order_by(
                'category').distinct('category')
            stocks_following = StockFollowing.objects.filter(
                trader=req_user.id,)
            queryset = {
                'strategy_ctgs': strategie_ctgs,
                'followings': stocks_following,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})


class XuanguHomeView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'analysis/xuangu.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'xg'
    today = date.today()

    # if today.weekday() == 5:  # 周六推1天
    #     today = today - timedelta(days=1)
    # elif today.weekday == 6:  # 周日推2天
    #     today = today - timedelta(days=2)

    def get(self, request, *args, **kwargs):
        req_user = request.user
        if req_user is not None:
            mon_range = monthrange(self.today.year, self.today.month)
            days_of_mon = mon_range[1]
            days = []
            for i in range(days_of_mon):
                days.append(i+1)
            queryset = {
                'cur_year': self.today.year,
                'cur_mon': self.today.month,
                'cur_day': self.today.day,
                'days': days,
                'mons': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                'yrs': [self.today.year, self.today.year+1]
            }
            return render(request, self.template_name, {self.context_object_name: queryset})


class YuceHomeView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'analysis/yuce.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'yuce'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        if req_user is not None:
            strategie_ctgs = TradeStrategyStat.objects.all().order_by(
                'category').distinct('category')
            stocks_following = StockFollowing.objects.filter(
                trader=req_user.id,)
            queryset = {
                'strategy_ctgs': strategie_ctgs,
                'followings': stocks_following,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})


class ZhenguHomeView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'analysis/zhengu.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'zhengu'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        if req_user is not None:
            strategie_ctgs = TradeStrategyStat.objects.all().order_by(
                'category').distinct('category')
            stocks_following = StockFollowing.objects.filter(
                trader=req_user.id,)
            queryset = {
                'strategy_ctgs': strategie_ctgs,
                'followings': stocks_following,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})


@login_required
def get_picked_stocks_bundle(request, year, mon, day, strategy_code, period=80, exp_pct='pct20_period', start_idx=0, end_idx=5):
    pk_stock_list = []
    code_list = []
    code_sfx_list = []
    try:
        picked_stocks = PickedStocksMeetStrategy.objects.filter(
            strategy_code=strategy_code, trade_date=datetime(year, mon, day)).order_by('ts_code')
        # picked_stocks = PickedStocksMeetStrategy.objects.filter(
        #     strategy_code=strategy_code.split('_')[0]+'_count_'+strategy_code.split('_')[1], trade_date=datetime(year, mon, day))[start_idx:end_idx]
        if picked_stocks is not None and len(picked_stocks) > 0:
            for picked_stock in picked_stocks[start_idx:end_idx]:
                code_list.append(picked_stock.ts_code.split('.')[0])
                code_sfx_list.append(picked_stock.ts_code)

            quotes = get_realtime_quotes(code_list)
            stocknames = get_stocknames(code_sfx_list)
            for ts_code in code_sfx_list:
                qt_uppct = get_qt_updownpct(
                    ts_code, strategy_code, period, 'up_pct')
                qt_downpct = get_qt_updownpct(
                    ts_code, strategy_code, period, 'down_pct')
                qt_targetpct = get_qt_period_on_exppct(
                    ts_code, strategy_code, exp_pct)
                pk_stock_list.append({
                    'ts_code': ts_code,
                    'stockname': stocknames[ts_code],
                    'price': quotes[ts_code.split('.')[0]].split(',')[0],
                    'chg_pct': quotes[ts_code.split('.')[0]].split(',')[1],
                    'qt_uppct': qt_uppct,
                    'qt_downpct': qt_downpct,
                    'qt_targetpct': qt_targetpct,
                })
            return JsonResponse({'value': pk_stock_list, 'row_count': len(picked_stocks)}, safe=False)
        else:
            return HttpResponse(status=404)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)

@login_required
def get_picked_stocks(request, strategy_code, pick_date):
    code_list = []
    picked_stocks = PickedStocksMeetStrategy.objects.filter(
        strategy_code=strategy_code, trade_date=pick_date)
    if picked_stocks is not None and len(picked_stocks) > 0:
        for picked_stock in picked_stocks:
            code_list.append(picked_stock['ts_code'])
        return JsonResponse({'value': code_list}, safe=False)
    else:
        return HttpResponse(status=404)


def get_qt_uppct(request, ts_codes, strategy_code):
    qt_list = []
    code_list = ts_codes.split(',')
    for ts_code in code_list:
        qt_uppct = get_qt_updownpct(ts_code, strategy_code, 'up_pct')
        qt_list.append(qt_uppct)
    if qt_list is not None and len(qt_list) > 0:
        return JsonResponse({'value': qt_list}, safe=False)
    else:
        return HttpResponse(status=404)


def get_qt_downpct(request, ts_codes):
    qt_list = []
    code_list = ts_codes.split(',')
    for ts_code in code_list:
        qt_uppct = get_qt_updownpct(ts_code, strategy_code, 'down_pct')
        qt_list.append(qt_uppct)
    if qt_list is not None and len(qt_list) > 0:
        return JsonResponse({'value': qt_list}, safe=False)
    else:
        return HttpResponse(status=404)


def get_qt_targetpct(request, ts_codes):
    qt_list = []
    code_list = ts_codes.split(',')
    for ts_code in code_list:
        qt_targetpct = get_qt_period_on_exppct(
            ts_code, strategy_code,)
        qt_list.append(qt_targetpct)
    if qt_list is not None and len(qt_list) > 0:
        return JsonResponse({'value': qt_list}, safe=False)
    else:
        return HttpResponse(status=404)
    pass


@login_required
def strategies_by_category(request, parent_strategy):
    user = request.user
    if request.method == 'GET':
        try:
            strategy_list = []
            strategies = TradeStrategyStat.objects.filter(
                category=parent_strategy).order_by('code').distinct('code')
            for strategy in strategies:
                strategy.name = strategy.name.split('(')[0]
                strategy_list.append(
                    {
                        'id': strategy.id,
                        'strategy_name': strategy.name,
                        'count': strategy.count,
                        'success_count': strategy.success_count,
                        'fail_count': strategy.fail_count,
                        'success_rate': strategy.success_rate,
                        'code': strategy.code,
                        'analyzed': strategy.hist_analyzed,
                    }
                )
            return JsonResponse(strategy_list, safe=False)
        except IndexError as err:
            logging.error(err)
            return HttpResponse(status=500)


# @login_required
# def bstrategy_test_result_incr_pct(request, strategy, stock_symbol, test_period):
#     '''
#     用户需要授权可以使用策略
#     '''
#     user = request.user
#     if request.method == 'GET':
#         try:
#             rst_pct_min = []
#             rst_pct_max = []
#             rst_pct_mean = []
#             result_label = ['10%', '20%', '30%', '50%', '80%', '100%']
#             results = BStrategyOnPctTest.objects.filter(
#                 test_strategy=strategy, ts_code=stock_symbol, test_period=test_period)
#             for rst in results:
#                 rst_pct_min = [rst.b_10_pct_min, rst.b_20_pct_min, rst.b_30_pct_min,
#                                rst.b_50_pct_min, rst.b_80_pct_min, rst.b_100_pct_min]
#                 rst_pct_max = [rst.b_10_pct_max, rst.b_20_pct_max, rst.b_30_pct_max,
#                                rst.b_50_pct_max, rst.b_80_pct_max, rst.b_100_pct_max]
#                 rst_pct_mean = [rst.b_10_pct_mean, rst.b_20_pct_mean, rst.b_30_pct_mean,
#                                 rst.b_50_pct_mean, rst.b_80_pct_mean, rst.b_100_pct_mean]
#             return JsonResponse({'v_min': rst_pct_min, 'v_max': rst_pct_max, 'v_mean': rst_pct_mean, 'label': result_label}, safe=False)
#         except IndexError as err:
#             logging.error(err)
#             return HttpResponse(status=404)
#     pass


@login_required
def freq_expected_pct_data(request, strategy, stock_symbol, freq, exp_pct):
    user = request.user
    if request.method == 'GET':
        try:
            exp_pct_data = []
            data_label = []
            quantile = []
            # rst_pct_mean = []
            # kwargs = {
            #     # '{0}'.format(exp_pct): -1,
            #     '{0}__{1}'.format(exp_pct, 'lt'): 240
            # }

            results = BStrategyOnFixedPctTest.objects.filter(
                strategy_code=strategy, ts_code=stock_symbol,
                test_freq=freq).order_by('trade_date').values('trade_date', exp_pct)  # [:int(freq_count)]
            df = pd.DataFrame(results.values())
            qtiles = df[exp_pct].quantile([0.25, 0.5, 0.75])
            # for qtile in qtiles.values():
            for index, value in qtiles.items():
                quantile.append(value)
            quantile.append(round(df[exp_pct].mean(), 3))
            for rst in results:
                if rst[exp_pct] > 0 and rst[exp_pct] <= 480:
                    data_label.append(rst['trade_date'])
                    exp_pct_data.append(rst[exp_pct])
            return JsonResponse({'value': exp_pct_data, 'label': data_label, 'quantile': quantile}, safe=False)
        except Exception as err:
            print(err)
            logging.error(err)
            return HttpResponse(status=500)
    pass


@login_required
def high_pct_data(request, strategy, stock_symbol, test_period):
    '''
    用户需要授权可以使用策略
    '''
    user = request.user
    if request.method == 'GET':
        try:
            result_pct = []
            result_label = []
            quantile = []
            results = StrategyTestLowHigh.objects.filter(
                strategy_code=strategy, ts_code=stock_symbol, test_period=test_period).order_by('trade_date')
            df = pd.DataFrame(results.values('stage_high_pct'))
            qtiles = df.stage_high_pct.quantile([0.25, 0.5, 0.75])
            for qtile in qtiles:
                quantile.append(round(qtile, 3))
            quantile.append(round(df.mean().stage_high_pct, 3))
            for result in results:
                result_pct.append(round(result.stage_high_pct, 2))
                result_label.append(result.trade_date)
            return JsonResponse({'value': result_pct, 'label': result_label, 'quantile': quantile}, safe=False)
        except IndexError as err:
            logging.error(err)
            return HttpResponse(status=500)
    pass


@login_required
def low_pct_data(request, strategy, stock_symbol, test_period):
    '''
    用户需要授权可以使用策略
    '''
    user = request.user
    if request.method == 'GET':
        try:
            result_pct = []
            result_label = []
            quantile = []

            results = StrategyTestLowHigh.objects.filter(
                strategy_code=strategy, ts_code=stock_symbol, test_period=test_period).order_by('trade_date')
            df = pd.DataFrame(results.values('stage_low_pct'))
            qtiles = df.stage_low_pct.quantile([0.25, 0.5, 0.75])
            for qtile in qtiles:
                quantile.append(round(qtile, 3))
            quantile.append(round(df.mean().stage_low_pct, 3))
            for result in results:
                result_pct.append(round(result.stage_low_pct, 2))
                result_label.append(result.trade_date)
            return JsonResponse({'value': result_pct, 'label': result_label, 'quantile': quantile}, safe=False)
        except IndexError as err:
            logging.error(err)
            return HttpResponse(status=500)
    pass


@login_required
def stock_history(request, ts_code, freq, type, period):
    '''
    用户需要授权可以使用策略
    '''
    user = request.user
    # 从当前时间为获取历史的最后一天
    end_date = date.today()
    if request.method == 'GET':
        try:
            close_result = []
            ticks_result = []
            ma25_result = []
            ma60_result = []
            ma200_result = []
            amount_result = []
            lbl_trade_date = []
            quantile = []
            start_date = end_date - timedelta(days=365 * period)
            results = StockHistoryDaily.objects.filter(
                ts_code=ts_code, freq=freq, trade_date__gte=start_date, trade_date__lte=end_date).order_by('trade_date')
            # df = pd.DataFrame(results.values('stage_low_pct'))
            for result in results:
                ma25_result.append(result.ma25)
                ma60_result.append(result.ma60)
                ma200_result.append(result.ma200)
                close_result.append(result.close)
                ticks_result.append(
                    {
                        't': result.trade_date, 'o': result.open, 'h': result.high,
                        'l': result.low, 'c': result.close, 'd': '',
                        'ma25': result.ma25, 'ma60': result.ma60, 'ma200': result.ma200,
                    }
                )
                amount_result.append(result.amount)
                lbl_trade_date.append(result.trade_date)
            if type == 'ticks':
                return JsonResponse({'ticks': ticks_result, 'ma25': ma25_result, 'ma60': ma60_result, 'ma200': ma200_result, 'amount': amount_result, 'label': lbl_trade_date}, safe=False)
            if type == 'close':
                return JsonResponse({'close': close_result, 'ma25': ma25_result, 'ma60': ma60_result, 'ma200': ma200_result, 'amount': amount_result, 'label': lbl_trade_date}, safe=False)
        except Exception as err:
            logging.error(err)
            return HttpResponse(status=500)
    pass


@login_required
def strategy_test_ranking(request, strategy_code, test_type, qt_pct, input_param, start_idx, end_idx):
    '''
    用户需要授权可以使用策略
    '''
    ranked_list = []
    if request.method == 'GET':
        try:
            if test_type == 'up_pct' or test_type == 'down_pct':
                rankings = StrategyUpDownTestRanking.objects.filter(
                    test_type=test_type, strategy_code=strategy_code, qt_pct=qt_pct, test_period=int(input_param)).order_by('ranking')[start_idx:end_idx]
            elif test_type == 'target_pct':
                rankings = StrategyTargetPctTestRanking.objects.filter(
                    qt_pct=qt_pct, strategy_code=strategy_code, target_pct=input_param).order_by('ranking')[start_idx:end_idx]
            if rankings is not None and len(rankings) > 0:
                for ranking in rankings:
                    ranked_list.append(
                        {
                            'qt_pct_val': ranking.qt_pct_val, 'rank': ranking.ranking, 'ts_code': ranking.ts_code, 'stock_name': ranking.stock_name,
                        })
                return JsonResponse(ranked_list, safe=False)
            else:
                return HttpResponse(status=400)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)
    pass


@login_required
def stock_ranking_updown_pct(request, stock_symbol, test_period, strategy_ctg, test_type):
    rtn_ranking_list = []
    ranking_label_list = []
    mean_list = []
    strategy_label = []
    chart_label = ['10ile', '25ile', '50ile', '75ile', '90ile']
    qt_pct_list = ['qt_10pct', 'qt_25pct', 'qt_50pct',
                   'qt_75pct', 'qt_90pct', ]  # , 'mean_val', 'min_val', 'max_val']
    buy_strategy_list = ['jiuzhuan_b', 'dibu_b', 'w_di',
                         'ma25_tupo_b', 'ma25_zhicheng_b', 'tupo_yali_b']
    buy_strategy_label = ['九转买', '底部', 'W底', '突破MA25', 'MA25支撑', '突破压力']
    sell_strategy_list = ['jiuzhuan_s', 'dingbu_s', 'm_ding',
                          'ma25_diepo_s', 'ma25_yali_s', 'diepo_zhicheng_s']
    sell_strategy_label = ['九转卖', '顶部', 'M顶', '跌破MA25', 'MA25压力', '跌破支撑']

    try:
        # rankings = StrategyUpDownTestRanking.objects.filter(ts_code=stock_symbol, test_period=test_period, test_type=test_type, qt_pct__in=qt_pct_list).order_by('qt_pct')
        rankings = StrategyUpDownTestRanking.objects.filter(
            ts_code=stock_symbol, test_period=test_period, qt_pct__in=qt_pct_list).order_by('qt_pct')
        # for qt_pct in qt_pct_list:
        if strategy_ctg == 'b':
            strategy_label = buy_strategy_label
            for buy_strategy in buy_strategy_list:
                strategy_ranking_list = []
                rankings_by_strategy = rankings.filter(
                    strategy_code=buy_strategy, test_type=test_type)
                for ranking_by_strategy in rankings_by_strategy:
                    strategy_ranking_list.append(
                        ranking_by_strategy.qt_pct_val)
                rtn_ranking_list.append(strategy_ranking_list)
                # pass
        else:
            strategy_label = sell_strategy_label
            for sell_strategy in sell_strategy_list:
                strategy_ranking_list = []
                rankings_by_strategy = rankings.filter(
                    strategy_code=sell_strategy, test_type=test_type)
                for ranking_by_strategy in rankings_by_strategy:
                    strategy_ranking_list.append(
                        ranking_by_strategy.qt_pct_val)
                rtn_ranking_list.append(strategy_ranking_list)
                strategy_ranking_list.clear()

        df = pd.DataFrame(rtn_ranking_list, columns=chart_label)
        for qt_pct in chart_label:
            mean_list.append(round(df[qt_pct].mean(), 3))
        return JsonResponse(
            {
                'code': 'OK',
                'label': chart_label,
                'mean': mean_list,
                'strategy_label': strategy_label,
                'rankings': rtn_ranking_list,
            }, safe=False)
        # pass
    except Exception as err:
        logger.error(err)
        return HttpResponse(status=500)

    # ds0 = [32,43,23,54,23]
    # # ds_label = ['jiuzhuan_b', 'dibu_b', 'w_di', 'ma25_tupo_b', 'ma25_zhicheng_b', 'tupo_yali_b']
    # ds1 = [11,23,12,34,45]
    # ds2 = [23,54,23,14,25]
    # ds3 = [32,21,32,44,21]
    # ds4 = [18,21,56,34,80]
    # ds5 = [36,90,89,77,177]

    # rtn_ranking_list.append(ds1)
    # rtn_ranking_list.append(ds2)
    # rtn_ranking_list.append(ds3)
    # rtn_ranking_list.append(ds4)
    # rtn_ranking_list.append(ds5)


@login_required
def stock_ranking_target_pct(request, stock_symbol, target_pct):
    rtn_ranking_list = []
    ranking_label_list = []
    mean_list = []
    strategy_label = []
    chart_label = ['10ile', '25ile', '50ile', '75ile', '90ile']
    qt_pct_list = ['qt_10pct', 'qt_25pct', 'qt_50pct',
                   'qt_75pct', 'qt_90pct', ]  # , 'mean_val', 'min_val', 'max_val']
    buy_strategy_list = ['jiuzhuan_b', 'dibu_b', 'w_di',
                         'ma25_tupo_b', 'ma25_zhicheng_b', 'tupo_yali_b']
    buy_strategy_label = ['九转买', '底部', 'W底', '突破MA25', 'MA25支撑', '突破压力']
    sell_strategy_list = ['jiuzhuan_s', 'dingbu_s', 'm_ding',
                          'ma25_diepo_s', 'ma25_yali_s', 'diepo_zhicheng_s']
    sell_strategy_label = ['九转卖', '顶部', 'M顶', '跌破MA25', 'MA25压力', '跌破支撑']

    try:
        rankings = StrategyTargetPctTestRanking.objects.filter(
            ts_code=stock_symbol, target_pct=target_pct, qt_pct__in=qt_pct_list).order_by('qt_pct')
        # for qt_pct in qt_pct_list:
        strategy_label = buy_strategy_label
        for buy_strategy in buy_strategy_list:
            strategy_ranking_list = []
            rankings_by_strategy = rankings.filter(strategy_code=buy_strategy)
            for ranking_by_strategy in rankings_by_strategy:
                strategy_ranking_list.append(ranking_by_strategy.qt_pct_val)
            rtn_ranking_list.append(strategy_ranking_list)

        df = pd.DataFrame(rtn_ranking_list, columns=chart_label)
        for qt_pct in chart_label:
            mean_list.append(round(df[qt_pct].mean(), 3))
        return JsonResponse(
            {
                'code': 'OK',
                'label': chart_label,
                'mean': mean_list,
                'strategy_label': strategy_label,
                'rankings': rtn_ranking_list,
            }, safe=False)
        # pass
    except Exception as err:
        logger.error(err)
        return HttpResponse(status=500)

    # chart_label = ['10ile','25ile','50ile','75ile','90ile']
    # ds0 = [32,43,23,54,23]
    # ds1 = [11,23,12,34,45]
    # ds2 = [23,54,23,14,25]
    # ds3 = [32,21,32,44,21]
    # ds4 = [18,21,56,34,80]
    # ds5 = [36,90,89,77,177]

    # ranking_list = []
    # ranking_list.append(ds1)
    # ranking_list.append(ds2)
    # ranking_list.append(ds3)
    # ranking_list.append(ds4)
    # ranking_list.append(ds5)

    # return JsonResponse(
    #     {
    #         'code': 'OK',
    #         'label': chart_label,
    #         'mean': ds0,
    #         'rankings': ranking_list,
    #     }, safe=False)


@login_required
def sstrategy_test_result_drop(request, strategy, stock_symbol, test_period):
    '''
    用户需要授权可以使用策略
    '''
    pass


def analysis_command(request, cmd, params):
    try:
        plist = params.split(',')
        if cmd == 'junxian':
            pre_handle_jx(plist[0] if plist[0] !='' else None, plist[1], plist[2], plist[3], plist[4])
        elif cmd == 'dingdi':
            pre_handle_dd(plist[0], plist[1], plist[2], plist[3], plist[4])
        elif cmd == 'tupo':
            handle_tupo_cp(plist[0], plist[1], plist[3], plist[4])
        elif cmd == 'jiuzhuan':
            handle_jiuzhuan_cp(
                plist[0] if plist[0] != '' else None, plist[1] if plist[1] != '' else 'D')
        elif cmd == 'download_hist':
            process_stock_download(
                plist[0] if plist[0] != '' else None, plist[1] if plist[1] != '' else None, 
                plist[2] if plist[2] != '' else None, plist[3] if plist[3] != '' else 'E', 
                plist[4] if plist[4] != '' else 'D')
        elif cmd == 'daily_basic':
            handle_daily_basic(
                plist[0] if plist[0] != '' else None, plist[1] if plist[1] != '' else None, 
                plist[2] if plist[2] != '' else None, plist[3] if plist[4] != '' else 'D')
        elif cmd == 'pick':
            handle_stocks_pick(plist[0] if plist[0] != '' else None)
        elif cmd == 'btest_pct':
            btest_pct_on_period(plist[0] if plist[0] != '' else None, 'D', plist[2])
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=500)
