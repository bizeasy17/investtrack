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

from analysis.analysis_junxian_bs_cp import mark_junxian_bs_listed
from analysis.strategy_quantiles_stats import (StrategyTargetPctTestRanking,
                                               StrategyUpDownTestRanking)
from investors.models import StockFollowing, TradeStrategy
from stockmarket.models import StockNameCodeMap

from .models import (BStrategyOnFixedPctTest, BStrategyOnPctTest,
                     StockHistoryDaily, StrategyTestLowHigh, TradeStrategyStat)

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
    chart_label = ['10ile','25ile','50ile','75ile','90ile']
    qt_pct_list = ['qt_10pct', 'qt_25pct', 'qt_50pct',
                     'qt_75pct', 'qt_90pct',]#, 'mean_val', 'min_val', 'max_val']
    buy_strategy_list = ['jiuzhuan_b', 'dibu_b', 'w_di', 'ma25_tupo_b', 'ma25_zhicheng_b', 'tupo_yali_b']
    buy_strategy_label = ['九转买', '底部', 'W底', '突破MA25', 'MA25支撑', '突破压力']
    sell_strategy_list = ['jiuzhuan_s', 'dingbu_s', 'm_ding', 'ma25_diepo_s', 'ma25_yali_s', 'diepo_zhicheng_s']
    sell_strategy_label = ['九转卖', '顶部', 'M顶', '跌破MA25', 'MA25压力', '跌破支撑']

    try:
        # rankings = StrategyUpDownTestRanking.objects.filter(ts_code=stock_symbol, test_period=test_period, test_type=test_type, qt_pct__in=qt_pct_list).order_by('qt_pct')
        rankings = StrategyUpDownTestRanking.objects.filter(ts_code=stock_symbol, test_period=test_period, qt_pct__in=qt_pct_list).order_by('qt_pct')
        # for qt_pct in qt_pct_list:
        if strategy_ctg == 'b':
            strategy_label = buy_strategy_label
            for buy_strategy in buy_strategy_list:
                strategy_ranking_list = []
                rankings_by_strategy = rankings.filter(strategy_code=buy_strategy, test_type=test_type)
                for ranking_by_strategy in rankings_by_strategy:
                    strategy_ranking_list.append(ranking_by_strategy.qt_pct_val)
                rtn_ranking_list.append(strategy_ranking_list)
                # pass
        else:
            strategy_label = sell_strategy_label
            for sell_strategy in sell_strategy_list:
                strategy_ranking_list = []
                rankings_by_strategy = rankings.filter(strategy_code=sell_strategy, test_type=test_type)
                for ranking_by_strategy in rankings_by_strategy:
                    strategy_ranking_list.append(ranking_by_strategy.qt_pct_val)
                rtn_ranking_list.append(strategy_ranking_list)
                strategy_ranking_list.clear()
        
        df = pd.DataFrame(rtn_ranking_list, columns=chart_label)
        for qt_pct in chart_label:
            mean_list.append(round(df[qt_pct].mean(),3))
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
    chart_label = ['10ile','25ile','50ile','75ile','90ile']
    qt_pct_list = ['qt_10pct', 'qt_25pct', 'qt_50pct',
                     'qt_75pct', 'qt_90pct',]#, 'mean_val', 'min_val', 'max_val']
    buy_strategy_list = ['jiuzhuan_b', 'dibu_b', 'w_di', 'ma25_tupo_b', 'ma25_zhicheng_b', 'tupo_yali_b']
    buy_strategy_label = ['九转买', '底部', 'W底', '突破MA25', 'MA25支撑', '突破压力']
    sell_strategy_list = ['jiuzhuan_s', 'dingbu_s', 'm_ding', 'ma25_diepo_s', 'ma25_yali_s', 'diepo_zhicheng_s']
    sell_strategy_label = ['九转卖', '顶部', 'M顶', '跌破MA25', 'MA25压力', '跌破支撑']

    try:
        rankings = StrategyTargetPctTestRanking.objects.filter(ts_code=stock_symbol, target_pct=target_pct, qt_pct__in=qt_pct_list).order_by('qt_pct')
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
            mean_list.append(round(df[qt_pct].mean(),3))
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


from analysis.v2.mark_junxian_cp_v2 import handle_junxian_cp
from analysis.analysis_dingdi import handle_dingdi_cp
from analysis.analysis_tupo_b_cp import handle_tupo_cp


def analysis_command(request, cmd, params):
    try:
        plist = params.split(',')
        if cmd == 'mark_junxian_cp':
            handle_junxian_cp(plist[0],plist[1],plist[2],plist[3])
        elif cmd == 'dingdi':
            handle_dingdi_cp(plist[0],plist[1],plist[2],plist[3],plist[4])
        elif cmd == 'tupo':
            handle_tupo_cp(plist[0], plist[1],plist[3],plist[4])
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=500)
    