from decimal import *
from datetime import datetime
import tushare as ts
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, DetailView, FormView, ListView

from investmgr.models import (Positions, StockNameCodeMap, TradeRec,
                              TradeStrategy, StockFollowing, TradeAccount)

from .forms import UserTradeForm
from .models import User


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
                trader=req_user.id, )[:5]  # 前台需要添加view more...
            trade_positions = Positions.objects.filter(
                trader=req_user.id).exclude(lots=0)[:8]
            # update the profit based on the realtime price
            for p in trade_positions:
                p.make_profit_updated()
            strategies = TradeStrategy.objects.filter(creator=req_user.id)
            stocks_following = StockFollowing.objects.filter(
                trader=req_user.id,)[:10]
            queryset = {
                'capital': 1000,
                'profit_loss': 15000,
                'total_shares': 8,
                'total_accounts': 3,
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
            stock_position = Positions.objects.get(trader=req_user.id,stock_code=ts_code,trade_account=account)
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
                id=req_user.id,)# 前台需要添加view more...
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
        if account is not None and len(account)==1:
            remain_to_buy = round(account[0].account_balance / realtime_price,0)
        else:
            remain_to_buy = 0
        if len(str(remain_to_buy)) > 2:
            remain_to_buy = int(str(remain_to_buy)[:-2]) * 100
        else:
            remain_to_buy = 0
        if stock_position is not None and len(stock_position)==1:
            remain_to_sell = stock_position[0].lots
            target_cash_amount = round(stock_position[0].target_position * realtime_price, 0)
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
                             board_lots=quantity, lots_remain=quantity, cash=cash, strategy=strategy[0], 
                             target_position=target_position, trade_time=datetime.strptime(trade_time, '%Y-%m-%d %H:%M'), 
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

    return JsonResponse({'code':'error', 'message': _('系统错误，请稍后再试')}, safe=False)


@login_required
def get_position_by_code(request, code):
    if request.method == 'GET':
        trader = request.user
        my_position = Positions.objects.find(trader=trader, stock_code=code)
        return JsonResponse(my_position, safe=False)

    return JsonResponse({'code': 'error', 'message': _('系统错误，请稍后再试')}, safe=False)

# class UserDetailView(LoginRequiredMixin, DetailView):
#     model = User

# custom 404, 403, 500 pages

def my_custom_page_not_found_view(request, exception):
     # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'pages/404.html'
    return render(request, template_name)
