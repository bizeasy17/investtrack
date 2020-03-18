import decimal
import locale
import os
# from calendar import monthrange
import calendar
import datedelta
from datetime import timedelta
import datetime

import tushare as ts
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
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

locale.setlocale(locale.LC_ALL, '')

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
                trader=req_user.id).exclude(is_liquadated=True).order_by('-last_mod_time')
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
                'trade_accounts': accounts,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})
        else:
            return HttpResponseRedirect(reverse('404'))


class UserRecordStockTradeView(LoginRequiredMixin, View):
    # form_class = UserTradeForm
    # model = TradeRec

    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'users/stock_trade.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'trade_info'

    def get(self, request, *args, **kwargs):
        # username = self.kwargs['username']
        req_user = request.user
        trade_type = 'b'  # default trade type is buy. self.kwargs['type']
        stock_symbol = self.kwargs['symbol']
        account_id = self.kwargs['account']
        trade_account = TradeAccount.objects.filter(id=account_id)
        if req_user is not None:
            strategies = TradeStrategy.objects.filter(creator=req_user.id)
            stock_position = []
            stock_name = ''
            if trade_account is None or len(trade_account) < 1:
                show_code = '1A0001'
                market = 'ZB'
                stock_name = '上证指数'
            else:
                if stock_symbol == 'sh':
                    # 默认上证指数，如果不指定股票编号
                    show_code = '1A0001'
                    market = 'ZB'
                    stock_name = '上证指数'
                else:
                    symbol_map = StockNameCodeMap.objects.filter(
                        stock_code=stock_symbol)
                    if symbol_map is None or len(symbol_map) == 0:
                        # 如果传入的股票代码不存在，默认上证指数，如果不指定股票编号
                        stock_symbol = 'sh'
                        show_code = '1A0001'
                        market = 'ZB'
                        stock_name = '上证指数'
                    else:
                        stock_position = Positions.objects.filter(
                            trader=req_user.id, stock_code=stock_symbol, trade_account=account_id)
                        # update the profit based on the realtime price
                        # stock_position.make_profit_updated()
                        stock_name = symbol_map[0].stock_name
                        if stock_symbol[0] == '3':
                            market = 'CYB'
                            show_code = stock_symbol + '.SZ'
                        elif stock_symbol[0] == '0':
                            market = 'ZXB'
                            show_code = stock_symbol + '.SZ'
                        else:
                            if stock_symbol[:3] == '688':
                                market = 'KCB'
                            else:
                                market = 'ZB'
                            show_code = stock_symbol + '.SH'

            queryset = {
                'type': trade_type,
                'stock_symbol': stock_symbol,
                'stock_name': stock_name,
                'show_code': show_code,
                'market': market,
                'account_id': account_id,
                'trade_account': trade_account[0] if len(trade_account) >= 1 else None,
                'strategies': strategies,
                'position': stock_position[0] if len(stock_position) >= 1 else None,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})
        else:
            return HttpResponseRedirect(reverse('404'))


class UserProfileView(LoginRequiredMixin, View):
    # form_class = UserTradeForm
    # model = TradeRec

    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'users/user_profile.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'user_profile'

    def get(self, request, *args, **kwargs):
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

    def get(self, request, *args, **kwargs):
        # username = self.kwargs['username']
        req_user = request.user
        total_balance = 0
        if req_user is not None:
            trade_accounts = TradeAccount.objects.filter(
                trader=req_user)  # 前台需要添加view more...
            for trade_account in trade_accounts:
                total_balance += trade_account.account_balance

            queryset = {
                'trade_accounts': trade_accounts,
                'total_balance': total_balance,
                'total_accounts': len(trade_accounts),
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
        stock_symbol = self.kwargs['symbol']
        if req_user is not None:
            tradedetails = TradeRec.objects.filter(
                trader=req_user.id, stock_code=stock_symbol, created_or_mod_by='human')  # 前台需要添加view more...
            trade_positions = Positions.objects.filter(
                trader=req_user.id, is_liquadated=False).exclude(lots=0)
            strategies = TradeStrategy.objects.filter(creator=req_user.id)
            stocks_following = StockFollowing.objects.filter(
                trader=req_user.id,)
            stock_info = StockNameCodeMap.objects.get(stock_code=stock_symbol)
            queryset = {
                'symbol': stock_info.stock_code,
                'stock_name': stock_info.stock_name,
                'show_symbol': stock_info.ts_code,
                'market': stock_info.market,
                'det': tradedetails,
                'pos': trade_positions,
                'str': strategies,
                'fol': stocks_following,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})
        else:
            return HttpResponseRedirect(reverse('404'))


