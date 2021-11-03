import logging

import numpy as np
from analysis.models import StockHistoryDaily
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (Http404, HttpResponse, HttpResponseRedirect,
                         HttpResponseServerError, JsonResponse)
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.views import APIView
from stockmarket.models import (City, CompanyDailyBasic, Industry, Province,
                                StockNameCodeMap)
from stockmarket.serializers import (CompanyDailyBasicExt,
                                     CompanyDailyBasicExtSerializer)
from stockmarket.utils import get_stocknames
from users.models import UserActionTrace, UserQueryTrace

from investors.models import StockFollowing, TradeStrategy


class XuanguView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'investors/xuangu.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'xuangu'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        if req_user is not None:
            # company = StockNameCodeMap.objects.filter(
            #     ts_code='')
            provinces = Province.objects.annotate(count_num=Count('city_province')).values(
                'name', 'count_num').order_by('-count_num')[0:6]
            industries = Industry.objects.annotate(count_num=Count('company_ind')).values(
                'industry', 'count_num').order_by('-count_num')[0:4]
            industries_more = Industry.objects.annotate(count_num=Count('company_ind')).values(
                'industry', 'count_num').order_by('-count_num')[5:]
            # city = City.objects.annotate(filter(ts_code='')
            queryset = {
                'provinces': provinces,
                'industries': industries,
                'ind_more': industries_more,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})


class CompanyHistoryDailyBasicList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, filters, start_idx, end_idx):
        '''
        filters - 板块，区域，城市，行业，PE，PB，PS
        step 1. 板块
        step 2. 区域
        step 3. 城市
        step 4. 行业
        step 5. PE > PB > PS
        '''
        filter_list = filters.split(',')
        cdbext_list = []
        try:
            if filter_list[0] == '3':
                my_stocks = StockNameCodeMap.objects.filter(
                    ts_code__startswith='3').order_by('-ts_code')
            elif filter_list[0] == '688':
                my_stocks = StockNameCodeMap.objects.filter(
                    ts_code__startswith='688').order_by('-ts_code')
            elif filter_list[0] == '0':
                my_stocks = StockNameCodeMap.objects.filter(
                    ts_code__startswith='0').order_by('-ts_code')
            elif filter_list[0] == '60':
                my_stocks = StockNameCodeMap.objects.filter(
                    ts_code__startswith='60').order_by('-ts_code')
            else:
                my_stocks = StockNameCodeMap.objects.all().order_by('-ts_code')

            # 省份过滤
            if filter_list[1] != '0':
                my_stocks = my_stocks.filter(
                    company_basic__province=filter_list[1])
            # 城市过滤
            if filter_list[2] != '0':
                my_stocks = my_stocks.filter(
                    company_basic__city=filter_list[2])
            # 行业
            if filter_list[3] != '0':
                my_stocks = my_stocks.filter(
                    ind__industry=filter_list[3])

                # get basic from industry table
                ind = Industry.objects.get(industry=filter_list[3])

            else:  # 无行业过滤器
                # industries = Industry.objects.all()

                # for ind in industries:
                #     company_basic = ind.company_ind.company_basic.filter(pe__lte=ind.pe_10pct*1.1)
                # my_stocks = my_stocks.filter(
                #     ind__industry=filter_list[3])
                pass

            my_stocks = my_stocks[start_idx:end_idx]

            for stock in my_stocks:
                db = stock.get_latest_daily_basic()
                dc = stock.get_latest_history()

                if db is None or dc is None:
                    continue

                if filter_list[3] != '0':
                    # PE高低过滤
                    # if filter_list[4] != 0:
                    if filter_list[4] == '-1':  # 亏损
                        if not np.isnan(db.pe):
                            continue
                    elif filter_list[4] == '1':  # low
                        if np.isnan(db.pe) or db.pe > ind.pe_10pct * 1.1:
                            continue
                    elif filter_list[4] == '2':  # med
                        if np.isnan(db.pe) or (db.pe > ind.pe_50pct * 1.2 or db.pe < ind.pe_50pct * 0.8):
                            continue
                    elif filter_list[4] == '3':  # high
                        if np.isnan(db.pe) or db.pe < ind.pe_90pct * 0.9:
                            continue

                    # PB高低过滤
                    if filter_list[5] == '1':
                        if db.pb > ind.pb_10pct * 1.1:
                            continue
                    elif filter_list[5] == '2':
                        if db.pb > ind.pb_50pct * 1.2 or db.pb < ind.pb_50pct * 0.8:
                            continue
                    elif filter_list[5] == '3':
                        if db.pb < ind.pb_90pct * 0.9:
                            continue

                    # PS高低过滤
                    if filter_list[6] == '1':
                        if db.ps > ind.ps_10pct * 1.1:
                            continue
                    elif filter_list[6] == '2':
                        if db.ps > ind.ps_50pct * 1.2 or db.ps < ind.ps_50pct * 0.8:
                            continue
                    elif filter_list[6] == '3':
                        if db.ps < ind.ps_90pct * 0.9:
                            continue

                cdbext = CompanyDailyBasicExt(ts_code=stock.ts_code, stock_name=stock.stock_name, industry=stock.industry, pe=db.pe, pe_ttm=db.pe_ttm, ps=db.ps,
                                              ps_ttm=db.ps_ttm, pb=db.pb, close=db.close, chg_pct=dc.pct_chg, total_mv=db.total_mv, trade_date=dc.trade_date)

                cdbext_list.append(cdbext)

            serializer = CompanyDailyBasicExtSerializer(
                cdbext_list, many=True)
            # serializer.fields = basic_type.split(',')
            return Response(serializer.data)
        except CompanyDailyBasic.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


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
