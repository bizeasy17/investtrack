import locale
from datetime import date, datetime, timedelta
from decimal import *

import tushare as ts
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, View

from investmgr.models import (Positions, StockFollowing, StockNameCodeMap,
                              TradeAccount, TradeProfitSnapshot, TradeRec,
                              TradeStrategy)

from .forms import UserTradeForm
from .models import User

locale.setlocale( locale.LC_ALL, '' )

# Create your views here.
class UserDashboardView(LoginRequiredMixin, View):
    # form_class = UserTradeForm
    # model = TradeRec

    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'users/dashboard.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'dashboard'

    def get(self, request, *args, **kwargs):
        # username = self.kwargs['username']
        req_user = request.user
        if req_user is not None:
            tradedetails = TradeRec.objects.filter(
                trader=req_user.id, )[:3]  # 前台需要添加view more...
            trade_positions = Positions.objects.filter(
                trader=req_user.id).exclude(lots=0)
            accounts = TradeAccount.objects.filter(trader=req_user.id)
            capital = 0
            profit_loss = 0
            total_accounts = 0
            total_shares = len(trade_positions)
            for acc in accounts:
                capital += acc.account_capital
                profit_loss += acc.account_balance
            total_accounts = len(accounts)
            # update the profit based on the realtime price
            for p in trade_positions:
                p.make_profit_updated()
            strategies = TradeStrategy.objects.filter(creator=req_user.id)
            stocks_following = StockFollowing.objects.filter(
                trader=req_user.id,)[:10]
            queryset = {
                'capital': capital,
                'profit_loss': profit_loss,
                'total_shares': total_shares,
                'total_accounts': total_accounts,
                'total_following': len(stocks_following),
                'total_strategies': len(strategies),
                'details': tradedetails,
                'positions': trade_positions,
                'strategies': strategies,
                'followings': stocks_following,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})
        else:
            return HttpResponseRedirect(reverse('404'))


class UserStockTradeView(LoginRequiredMixin, View):
    # form_class = UserTradeForm
    # model = TradeRec

    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'users/stock_trade.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'trade_info'

    def get(self, request, *args, **kwargs):
        # username = self.kwargs['username']
        req_user = request.user
        trade_type = self.kwargs['type']
        ts_code = self.kwargs['ts_code']
        account = self.kwargs['account']
        if req_user is not None:
            stock_position = Positions.objects.get(
                trader=req_user.id, stock_code=ts_code, trade_account=account)
            # update the profit based on the realtime price
            # stock_position.make_profit_updated()
            strategies = TradeStrategy.objects.filter(creator=req_user.id)
            stock_name = StockNameCodeMap.objects.get(stock_code=ts_code)
            if ts_code[0] == '3':
                market = 'CYB'
                show_code = ts_code + '.SZ'
            elif ts_code[0] == '0':
                market = 'ZXB'
                show_code = ts_code + '.SZ'
            else:
                if ts_code[:3] == '688':
                    market = 'KCB'
                else:
                    market = 'ZB'
                show_code = ts_code + '.SH'

            queryset = {
                'type': trade_type,
                'stock_symbol': ts_code,
                'stock_name': stock_name,
                'show_code': show_code,
                'market': market,
                'account': account,
                'strategies': strategies,
                'position': stock_position,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})
        else:
            return HttpResponseRedirect(reverse('404'))


class UserProfileView(LoginRequiredMixin, DetailView):
    # form_class = UserTradeForm
    # model = TradeRec

    # template_name属性用于指定使用哪个模板进行渲染
    model = User
    template_name = 'users/user_profile.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'user_profile'

    def get_queryset(self, request, *args, **kwargs):
        # username = self.kwargs['username']
        req_user = request.user
        if req_user is not None:
            user = User.objects.filter(
                id=req_user.id,)  # 前台需要添加view more...
            queryset = {
                'user': user,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})


class UserTradeAccountCreateView(LoginRequiredMixin, View):
    # form_class = UserTradeForm
    # model = TradeRec

    # template_name属性用于指定使用哪个模板进行渲染
    model = User
    template_name = 'users/trade_account_create.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'trade_account'

    def get_queryset(self, request, *args, **kwargs):
        # username = self.kwargs['username']
        req_user = request.user
        if req_user is not None:
            user = User.objects.filter(
                id=req_user.id,)  # 前台需要添加view more...
            queryset = {
                'user': user,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})