# Create your function views here.
def file_upload(request):
    img_id = request.user.id
    file = request.FILES['filePortrait']
    ext = file.name.split('.')[1] if file is not None else ''
    save_path = os.path.join(
        settings.MEDIA_ROOT, 'portraits', str(img_id) + '.' + ext)
    default_storage.save(save_path, file)
    return 'portraits/' + str(img_id) + '.' + ext


@login_required
def update_user_profile(request):
    if request.method == 'POST':
        picture_url = file_upload(request)
        data = request.POST.copy()
        trader = request.user
        username = data.get("username")
        email = data.get('email')
        # firstname = data.get('firstName')
        # lastname = data.get('lastName')
        name = data.get('name')
        location = data.get('location')
        job_title = data.get('jobTitle')
        # bio = data.get('bio')
        short_bio = data.get('shortBio')
        # 更新相关用户字段
        # trader.email = email
        # trader.firstname = firstname
        # trader.lastname = lastname
        trader.email = email
        trader.name = name
        trader.location = location
        trader.job_title = job_title
        # trader.bio = bio
        trader.short_bio = short_bio
        trader.picture = picture_url
        # if direction == 'b':
        is_ok = trader.save()
        return JsonResponse({'code': 'success', 'message': _('更新成功')}, safe=False)

        # else:
        #     return JsonResponse({'code': 'error', 'message': _('更新失败')}, safe=False)

    return JsonResponse({'code': 'error', 'message': _('更新失败')}, safe=False)


def get_week_of_month(year, month, day):
    """
    获取指定的某天是某个月中的第几周
    周一作为一周的开始
    """
    end = int(datetime.datetime(year, month, day).strftime("%W"))
    begin = int(datetime.datetime(year, month, 1).strftime("%W"))
    return end - begin + 1


def calc_realtime_snapshot(request):
    trader = request.user
    today = datetime.date.today()
    trader_positions = Positions.objects.filter(trader=trader)
    # realtime更新持仓
    for trader_position in trader_positions:
        trader_position.make_profit_updated()
    positions = Positions.objects.values('trade_account').annotate(sum_profit=Sum(
        'profit')).values('trade_account', 'sum_profit').filter(trader=trader, is_liquadated=False)
    # 是否今天的snapshot存在
    for position in positions:
        # 当天是否有snapshot，如果没有就创建，有就更新
        snapshots = TradeProfitSnapshot.objects.filter(
            trader=trader, trade_account=position['trade_account'], snap_date=today, applied_period='d')
        if snapshots is None or len(snapshots) == 0:
            snapshot = TradeProfitSnapshot(trader=trader, trade_account=TradeAccount.objects.get(
                id=position['trade_account']), snap_date=today)
            snapshot.take_snapshot(position, 'd')
        else:
            snapshots[0].take_snapshot(position, 'd')
        # 本周是否有snapshot，如果没有就创建，有就更新
        start_day = today - \
            timedelta(days=today.weekday())  # 当前时间所在周的周一
        end_day = start_day + timedelta(days=4)  # 当前时间所在周周五
        snapshots = TradeProfitSnapshot.objects.filter(
            trader=trader, trade_account=position['trade_account'], snap_date__range=[start_day, end_day], applied_period='w')
        if snapshots is None or len(snapshots) == 0:
            snapshot = TradeProfitSnapshot(trader=trader, trade_account=TradeAccount.objects.get(
                id=position['trade_account']), snap_date=end_day)
            snapshot.take_snapshot(position, 'w')
        else:
            snapshots[0].take_snapshot(position, 'w')
        # 本月是否有snapshot，如果没有就创建，有就更新
        cal = calendar.Calendar()
        last_friday = None
        for weekdays in cal.monthdays2calendar(today.year, today.month):
            for weekday in weekdays:
                if weekday[0] != 0 and weekday[1] == calendar.FRIDAY:
                    last_friday = datetime.date(
                        today.year, today.month, weekday[0])
                    break
        start_day = today - \
            timedelta(days=today.weekday())  # 当前时间所在周的周一
        end_day = start_day + timedelta(days=4)  # 当前时间所在周周五
        snapshots = TradeProfitSnapshot.objects.filter(
            trader=trader, trade_account=position['trade_account'], snap_date=last_friday, applied_period='m')
        if snapshots is None or len(snapshots) == 0:
            snapshot = TradeProfitSnapshot(trader=trader, trade_account=TradeAccount.objects.get(
                id=position['trade_account']), snap_date=last_friday)
            snapshot.take_snapshot(position, 'm')
        else:
            snapshots[0].take_snapshot(position, 'm')
    pass


