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

from investors.models import StockFollowing, TradeStrategy
from stockmarket.models import StockNameCodeMap
# from stocktrade.models import Transactions
# from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
# from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.analysis_jiuzhuan_cp import mark_jiuzhuan
from analysis.strategy_test_pct import test_exp_pct
from analysis.strategy_test_period import test_by_period
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

class QueryAnalyzerView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'siteadmin/query-analyzer.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'query_analyzer'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        if req_user is not None and req_user.is_superuser:
            positions = Positions.objects.filter()[:10]
            queryset = {
                'positions': positions,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})

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
def get_transaction_detail(request, id):
    if request.method == 'GET':
        req_user = request.user
        if req_user is not None:
            if req_user.is_superuser:
                recs_json = []
                trade_recs = Transactions.objects.filter(
                    in_stock_positions_id=id).exclude(created_or_mod_by='system').order_by('-trade_time')
                recs_json = traderec2json(trade_recs)
                return JsonResponse({'code': 'ok', 'content': recs_json}, safe=False)
            # workaround for use the function for normal user
            else:
                recs_json = []
                trade_recs = Transactions.objects.filter(trader=req_user.id,
                                                     in_stock_positions_id=id).exclude(created_or_mod_by='system').order_by('-trade_time')
                recs_json = traderec2json(trade_recs)
                return JsonResponse({'code': 'ok', 'content': recs_json}, safe=False)

    return JsonResponse({'code': 'error', 'message': _('数据获取失败或未授权')}, safe=False)


@login_required
def get_transaction_detail_breakdown(request, id, ref_num):
    if request.method == 'GET':
        req_user = request.user
        if req_user is not None and req_user.is_superuser:
            recs_json = []
            trade_recs = Transactions.objects.filter(
                rec_ref_number=ref_num).exclude(id=id).exclude(direction='s').order_by('-trade_time')
            recs_json = traderec2json(trade_recs)
            return JsonResponse({'code': 'ok', 'content': recs_json}, safe=False)
    return JsonResponse({'code': 'error', 'message': _('数据获取失败或未授权')}, safe=False)


@login_required
def get_transaction_detail_pkd(request, ref_id):
    if request.method == 'GET':
        site_admin = request.user
        if site_admin is not None and site_admin.is_superuser:
            recs_json = []
            trade_recs = Transactions.objects.filter(
                sell_stock_refer_id=ref_id).exclude(created_or_mod_by='human').order_by('-trade_time')
            recs_json = traderec2json(trade_recs)
            return JsonResponse({'code': 'ok', 'content': recs_json}, safe=False)
    return JsonResponse({'code': 'error', 'message': _('数据获取失败或未授权')}, safe=False)


def sync_stock_price_for_investor(position_pk, realtime_quotes=[]):
    '''
    将持仓股的价格更新到最新报价
    '''
    if len(realtime_quotes) > 0:
        linked_traderecs = Transactions.objects.select_for_update().filter(
            in_stock_positions=position_pk)
        with transaction.atomic():
            for entry in linked_traderecs:
                entry.current_price = realtime_quotes[entry.stock_code]
                entry.save()


def sync_stock_position_for_investor(investor):
    '''
    根据stock_symbol更新最新的价格
    '''
    stock_symbols = []
    latest_positions = []
    realtime_quotes = []
    in_stock_positions = Positions.objects.select_for_update().filter(
        trader=investor).exclude(is_liquidated=True,)
    with transaction.atomic():
        for entry in in_stock_positions:
            # entry.make_profit_updated(realtime_quotes[entry.stock_code])
            # sync_stock_price_for_investor(entry.pk, realtime_quotes)
            calibrate_realtime_position(entry)
            latest_positions.append(
                {
                    'id': entry.pk,
                    'symbol': entry.stock_code,
                    'name': entry.stock_name,
                    'position_price': entry.position_price,
                    'realtime_price': entry.current_price,
                    'profit': entry.profit,
                    'profit_ratio': entry.profit_ratio,
                    'lots': entry.lots,
                    'target_position': entry.target_position,
                    'amount': entry.cash,
                }
            )
    return latest_positions


def take_account_snapshot(invest_account):
    today = date.today()
    # 判断是否存在snapshot
    snapshots = TradeAccountSnapshot.objects.filter(
        trade_account=invest_account, snap_date=today)
    if snapshots is not None and not snapshots.exists():
        snapshot = TradeAccountSnapshot(
            trade_account=invest_account, snap_date=today)
        snapshot.take_account_snapshot()


@login_required
def take_snapshot_manual(request):
    '''
    生成snapshot的流程
    1. 获得有效的用户，
    2. 根据用户获得所有持仓（未清仓）
    3. 获得最新报价，更新持仓和交易记录
    4. 根据最新持仓信息更新交易账户余额
    5. 生成账户快照
    - 本金
    - 余额
    - 变化？
    - 比率？
    - 日期
    - 周期 d - 每日，w - 每周周五?，y - 每月最后一个周五?
    '''
    if request.method == 'GET':
        site_admin = request.user
        if site_admin is not None and site_admin.is_superuser:
            latest_positions = {}
            # 1. 获得有效的用户，
            investors = User.objects.filter(
                is_active=True).exclude(is_superuser=True)
            if investors is not None and len(investors):
                for investor in investors:
                    # 2. 根据用户获得所有持仓（未清仓）
                    # 3. 获得最新报价，更新持仓和交易记录
                    sync_stock_position_for_investor(
                        investor)
                    # 4. 根据最新持仓信息更新交易账户余额
                    accounts = TradeAccount.objects.filter(trader=investor)
                    for account in accounts:
                        account.update_account_balance()
                        # 5. 生成账户快照
                        take_account_snapshot(account)
        return JsonResponse({'code': 'ok', 'message': _('账户快照生成成功')}, safe=False)
    return JsonResponse({'code': 'error', 'message': _('系统错误或未授权')}, safe=False)


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

def jiuzhuan_test(request, stock_symbol, start_date, freq):
    # end_date = date.today()
    start_date = datetime.strptime(start_date, '%Y%m%d')
    symbol_list = stock_symbol.split(',')
    res = mark_jiuzhuan(freq, symbol_list)
    if res:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)

# def dingdi_test(request, stock_symbol, freq):
#     # end_date = date.today()
#     symbol_list = stock_symbol.split(',')
#     res = mark_dingdi_listed(freq, symbol_list)
#     if res:
#         return HttpResponse(status=200)
#     else:
#         return HttpResponse(status=500)

@login_required
def bstrategy_test_by_period(request,  strategy, stock_symbol, test_period):
    user = request.user
    if request.method == 'GET':
        try:
            symbol_list = stock_symbol.split(',')
            test_by_period(strategy, symbol_list)
            return HttpResponse(status=200)
        except Exception as e:
            logging.error(e)
            return HttpResponse(status=500)


@login_required
def bstrategy_exp_pct_test(request,  strategy, stock_symbol, test_freq):
    user = request.user
    if request.method == 'GET':
        try:
            if stock_symbol != 'all':
                symbol_list = stock_symbol.split(',')
                if len(symbol_list) > 0:
                    test_exp_pct(strategy, symbol_list, test_freq)
            else:
                test_exp_pct(strategy, test_freq=test_freq)
            return HttpResponse(status=200)
        except Exception as e:
            logging.error(e)
            return HttpResponse(status=500)