class UserTradelogView(LoginRequiredMixin, View):
    # form_class = UserTradeForm
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'users/trade_log.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'trade_log'

    def get(self, request, *args, **kwargs):
        # username = self.kwargs['username']
        req_user = request.user
        if req_user is not None:
            tradedetails = TradeRec.objects.filter(
                trader=req_user.id, )[:10]  # 前台需要添加view more...
            trade_positions = Positions.objects.filter(
                trader=req_user.id).exclude(lots=0)[:5]
            strategies = TradeStrategy.objects.filter(creator=req_user.id)
            stocks_following = StockFollowing.objects.filter(
                trader=req_user.id,)
            queryset = {
                'det': tradedetails,
                'pos': trade_positions,
                'str': strategies,
                'fol': stocks_following,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})
        else:
            return HttpResponseRedirect(reverse('404'))

# Create your views here.
@login_required
def get_profit_trend_by_period(request, period):
    if request.method == 'GET':
        trader = request.user
        today = date.today()
        total_profit = 0
        total_profit_prev = 0
        avg_profit = 0
        profit_ratio = 0
        profit_label = []
        profit_trend = []
        previous_profit_trend = []
        max_profit = 0
        if period == 'd':  # 本周收益，按天统计收益
            startDayOfWk = today - timedelta(days=today.weekday())
            endDayOfWk = startDayOfWk + timedelta(days=6)
            profit_qs = TradeProfitSnapshot.objects.filter(
                trader=trader, profit__gt=0).aggregate(sum_profit=Sum('profit'))
            profit_label = [_('周一'), _('周二'), _('周三'), _('周四'), _('周五')]
            profit_trend = [3000, 2000, 4000, 4000, 3000]
            previous_profit_trend = [1000, 2390, 1389, 3500, 2800]
            for p in profit_trend:
                total_profit += p
            for p in previous_profit_trend:
                total_profit_prev += p
            profit_ratio = str(round((total_profit - total_profit_prev) / total_profit * 100,2)) + '%'
            avg_profit = round(total_profit / len(profit_label), 2)
            max_profit = max(profit_trend) if  max(profit_trend) > max(previous_profit_trend) else max(previous_profit_trend)
        elif period == 'm':  # 本月收益，按周统计收益
            startDayOfMth = today - timedelta(days=today.weekday())
            endDayOfMth = startDayOfMth + timedelta(days=6)
            profit_label = [_('第一周'), _('第二周'), _('第三周'), _('第四周'), _('第五周')]
        else: # 本年收益，按月统计收益
            startDayOfYear = today - timedelta(days=today.weekday())
            endDayOfYear = startDayOfYear + timedelta(days=6)
            profit_label = [_('一月'), _('二月'), _(
                '三月'), _('四月'), _('五月'), _('六月')]
        
        if True:
            return JsonResponse(
                {
                    'code': 'OK',
                    'max_profit': max_profit,
                    'total_profit': total_profit,
                    'avg_profit': locale.currency(avg_profit, grouping=True),
                    'profit_ratio': profit_ratio,
                    'label': profit_label,
                    'profit_trend': profit_trend,
                    'previous_profit_trend': previous_profit_trend,
                }, safe=False)
        else:
            return JsonResponse({'code': 'NULL'}, safe=False)

