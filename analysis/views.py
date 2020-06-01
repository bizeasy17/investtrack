import decimal
import logging
from datetime import date, datetime, timedelta

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
                     BStrategyTestResultOnDays, TradeStrategyStat)

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
            strategie_ctgs = TradeStrategyStat.objects.filter(
                category=None)
            queryset = {
                'strategy_ctgs': strategie_ctgs,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})


@login_required
def strategies_by_category(request, parent_strategy):
    user = request.user
    if request.method == 'GET':
        try:
            strategy_list = []
            strategies = TradeStrategyStat.objects.filter(
                category=parent_strategy)
            for strategy in strategies:
                strategy_list.append(
                    {
                        'id': strategy.id,
                        'strategy_code': strategy.code,
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
            return HttpResponse(status=404)


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
            # rst_pct_max = []
            # rst_pct_mean = []
            # kwargs = {
            #     # '{0}'.format(exp_pct): -1,
            #     '{0}__{1}'.format(exp_pct, 'lt'): 240
            # }

            results = BStrategyOnFixedPctTest.objects.filter(
                test_strategy=TradeStrategy.objects.get(code=strategy), ts_code=stock_symbol,
                test_freq=freq).order_by('trade_date').values('trade_date', exp_pct)  # [:int(freq_count)]
            for rst in results:
                if rst[exp_pct] > 0 and rst[exp_pct] <= 480:
                    data_label.append(rst['trade_date'])
                    exp_pct_data.append(rst[exp_pct])
            return JsonResponse({'value': exp_pct_data, 'label': data_label}, safe=False)
        except IndexError as err:
            print(err)
            logging.error(err)
            return HttpResponse(status=404)
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
            results = BStrategyTestResultOnDays.objects.filter(
                test_strategy=TradeStrategy.objects.get(code=strategy), ts_code=stock_symbol, test_period=test_period, stage_high=True).order_by('trade_date')
            for result in results:
                result_pct.append(round(result.stage_high_pct,2))
                result_label.append(result.trade_date)
            return JsonResponse({'value': result_pct, 'label': result_label}, safe=False)
        except IndexError as err:
            logging.error(err)
            return HttpResponse(status=404)
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
            results = BStrategyTestResultOnDays.objects.filter(
                test_strategy=TradeStrategy.objects.get(code=strategy), ts_code=stock_symbol, test_period=test_period, stage_low=True).order_by('trade_date')
            for result in results:
                result_pct.append(round(result.stage_low_pct,2))
                result_label.append(result.trade_date)
            return JsonResponse({'value': result_pct, 'label': result_label}, safe=False)
        except IndexError as err:
            logging.error(err)
            return HttpResponse(status=404)
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
