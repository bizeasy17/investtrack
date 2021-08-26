from analysis.models import StockHistoryDaily
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
from stockmarket.models import StockNameCodeMap
from investors.models import StockFollowing
# Create your views here.

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'zixuan/home.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'zixuan'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        # if req_user is not None:
        #     pass
        # else:
        #     pass
        stk_ind_dic = {}
        stk_dic = {}
        try:
            industries = StockFollowing.objects.filter(
                trader=req_user).order_by().values('industry').distinct()

            if len(industries) > 0:
                for ind in industries:
                    stocks = StockFollowing.objects.filter(trader=req_user,
                                                           industry=ind['industry'])
                    for stk in stocks:
                        stk_dic[stk.ts_code] = stk.stock_name
                    stk_ind_dic[ind['industry']] = stk_dic
                    stk_dic = {}
        except Exception as err:
            logger.err(err)

        return render(request, self.template_name, {self.context_object_name: stk_ind_dic})


@login_required
def get_selected_latest_price(request):
    selected_stk = {}

    try:
        req_user = request.user
        picked_stocks = StockFollowing.objects.filter(
            trader=req_user)

        if picked_stocks is not None and len(picked_stocks) > 0:
            for picked_stock in picked_stocks:
                stock_hist = StockHistoryDaily.objects.filter(ts_code=picked_stock.ts_code).values(
                    'ts_code', 'close', 'pct_chg', 'jiuzhuan_count_b', 'jiuzhuan_count_s').order_by('-trade_date')[:1]
                if stock_hist is not None and len(stock_hist) > 0:
                    for stk in stock_hist:
                        selected_stk[stk['ts_code']] = [
                            stk['close'], stk['pct_chg'], stk['jiuzhuan_count_b'], stk['jiuzhuan_count_s']]
            return JsonResponse({'content': selected_stk}, safe=False)
        else:
            return HttpResponse(status=404)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)