@login_required
def get_invest_success_attempt_by_period(request, period):
    if request.method == 'GET':
        trader = request.user
        today = date.today()
        total_attempt = 0
        total_attempt_prev = 0
        avg_attempt = 0
        relative_ratio = 0
        label = []
        attempt_trend = []
        prev_attempt_trend = []
        max_attempt = 0
        if period == 'd':  # 本周收益，按天统计收益
            startDayOfWk = today - timedelta(days=today.weekday())
            endDayOfWk = startDayOfWk + timedelta(days=6)
            # profit_qs = TradeProfitSnapshot.objects.filter(
            #     trader=trader, profit__gt=0).aggregate(sum_profit=Sum('profit'))
            label = [_('周一'), _('周二'), _('周三'), _('周四'), _('周五')]
            attempt_trend = [3, 1, 0, 3, 1]
            prev_attempt_trend = [1, 0, 1, -1, 3]
            for p in attempt_trend:
                total_attempt += p
            for p in prev_attempt_trend:
                total_attempt_prev += p
            relative_ratio = str(
                round((total_attempt - total_attempt_prev) / total_attempt * 100, 2)) + '%'
            avg_attempt = round(total_attempt / len(label), 2)
            max_attempt = max(attempt_trend) if max(attempt_trend) > max(
                prev_attempt_trend) else max(prev_attempt_trend)
        elif period == 'm':  # 本月收益，按周统计收益
            startDayOfMth = today - timedelta(days=today.weekday())
            endDayOfMth = startDayOfMth + timedelta(days=6)
            profit_label = [_('第一周'), _('第二周'), _('第三周'), _('第四周'), _('第五周')]
        else: # 本年收益，按月统计收益
            startDayOfYear = today - timedelta(days=today.weekday())
            endDayOfYear = startDayOfYear + timedelta(days=6)
            profit_label = [_('一月'), _('二月'), _(
                '三月'), _('四月'), _('五月'), _('六月')]
        
        if True:
            return JsonResponse(
                {
                    'code': 'OK',
                    'label': label,
                    'max_attempt': max_attempt,
                    'total_attempt': total_attempt,
                    'avg_attempt': avg_attempt,
                    'relative_ratio': relative_ratio,
                    'attempt_trend': attempt_trend,
                    'prev_attempt_trend': prev_attempt_trend,
                }, safe=False)
        else:
            return JsonResponse({'code': 'NULL'}, safe=False)

@login_required
def get_position_status(request, account, symbol):
    if request.method == 'GET':
        trader = request.user
        # account = TradeAccount(account_id)
        pos_label = []
        target_pos = []
        available_pos = []
        total_avail = 0
        total_target = 0
        total_percentage = ''
        if account == "a":
            if symbol == 'a': # 取所有持仓信息
                pos_qs = Positions.objects.filter(
                    trader=trader, is_liquadated=False)
            else:
                symbol_list = list(symbol.split(','))
                pos_qs = Positions.objects.filter(
                    trader=trader, stock_code__in=symbol_list, is_liquadated=False)
            for pos in pos_qs:
                pos_label.append(pos.stock_name)
                target_pos.append(pos.target_position * pos.position_price)
                available_pos.append(pos.lots * pos.position_price)
                total_target += pos.target_position
                total_avail += pos.lots
        else:
            if symbol == 'a':
                pos_qs = Positions.objects.filter(
                    trader=trader, trade_account=account, is_liquadated=False)
            else:
                symbol_list = list(symbol.split(','))
                pos_qs = Positions.objects.filter(
                    trader=trader, trade_account=account, stock_code__in=symbol_list, is_liquadated=False)
            for pos in pos_qs:
                pos_label.append(pos.stock_name)
                target_pos.append(pos.target_position * pos.position_price)
                available_pos.append(pos.lots * pos.position_price)
                total_target += pos.target_position
                total_avail += pos.lots
        total_percentage = str(round(total_avail / total_target, 2) * 100) + '%'
        if len(pos_qs) > 0:
            return JsonResponse(
                {
                    'code': 'OK', 
                    'total_percentage': total_percentage,
                    'label': pos_label,
                    'target_position': target_pos, 
                    'available_position': available_pos,
                }, safe=False)
        else:
            return JsonResponse({'code': 'NULL'}, safe=False)


