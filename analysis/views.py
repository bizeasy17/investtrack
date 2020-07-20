import decimal
import logging
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

from .models import (BStrategyOnFixedPctTest, BStrategyOnPctTest,
                     StrategyTestLowHigh, TradeStrategyStat, StockHistoryDaily)

from analysis.analysis_junxian_bs_cp import mark_junxian_bs_listed


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
            strategie_ctgs = TradeStrategyStat.objects.all().order_by(
                'category').distinct('category')
            stocks_following = StockFollowing.objects.filter(
                trader=req_user.id,)
            queryset = {
                'strategy_ctgs': strategie_ctgs,
                'followings': stocks_following,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})

class XuanGuHomeView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'analysis/xuangu.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'xuangu'

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

class YuCeHomeView(LoginRequiredMixin, TemplateView):
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

class ZhenGuHomeView(LoginRequiredMixin, TemplateView):
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
def stock_history(request, strategy, stock_symbol, freq, type, period):
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
                ts_code=stock_symbol, freq=freq, trade_date__gte=start_date, trade_date__lte=end_date).order_by('trade_date')       
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
            else:
                return JsonResponse({'close': close_result, 'ma25': ma25_result, 'ma60': ma60_result, 'ma200': ma200_result, 'amount': amount_result, 'label': lbl_trade_date}, safe=False)
        except Exception as err:
            logging.error(err)
            return HttpResponse(status=500)
    pass


@login_required
def sstrategy_test_result_incr(request, strategy, stock_symbol, test_period):
    '''
    用户需要授权可以使用策略
    '''
    pass


@login_required
def sstrategy_test_result_drop(request, strategy, stock_symbol, test_period):
    '''
    用户需要授权可以使用策略
    '''
    pass


def ma_test(request, stock_symbol, freq):
    # end_date = date.today()
    symbol_list = stock_symbol.split(',')
    res = mark_junxian_bs_listed(freq, symbol_list)
    if res:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)
