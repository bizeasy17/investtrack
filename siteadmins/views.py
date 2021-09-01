import logging
import pytz
from datetime import date, datetime

import tushare as ts
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, TemplateView, View

from investors.models import StockFollowing
from stockmarket.models import StockNameCodeMap
# from stocktrade.models import Transactions
# from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
# from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
# from analysis.analysis_dingdi import mark_dingdi_listed


logger = logging.getLogger(__name__)

# Create your views here.

class DashboardView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'siteadmin/dashboard.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'dashboard'

class SettingsView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'siteadmin/settings.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'settings'

class StrategyMgmtView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'siteadmin/strategy_mgmt.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'strategy'

def traderec2json(trade_records):
    recs_json = []
    if trade_records is not None and trade_records.count() > 0:
        for trade_rec in trade_records:
            recs_json.append(
                {
                    'id': trade_rec.id,
                    'symbol': trade_rec.stock_code,
                    'name': trade_rec.stock_name,
                    'direction': trade_rec.direction,
                    'price': trade_rec.price,
                    'shares': trade_rec.board_lots,
                    'current_price': trade_rec.current_price,
                    'amount': trade_rec.cash,
                    'account': trade_rec.trade_account.account_name,
                    'is_sold': trade_rec.is_sold,
                    'sell_ref': trade_rec.sell_stock_refer_id,
                    'sold_price': trade_rec.sell_price,
                    'refer_number': trade_rec.rec_ref_number,
                    'lots_remain': trade_rec.lots_remain,
                    'sold_time': trade_rec.sold_time,
                    'trade_time': trade_rec.trade_time,
                }
            )
    return recs_json


@login_required
def sync_company_list(request):
    if request.method == 'GET':
        try:
            pro = ts.pro_api()

            # 查询当前所有正常上市交易的股票列表
            data = pro.stock_basic(exchange='', list_status='',
                                   fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,list_status,list_date,delist_date,is_hs')
            company_list = StockNameCodeMap.objects.all()
            if data is not None and len(data) > 0:
                if company_list.count() != len(data):
                    for v in data.values:
                        try:
                            if str(v[1])[0] == '3':
                                v[7] = 'CYB'
                            elif str(v[1])[0] == '0':
                                v[7] = 'ZXB'
                            else:
                                if str(v[1])[:3] == '688':
                                    v[7] = 'KCB'
                                else:
                                    v[7] = 'ZB'
                            company_list =  StockNameCodeMap.objects.get(ts_code=v[0])
                            company_list.stock_name = v[2]
                            company_list.list_status = v[9]
                            company_list.delist_date = v[11]
                        except Exception as e:
                            # cn_tz = pytz.timezone("Asia/Shanghai")
                            company_list = StockNameCodeMap(ts_code=v[0], stock_code=v[1], stock_name=v[2], area=v[3],
                                                            industry=v[4], fullname=v[5], en_name=v[6], market=v[7], exchange=v[8],
                                                            list_status=v[9], list_date=datetime.strptime(v[10], '%Y%m%d'), delist_date=v[11],
                                                            is_hs=v[12])
                        company_list.save()
            # result = StockNameCodeMap.objects.filter(stock_name=stock_name)
            return JsonResponse({'success': _('公司信息同步成功')}, safe=False)
        except Exception as e:
            logger.error(e)
    return JsonResponse({'error': _('无法创建交易记录')}, safe=False)


# def dingdi_test(request, stock_symbol, freq):
#     # end_date = date.today()
#     symbol_list = stock_symbol.split(',')
#     res = mark_dingdi_listed(freq, symbol_list)
#     if res:
#         return HttpResponse(status=200)
#     else:
#         return HttpResponse(status=500)



