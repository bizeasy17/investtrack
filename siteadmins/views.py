from datetime import date, datetime

import tushare as ts
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, View

from investmgr import utils
from investmgr.models import TradeRec, Positions, TradeProfitSnapshot, TradeAccount
from users.models import User


# Create your views here.
class SiteAdminGenericView(LoginRequiredMixin, View):
    # form_class = UserTradeForm
    # model = TradeRec

    # template_name属性用于指定使用哪个模板进行渲染
    default_template_name = 'siteadmin/dashboard.html'
    site_settings_template_name = 'siteadmin/settings.html'
    site_query_analyzer_template_name = 'siteadmin/query_analyzer.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'site_admin'

    def get(self, request, *args, **kwargs):
        module_name = self.kwargs['module_name']
        req_user = request.user
        if req_user is not None and req_user.is_superuser:
            if module_name is not None:
                if module_name == 'dashboard':
                    return render(request, self.default_template_name)
                elif module_name == 'settings':
                    return render(request, self.site_settings_template_name)
                elif module_name == 'query-analyzer':
                    positions = Positions.objects.filter()[:10]
                    queryset = {
                        'positions': positions,
                    }
                    return render(request, self.site_query_analyzer_template_name, {self.context_object_name: queryset})
                else:
                    return render(request, self.default_template_name)
        else:
            return HttpResponseRedirect(reverse('404'))


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
        recs_json = []
        trade_recs = TradeRec.objects.filter(
            in_stock_positions_id=id).exclude(created_or_mod_by='system')
        recs_json = traderec2json(trade_recs)
        return JsonResponse({'code': 'ok', 'content': recs_json}, safe=False)
    return JsonResponse({'code': 'error', 'message': _('数据获取失败')}, safe=False)


@login_required
def get_transaction_detail_breakdown(request, id, ref_num):
    if request.method == 'GET':
        recs_json = []
        trade_recs = TradeRec.objects.filter(
            rec_ref_number=ref_num).exclude(id=id).exclude(direction='s')
        recs_json = traderec2json(trade_recs)
        return JsonResponse({'code': 'ok', 'content': recs_json}, safe=False)
    return JsonResponse({'code': 'error', 'message': _('数据获取失败')}, safe=False)


@login_required
def get_transaction_detail_pkd(request, ref_id):
    if request.method == 'GET':
        recs_json = []
        trade_recs = TradeRec.objects.filter(
            sell_stock_refer_id=ref_id).exclude(created_or_mod_by='human')
        recs_json = traderec2json(trade_recs)
        return JsonResponse({'code': 'ok', 'content': recs_json}, safe=False)
    return JsonResponse({'code': 'error', 'message': _('数据获取失败')}, safe=False)


def sync_stock_price_for_investor(position_pk, realtime_quotes=[]):
    '''
    将持仓股的价格更新到最新报价
    '''
    if len(realtime_quotes) > 0:
        linked_traderecs = TradeRec.objects.select_for_update().filter(
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
    # in_stock_symbols = Positions.objects.filter(trader=investor).exclude(is_liquadated=True,).distinct().values('stock_code')
    # if in_stock_symbols is not None and len(in_stock_symbols) > 0:
    #     for stock_symbol in in_stock_symbols:
    #         stock_symbols.append(stock_symbol['stock_code'])

    in_stock_positions = Positions.objects.select_for_update().filter(
        trader=investor).exclude(is_liquadated=True,)
    with transaction.atomic():
        if in_stock_positions is not None and len(in_stock_positions) > 0:
            for position in in_stock_positions:
                stock_symbols.append(position.stock_code)
            realtime_quotes = utils.get_realtime_price(
                list(set(stock_symbols)))
        for entry in in_stock_positions:
            entry.make_profit_updated(realtime_quotes[entry.stock_code])
            sync_stock_price_for_investor(entry.pk, realtime_quotes)
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
    snapshots = TradeProfitSnapshot.objects.filter(
        trade_account=invest_account, snap_date=today)
    if snapshots is not None and not snapshots.exists():
        snapshot = TradeProfitSnapshot(
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
    return JsonResponse({'code': 'error', 'message': _('系统错误，请稍后再试')}, safe=False)
