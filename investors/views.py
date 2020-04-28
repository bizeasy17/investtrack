import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from investors.models import StockFollowing, TradeStrategy


# Create your views here.
@login_required
def follow_stock(request, symbol):
    if request.method == 'POST':
        data = request.POST.copy()
        name = data.get('name')
        investor = request.user
        new_follow = StockFollowing(trader=investor, stock_code=symbol, stock_name=name)
        new_follow.save()
        return JsonResponse({'code': 'ok', 'message': _('添加成功')}, safe=False)
    return JsonResponse({'code': 'error', 'message': _('添加失败')}, safe=False)
