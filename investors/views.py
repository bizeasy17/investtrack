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

@login_required
def stocks_following(request):
    if request.method == 'GET':
        try:
            stock_list = []
            investor = request.user
            following = StockFollowing.objects.filter(trader=investor)
            if following is not None and len(following) > 0:
                for stock in following:
                    stock_list.append(stock.stock_code)
                return JsonResponse({'results':stock_list}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as e:
            print(e)
            return HttpResponse(status=500)