@login_required
def get_profit_trend_by_period(request, period):
    if request.method == 'GET':
        calc_realtime_snapshot(request)
        trader = request.user
        today = datetime.date.today()
        total_profit = 0
        total_profit_prev = 0
        avg_profit = 0
        profit_ratio = 0
        profit_label = []
        profit_trend = []
        previous_profit_trend = []
        max_profit = 0
        cal = calendar.Calendar()
        if period == 'w':  # 本周收益，按天统计收益
            start_day = today - \
                timedelta(days=today.weekday())  # 当前时间所在周的周一
            # end_day_wk = start_day_wk + timedelta(days=4)  # 当前时间所在周周五
            relative_start_day = start_day - \
                timedelta(days=7)  # 当前时间前一周的周一
            # relative_end_day_wk = relative_start_day_wk + \
            #     timedelta(days=4)  # 当前时间前一周周五
            for i in range(0, 5):
                snap_date = start_day + timedelta(days=i)
                relative_snap_date = relative_start_day + timedelta(days=i)
                # 日期标签
                profit_label.append(snap_date.strftime('%Y-%m-%d'))
                # 统计本周所有账户profit
                trade_account_snapshots = TradeProfitSnapshot.objects.values('snap_date',).annotate(sum_profit=Sum(
                    'profit')).values('snap_date', 'sum_profit').filter(trader=trader, snap_date=snap_date, applied_period='d')
                if trade_account_snapshots is not None and len(trade_account_snapshots) >= 1:
                    profit_trend.append(
                        int(trade_account_snapshots[0]['sum_profit']))
                else:
                    profit_trend.append(0)
                # 上一周环比数据
                relative_trade_account_snapshots = TradeProfitSnapshot.objects.values('snap_date',).annotate(sum_profit=Sum(
                    'profit')).values('snap_date', 'sum_profit').filter(trader=trader, snap_date=relative_snap_date)
                if relative_trade_account_snapshots is not None and len(relative_trade_account_snapshots) >= 1:
                    previous_profit_trend.append(
                        int(relative_trade_account_snapshots[0]['sum_profit']))
                else:
                    previous_profit_trend.append(0)
        elif period == 'm':  # 本月收益，按周统计收益
            month = today.month
            year = today.year
            # import datedelta
            last_month = today - datedelta.datedelta(months=1)
            for weekdays in cal.monthdays2calendar(year, last_month.month):
                for weekday in weekdays:
                    if weekday[0] != 0 and weekday[1] == 4:
                        profit_label.append(
                            str(year)+'-'+str(last_month.month)+'-'+str(weekday[0]))
            for date in profit_label:
                trade_account_snapshots = TradeProfitSnapshot.objects.values('snap_date',).annotate(sum_profit=Sum(
                    'profit')).values('snap_date', 'sum_profit').filter(trader=trader, snap_date=date, applied_period='w').first()
                if trade_account_snapshots is not None:
                    previous_profit_trend.append(
                        trade_account_snapshots['sum_profit'])
                else:
                    previous_profit_trend.append(0)
            profit_label = []
            for weekdays in cal.monthdays2calendar(year, month):
                for weekday in weekdays:
                    if weekday[0] != 0 and weekday[1] == 4:
                        profit_label.append(
                            str(year)+'-'+str(month)+'-'+str(weekday[0]))
            for date in profit_label:
                trade_account_snapshots = TradeProfitSnapshot.objects.values('snap_date',).annotate(sum_profit=Sum(
                    'profit')).values('snap_date', 'sum_profit').filter(trader=trader, snap_date=date, applied_period='w').first()
                if trade_account_snapshots is not None:
                    profit_trend.append(
                        trade_account_snapshots['sum_profit'])
                else:
                    profit_trend.append(0)
            # if today.weekday == 6 or today.weekday == 7:
            #     pass
            # else:
            #     start_day = today - \
            #         timedelta(days=today.weekday())  # 当前时间所在周的周一
            #     end_day = start_day + timedelta(days=4)  # 当前时间所在周周五
            #     days_in_week = 7
            #     for i in range(1, monthcalendar(year, month)):

        elif period == 'y':  # 本年收益，按月统计收益
            month = today.month
            year = today.year
            # range = monthrange(year, month)
            start_day = today - \
                timedelta(days=today.weekday())  # 当前时间所在周的周一
            end_day = start_day + timedelta(days=4)  # 当前时间所在周周五

            profit_label = [_('一月'), _('二月'), _(
                '三月'), _('四月'), _('五月'), _('六月')]
        for p in profit_trend:
            total_profit += p
        for p in previous_profit_trend:
            total_profit_prev += p
        profit_ratio = round(
            (total_profit - total_profit_prev) / total_profit * 100, 2)
        avg_profit = round(total_profit / len(profit_label), 2)
        max_profit = max(profit_trend) if max(profit_trend) > max(
            previous_profit_trend) else max(previous_profit_trend)
        min_profit = min(profit_trend) if min(profit_trend) < min(
            previous_profit_trend) else min(previous_profit_trend)
        if True:
            return JsonResponse(
                {
                    'code': 'OK',
                    'max_profit': max_profit,
                    'min_profit': min_profit,
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
        today = datetime.date.today()
        total_attempt = 0
        total_attempt_prev = 0
        avg_attempt = 0
        relative_ratio = 0
        label = []
        attempt_trend = []
        prev_attempt_trend = []
        max_attempt = 0
        if period == 'd':  # 本周收益，按天统计收益
            start_day_wk = today - timedelta(days=today.weekday())
            end_day_wk = start_day_wk + timedelta(days=6)
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
        else:  # 本年收益，按月统计收益
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
            if symbol == 'a':  # 取所有持仓信息
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
        total_percentage = str(
            round(total_avail / total_target, 2) * 100) + '%'
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
        realtime_price = decimal.Decimal(round(realtime_df['price'].mean(), 2))
        realtime_bid = decimal.Decimal(round(realtime_df['bid'].mean(), 2))
        realtime_pre_close = decimal.Decimal(round(realtime_df['pre_close'].mean(), 2))
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
        current_price = round(decimal.Decimal(data.get('currentPrice')), 2)
        price = round(decimal.Decimal(data.get('price')), 2)
        cash = round(decimal.Decimal(data.get('cash').replace(',', '')), 2)
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
def create_account(request):
    if request.method == 'POST':
        data = request.POST.copy()
        trader = request.user
        trade_account_id = data.get("accountId")
        trade_account_provider = data.get('accountProvider')
        trade_account_type = data.get('accountType')
        trade_account_capital = data.get('accountCapital')
        trade_account_balance = data.get('accountBalance')
        trade_fee = data.get('tradeFee')
        trade_account_valid_since = data.get('accountValidSince')
        if trade_account_id is None or trade_account_id == '':
            trade_account = TradeAccount(trader=trader, account_provider=trade_account_provider,
                                         account_type=trade_account_type, account_capital=trade_account_capital,
                                         trade_fee=trade_fee, account_balance=trade_account_balance,
                                         activate_date=datetime.strptime(trade_account_valid_since, '%Y-%m-%d'))
        else:
            trade_account = TradeAccount.objects.get(id=trade_account_id)
            trade_account.account_capital = trade_account_capital
            trade_account.account_balance = trade_account_balance
            trade_account.trade_fee = trade_fee
        # if direction == 'b':
        acc_id = trade_account.save()
        # else:
        #     # 卖出操作需要split买入的先前持仓
        #     new_trade.allocate_stock_for_sell()
        # result = StockNameCodeMap.objects.filter(stock_name=stock_name)
        if acc_id is not None:
            return JsonResponse({'code': 'success', 'id': acc_id, 'message': _('创建成功')}, safe=False)
        else:
            return JsonResponse({'code': 'error', 'message': _('创建失败')}, safe=False)

    return JsonResponse({'code': 'error', 'message': _('创建失败')}, safe=False)


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
