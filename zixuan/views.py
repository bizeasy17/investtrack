from os import stat
from investtrack.settings import NEAREST_THRESHOLD
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
from analysis.models import StockQuantileStat
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
        count_ind = 0
        count_stk = 0
        login_url = reverse("account:login")

        if not req_user.is_anonymous:
            try:
                industries = StockFollowing.objects.filter(
                    trader=req_user).order_by().values('industry').distinct()
                count_ind = len(industries)
                if len(industries) > 0:
                    for ind in industries:
                        stocks = StockFollowing.objects.filter(trader=req_user,
                                                            industry=ind['industry'])
                        for stk in stocks:
                            stk_dic[stk.ts_code] = stk.stock_name
                            count_stk += 1
                        stk_ind_dic[ind['industry']] = stk_dic
                        stk_dic = {}
            except Exception as err:
                logger.error(err)

            return render(request, self.template_name, {self.context_object_name: stk_ind_dic, 'cnt_ind': count_ind, 'cnt_stk': count_stk})
        else:
            return render(request, self.template_name, {'cnt_ind': count_ind, 'cnt_stk': count_stk})


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
                            stk['close'], stk['pct_chg'], stk['jiuzhuan_count_b'], stk['jiuzhuan_count_s'], get_stock_nearest_qtpct(ts_code=stk['ts_code'], close=stk['close'])]
            return JsonResponse({'content': selected_stk}, safe=False)
        else:
            return HttpResponse(status=404)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)


def get_stock_nearest_qtpct(ts_code, close):
    stat_list = []
    stats = StockQuantileStat.objects.filter(ts_code=ts_code).order_by('period')
    if stats is not None:
        for stat in stats:
            if stat.quantile == 0.5 and abs(close-stat.price)/stat.price <= NEAREST_THRESHOLD:
                stat_list.append({
                    'traffic_light': 'Y',
                    'msg': '股价处于' + (str(stat.period) if stat.period != 99 else '全部历史') + '年中位',
                    'type': stat.stat_type,
                    'period': stat.period,
                    'qt': stat.quantile,
                    'price': stat.price
                })
            
            if stat.quantile == 0.1 and close <= stat.price * (1 + NEAREST_THRESHOLD):
                stat_list.append({
                    'traffic_light': 'G',
                    'msg': '股价处于' + (str(stat.period) if stat.period != 99 else '全部历史') + '年低位',
                    'type': stat.stat_type,
                    'period': stat.period,
                    'qt': stat.quantile,
                    'price': stat.price
                })

            if stat.quantile == 0.9 and close >= stat.price * (1 + NEAREST_THRESHOLD):
                stat_list.append({
                    'traffic_light': 'R',
                    'msg': '股价处于' + (str(stat.period) if stat.period != 99 else '全部历史') + '年高位',
                    'type': stat.stat_type,
                    'period': stat.period,
                    'qt': stat.quantile,
                    'price': stat.price
                })
            
            if len(stat_list) > 0:
                return stat_list
    return None
    # pass
