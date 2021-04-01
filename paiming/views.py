import logging

import pandas as pd
import pytz
from analysis.models import (StrategyTargetPctTestRanking,
                             StrategyUpDownTestRanking)
from analysis.utils import get_ip
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from users.models import UserActionTrace, UserQueryTrace

from .utils import (build_area_label, build_board_label, build_degree_label,
                    build_industry_label, build_province_label, build_marketval_label)

# Create your views here.

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'paiming/home.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'paiming'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        # if req_user is not None:
        #     pass
        # else:
        #     pass
        filters = []
        province = []
        area = []
        board = []
        degree = []
        industry = []
        pe = []
        mv = []
        try:
            # board = ['深市主板','科创板']
            build_board_label(board)
            build_area_label(area)
            build_industry_label(industry)
            build_province_label(province)
            build_degree_label(degree)
            build_marketval_label(mv)
            
            filters.append(board)
            filters.append(area)
            filters.append(industry)
            filters.append(province)
            filters.append(degree)
            filters.append(mv)

            if len(request.GET) > 0:
                # query_trace = UserQueryTrace(query_string=request.GET['q'], request_url=request.path, ip_addr=get_ip(request), uid=req_user)
                # query_trace.save()
                return render(request, self.search_template, {self.context_object_name: {'ts_code':request.GET['q'], 'filters': filters}})
            else:
                return render(request, self.template_name, {self.context_object_name: {'filters': filters}})
        except Exception as err:
            logger.error(err)


def get_btest_ranking(request, strategy_code, test_type, qt_pct, input_param, start_idx, end_idx):
    ranked_list = []
    if request.method == 'GET':
        '''
        1. Company Basic
        2. Company Daily Basic
        3. BTEST Quantile
        '''
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