@login_required
def get_stock_for_trade(request, account, stock_code):
    if request.method == 'GET':
        req_user = request.user
        # 获得实时报价
        realtime_df = ts.get_realtime_quotes(
            str(stock_code))  # 需要再判断一下ts_code
        realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                                   'high', 'low', 'bid', 'ask', 'volume', 'amount', 'time']]
        realtime_price = Decimal(round(realtime_df['price'].mean(), 2))
        realtime_bid = Decimal(round(realtime_df['bid'].mean(), 2))
        realtime_pre_close = Decimal(round(realtime_df['pre_close'].mean(), 2))
        if realtime_price != 0.00:
            realtime_price = round(realtime_price, 2)
        elif realtime_bid != 0.00:
            realtime_price = round(realtime_bid, 2)
        else:
            realtime_price = round(realtime_pre_close, 2)
        stock_position = Positions.objects.filter(
            trader=req_user.id, stock_code=stock_code, trade_account=account)
        account = TradeAccount.objects.filter(id=account)
        if account is not None and len(account) == 1:
            remain_to_buy = round(
                account[0].account_balance / realtime_price, 0)
        else:
            remain_to_buy = 0
        if len(str(remain_to_buy)) > 2:
            remain_to_buy = int(str(remain_to_buy)[:-2]) * 100
        else:
            remain_to_buy = 0
        if stock_position is not None and len(stock_position) == 1:
            remain_to_sell = stock_position[0].lots
            target_cash_amount = round(
                stock_position[0].target_position * realtime_price, 0)
            target_position = stock_position[0].target_position
        else:
            remain_to_sell = 0
            target_position = 0
            target_cash_amount = 0
        data = {
            'current_price': realtime_price,
            'target_position': target_position,
            'target_cash_amount': target_cash_amount,
            'remain_to_buy': remain_to_buy,
            'remain_to_sell': remain_to_sell,
        }
    return JsonResponse(data, safe=False)


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
        trade_time = data.get('tradeTime')
        trade_account_id = data.get('tradeAcc')

        new_trade = TradeRec(trader=trader, market=market, stock_name=company_name, stock_code=code, direction=direction, current_price=current_price, price=price,
                             board_lots=quantity, lots_remain=quantity, cash=cash, strategy=strategy[
                                 0],
                             target_position=target_position, trade_time=datetime.strptime(
                                 trade_time, '%Y-%m-%d %H:%M'),
                             created_or_mod_by='human', trade_account=TradeAccount(id=trade_account_id))
        # if direction == 'b':
        is_ok = new_trade.save()
        # else:
        #     # 卖出操作需要split买入的先前持仓
        #     new_trade.allocate_stock_for_sell()
        # result = StockNameCodeMap.objects.filter(stock_name=stock_name)
        if is_ok:
            return JsonResponse({'success': _('交易成功')}, safe=False)
        else:
            return JsonResponse({'success': _('交易失败')}, safe=False)

    return JsonResponse({'error': _('交易失败')}, safe=False)


@login_required
def refresh_position(request):
    if request.method == 'GET':
        trader = request.user
        my_position = Positions.objects.find(trader=trader).update()
        return JsonResponse(my_position, safe=False)

    return JsonResponse({'code': 'error', 'message': _('系统错误，请稍后再试')}, safe=False)


@login_required
def get_position_by_symbol(request, account_id, symbol):
    if request.method == 'GET':
        trader = request.user
        # account = TradeAccount(account_id)
        pos_qs = Positions.objects.filter(
            trader=trader, trade_account=account_id, stock_code=symbol, is_liquadated=False)
        my_pos = {}
        if len(pos_qs) > 0:
            my_pos = {
                'stock_name': pos_qs[0].stock_name,
                'stock_symbol': pos_qs[0].stock_code,
                'trade_account': pos_qs[0].trade_account.account_name,
                'profit': pos_qs[0].profit,
                'profit_ratio': pos_qs[0].profit_ratio,
                'current_price': pos_qs[0].current_price,
                'cost': pos_qs[0].position_price,
                'lots': pos_qs[0].lots,
                'target_position': pos_qs[0].target_position,
                'capital': pos_qs[0].cash,
            }
        if len(my_pos) > 0:
            return JsonResponse({'code': 'OK', 'content': my_pos}, safe=False)
        else:
            return JsonResponse({'code': 'NULL'}, safe=False)

    return JsonResponse({'code': 'ERR', 'content': _('系统错误，请稍后再试')}, safe=False)

# class UserDetailView(LoginRequiredMixin, DetailView):
#     model = User

# custom 404, 403, 500 pages


def my_custom_page_not_found_view(request, exception):
     # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'pages/404.html'
    return render(request, template_name)
