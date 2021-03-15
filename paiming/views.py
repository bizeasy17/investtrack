import pandas as pd
import logging
import pytz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from users.models import UserActionTrace, UserQueryTrace
from analysis.utils import get_ip
from analysis.models import StrategyUpDownTestRanking, StrategyTargetPctTestRanking
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
        try:
            if len(request.GET) > 0:
                # query_trace = UserQueryTrace(query_string=request.GET['q'], request_url=request.path, ip_addr=get_ip(request), uid=req_user)
                # query_trace.save()
                return render(request, self.search_template, {self.context_object_name: {'ts_code':request.GET['q']}})
            else:
                return render(request, self.template_name)
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
