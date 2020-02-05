from decimal import *

import tushare as ts
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, DetailView, FormView, ListView

from investmgr.models import (Positions, StockNameCodeMap, TradeRec,
                              TradeStrategy, StockFollowing)

from .forms import UserTradeForm
from .models import User


# Create your views here.
class UserDashboardView(LoginRequiredMixin, View):
    # form_class = UserTradeForm
    # model = TradeRec

    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'users/user_dashboard.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'trade_info'

    def get(self, request, *args, **kwargs):
        username = self.kwargs['username']
        req_user = User.objects.filter(username=username)
        if req_user is not None and req_user.count() > 0:
            tradedetails = TradeRec.objects.filter(
                trader=req_user[0].id, )[:10]
            trade_positions = Positions.objects.filter(
                trader=req_user[0].id).exclude(lots=0)
            strategies = TradeStrategy.objects.filter(creator=req_user[0].id)
            stocks_following = StockFollowing.objects.filter(
                trader=self.request.user.id,)
            queryset = {
                'tradedetails': tradedetails,
                'positions': trade_positions,
                'strategies': strategies,
                'stocks_following': stocks_following,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})
        else:
            return HttpResponseRedirect(reverse('404'))


@login_required
def create_trade(request):
    if request.method == 'POST':
        data = request.POST.copy()
        trader = request.user
        company_name = data.get('name')
        code = data.get('code')
        ts_code = data.get('tsCode')
        market = data.get('market')
        current_price = round(Decimal(data.get('currentPrice')), 2)
        price = round(Decimal(data.get('price')), 2)
        cash = round(Decimal(data.get('cash').replace(',', '')), 2)
        strategy = TradeStrategy.objects.filter(pk=data.get('strategy'))
        quantity = int(data.get('quantity'))
        target_position = data.get('targetPosition')
        direction = data.get('direction')

        new_trade = TradeRec(trader=trader, market=market, stock_name=company_name, stock_code=code, direction=direction, current_price=current_price, price=price,
                             board_lots=quantity, cash=cash, strategy=strategy[0], target_position=target_position)
        new_trade.save()
        # result = StockNameCodeMap.objects.filter(stock_name=stock_name)
        return JsonResponse({'success':_('成功创建交易记录')}, safe=False)

    return JsonResponse({'error':_('无法创建交易记录')}, safe=False)


class TradeRecCreateView(LoginRequiredMixin, FormView):
    # model = TradeRec
    """Basic CreateView implementation to create new articles."""
    model = TradeRec
    message = _('新的交易记录创建成功.')

    def form_valid(self, form):
        user = self.request.user
        # form.instance.user = user
        traderec = form.save(False)
        traderec.trader = user
        traderec.save(True)
        return super().form_valid(form)

# class UserDetailView(LoginRequiredMixin, DetailView):
#     model = User
