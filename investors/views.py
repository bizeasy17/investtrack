import logging
from stockmarket.models import StockNameCodeMap

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from investors.models import StockFollowing, TradeStrategy
from stockmarket.utils import get_stocknames


class KanpanView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'investors/kanpan.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'kanpan'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        if req_user is not None:
            stocks_following = StockFollowing.objects.filter(
                trader=req_user.id,)
            queryset = {
                'followings': stocks_following,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})


class LinechartView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'investors/linechart.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'linechart'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        if req_user is not None:
            return render(request, self.template_name)


# Create your views here.
@login_required
def follow_stock(request, symbol):
    if request.method == 'POST':
        # data = request.POST.copy()
        name = get_stocknames([symbol])[symbol]  # data.get('name')
        investor = request.user
        try:
            stk_basic = StockNameCodeMap.objects.get(ts_code=symbol)
            new_follow = StockFollowing(trader=investor, stock_code=symbol.split('.')[0], stock_name=name, industry=stk_basic.industry,
                                        area=stk_basic.area, fullname=stk_basic.fullname, ts_code=stk_basic.ts_code)
            new_follow.save()
            return JsonResponse({'code': 'aok', 'message': _('添加成功')}, safe=False)
        except Exception as err:
            return JsonResponse({'code': 'error', 'message': _('添加失败')}, safe=False)


@login_required
def unfollow_stock(request, symbol):
    if request.method == 'DELETE':
        investor = request.user
        following = StockFollowing.objects.filter(
            trader=investor, ts_code=symbol)
        following.delete()
        return JsonResponse({'code': 'dok', 'message': _('删除成功')}, safe=False)
    return JsonResponse({'code': 'error', 'message': _('删除失败')}, safe=False)


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
                return JsonResponse({'results': stock_list}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as e:
            print(e)
            return HttpResponse(status=500)


@login_required
def get_trade_account(request):
    if request.method == 'GET':
        try:
            stock_list = []
            investor = request.user
            following = StockFollowing.objects.filter(trader=investor)
            if following is not None and len(following) > 0:
                for stock in following:
                    stock_list.append(stock.stock_code)
                return JsonResponse({'results': stock_list}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as e:
            print(e)
            return HttpResponse(status=500)
