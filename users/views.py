# from calendar import monthrange
import calendar
import decimal
import locale
import os
import logging
from datetime import date, datetime, timedelta

import datedelta
import tushare as ts
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, View

from investmgr import utils
from investmgr.models import (Positions, StockFollowing, StockNameCodeMap,
                              TradeAccount, TradeProfitSnapshot, TradeRec,
                              TradeStrategy)

from .forms import UserTradeForm
from .models import User

locale.setlocale(locale.LC_ALL, '')

logger = logging.getLogger(__name__)

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
            today_pnl = 0
            tradedetails = TradeRec.objects.filter(
                trader=req_user.id, )[:3]  # 前台需要添加view more...
            today = date.today()
            if today.weekday() == calendar.SATURDAY:
                snap_date = today - timedelta(days=1)
            elif today.weekday() == calendar.SUNDAY:
                snap_date = today - timedelta(days=2)
            else:
                snap_date = today
            today_snapshots = TradeProfitSnapshot.objects.filter(
                trader=req_user.id, snap_date=snap_date, applied_period='d').aggregate(profit_change=Sum('profit_change'))  # , sum_change=Sum('profit_change'))
            if today_snapshots['profit_change'] is not None:
                today_pnl = today_snapshots['profit_change']
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
            # update the position based on the realtime price
            for p in trade_positions:
                p.calibrate_realtime_position()
            strategies = TradeStrategy.objects.filter(creator=req_user.id)
            stocks_following = StockFollowing.objects.filter(
                trader=req_user.id,)[:10]
            queryset = {
                'today_pnl': today_pnl,
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
            try:
                trade_accounts = TradeAccount.objects.filter(trader=req_user)
                tradedetails = TradeRec.objects.filter(
                    trader=req_user.id, stock_code=stock_symbol, created_or_mod_by='human')
                strategies = TradeStrategy.objects.all()
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
                    'accounts': trade_accounts,
                    'account_id': account_id,
                    'trade_account': trade_account[0] if len(trade_account) >= 1 else None,
                    'strategies': strategies,
                    'trade_log': tradedetails,
                    'position': stock_position[0] if len(stock_position) >= 1 else None,
                }
                return render(request, self.template_name, {self.context_object_name: queryset})
            except Exception as e:
                logger.error(e)
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
    if len(request.FILES) > 0:
        file = request.FILES['filePortrait']
        ext = file.name.split('.')[1] if file is not None else ''
        save_path = os.path.join(
            settings.MEDIA_ROOT, 'portraits', str(img_id) + '.' + ext)
        default_storage.save(save_path, file)
        return 'portraits/' + str(img_id) + '.' + ext


@login_required
def update_user_profile(request):
    if request.method == 'POST':
        trader = request.user
        picture_url= ''
        try:
            picture_url = file_upload(request)
            data = request.POST.copy()
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
            if picture_url is not None and picture_url != '': # 如果上传头像不为空，就更新
                trader.picture = picture_url
            # if direction == 'b':
            is_ok = trader.save()
            return JsonResponse({'code': 'success', 'message': _('更新成功')}, safe=False)
        except Exception as e:
            logger.error(e)

        # else:
        #     return JsonResponse({'code': 'error', 'message': _('更新失败')}, safe=False)
    return JsonResponse({'code': 'error', 'message': _('更新失败')}, safe=False)

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
    today = date.today()
    trader_positions = Positions.objects.filter(trader=trader)
    # realtime更新持仓
    for trader_position in trader_positions:
        trader_position.make_profit_updated()
    positions = Positions.objects.values('trade_account').annotate(sum_profit=Sum(
        'profit')).values('trade_account', 'sum_profit').filter(trader=trader, is_liquadated=False)
    # 是否今天的snapshot存在
    for position in positions:
        # 当天是否有snapshot，如果没有就创建，有就更新
        if today.weekday() == calendar.SATURDAY and today.weekday() == calendar.SUNDAY:
            pass
        else:
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
                    last_friday = date(
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


def is_enough_trade_records():
    return True
    # pass


@login_required
def get_profit_trend_by_period(request, period):
    from datetime import date # workaround for UnboundLocalError: local variable 'date' referenced before assignment; don know waht
    today = date.today()
    if request.method == 'GET':
        try:
            pnl_change_today = 0
            total_profit = 0
            total_profit_prev = 0
            avg_profit = 0
            profit_ratio = 0
            pnl_label = []
            current_pnl = []
            # current_pnl_change = []
            relative_pnl_data = []
            max_pnl = 0
            code = 'OK'
            if is_enough_trade_records():
                trader = request.user
                cal = calendar.Calendar()
                if not (today.weekday() == calendar.SATURDAY or today.weekday() == calendar.SUNDAY):
                    # calc_realtime_snapshot(request)
                    pass
                sum_capital = TradeAccount.objects.filter(
                    trader=trader).aggregate(sum_capital=Sum('account_capital'))
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
                        pnl_label.append(snap_date.strftime('%Y-%m-%d'))
                        # 统计本周所有账户profit
                        trade_snapshots = TradeProfitSnapshot.objects.filter(
                            trader=trader, snap_date=snap_date, applied_period='d').aggregate(sum_profit=Sum('profit'))#, sum_change=Sum('profit_change'))
                        if trade_snapshots['sum_profit'] is not None:
                            current_pnl.append(
                                int(trade_snapshots['sum_profit']))
                            total_profit = trade_snapshots['sum_profit']
                        else:
                            current_pnl.append(0)
                        # 上一周环比数据
                        relative_snapshots = TradeProfitSnapshot.objects.filter(
                            trader=trader, snap_date=relative_snap_date).aggregate(sum_profit=Sum('profit'))
                        if relative_snapshots['sum_profit'] is not None:
                            relative_pnl_data.append(
                                int(relative_snapshots['sum_profit']))
                            total_profit_prev = relative_snapshots['sum_profit']
                        else:
                            relative_pnl_data.append(0)
                elif period == 'm':  # 本月收益，按周统计收益
                    month = today.month
                    year = today.year
                    # import datedelta
                    last_month = today - datedelta.datedelta(months=1)
                    for weekdays in cal.monthdays2calendar(year, last_month.month):
                        for weekday in weekdays:
                            if weekday[0] != 0 and weekday[1] == calendar.FRIDAY:
                                pnl_label.append(
                                    str(year)+'-'+str(last_month.month)+'-'+str(weekday[0]))
                    for date in pnl_label:
                        trade_snapshots = TradeProfitSnapshot.objects.filter(
                            trader=trader, snap_date=date, applied_period='w').aggregate(sum_profit=Sum('profit'))
                        if trade_snapshots['sum_profit'] is not None:
                            relative_pnl_data.append(
                                trade_snapshots['sum_profit'])
                            total_profit_prev = trade_snapshots['sum_profit']
                        else:
                            relative_pnl_data.append(0)
                    pnl_label = []
                    for weekdays in cal.monthdays2calendar(year, month):
                        for weekday in weekdays:
                            if weekday[0] != 0 and weekday[1] == calendar.FRIDAY:
                                pnl_label.append(
                                    str(year)+'-'+str(month)+'-'+str(weekday[0]))
                    for date in pnl_label:
                        trade_snapshots = TradeProfitSnapshot.objects.filter(
                            trader=trader, snap_date=date, applied_period='w').aggregate(sum_profit=Sum('profit'))
                        if trade_snapshots['sum_profit'] is not None:
                            current_pnl.append(
                                trade_snapshots['sum_profit'])
                            total_profit = trade_snapshots['sum_profit']
                        else:
                            current_pnl.append(0)
                    # if today.weekday == 6 or today.weekday == 7:
                    #     pass
                    # else:
                    #     start_day = today - \
                    #         timedelta(days=today.weekday())  # 当前时间所在周的周一
                    #     end_day = start_day + timedelta(days=4)  # 当前时间所在周周五
                    #     days_in_week = 7
                    #     for i in range(1, monthcalendar(year, month)):

                elif period == 'y':  # 本年收益，按月统计收益
                    year = today.year
                    month = today.month
                    day_last_year = today - datedelta.YEAR
                    for i in range(1, 13):
                        # 日期标签
                        month_label = date(year, i, 1)
                        pnl_label.append(month_label.strftime('%Y-%m'))
                        # 按月计算账户合计利润
                        month_snapshots = TradeProfitSnapshot.objects.filter(trader=trader, snap_date__year=year, snap_date__month=month_label.strftime(
                            '%m'), applied_period='m').aggregate(sum_profit=Sum('profit'))
                        if month_snapshots['sum_profit'] is not None:
                            current_pnl.append(month_snapshots['sum_profit'])
                            total_profit_prev = month_snapshots['sum_profit']
                        else:
                            current_pnl.append(0)
                        # 上年月利润快照
                        month_snapshots = TradeProfitSnapshot.objects.values('snap_date',).filter(trader=trader, snap_date__year=day_last_year.strftime(
                            '%Y'), snap_date__month=month_label.strftime('%m'), applied_period='m').aggregate(sum_profit=Sum('profit'))
                        if month_snapshots['sum_profit'] is not None:
                            relative_pnl_data.append(
                                month_snapshots['sum_profit'])
                            total_profit = month_snapshots['sum_profit']
                        else:
                            relative_pnl_data.append(0)
                ratio = total_profit / sum_capital['sum_capital']
                ratio_compare = total_profit_prev / sum_capital['sum_capital']
                # total_profit_prev = previous_profit_trend[::-1]
                profit_ratio = round(ratio - ratio_compare, 2) * 100
                avg_profit = round(total_profit / len(pnl_label), 2)
                max_pnl = max(current_pnl) if max(current_pnl) > max(
                    relative_pnl_data) else max(relative_pnl_data)
                min_profit = min(current_pnl) if min(current_pnl) < min(
                    relative_pnl_data) else min(relative_pnl_data)
            else:
                code = 'BLANK'
            if True:
                return JsonResponse(
                    {
                        'code': code,
                        'max_profit': max_pnl,
                        'min_profit': min_profit,
                        'total_profit': total_profit,
                        'avg_profit': avg_profit,
                        'profit_ratio': profit_ratio,
                        'label': pnl_label,
                        'profit_trend': current_pnl,
                        'previous_profit_trend': relative_pnl_data,
                    }, safe=False)
            else:
                return JsonResponse({'code': 'NULL'}, safe=False)
        except Exception as e:
            logger.error(e)

def get_realtime_price(stock_symbol):
    realtime_df = ts.get_realtime_quotes(
        stock_symbol)  # 需要再判断一下ts_code
    realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                               'high', 'low', 'bid', 'ask', 'volume', 'amount', 'time']]
    realtime_price = round(decimal.Decimal(realtime_df['price'].mean()), 2)
    realtime_bid = round(decimal.Decimal(realtime_df['bid'].mean()), 2)
    realtime_pre_close = round(
        decimal.Decimal(realtime_df['pre_close'].mean()), 2)

    if realtime_price != decimal.Decimal(0.00):
        realtime_price = realtime_price
    elif realtime_bid != decimal.Decimal(0.00):
        realtime_price = realtime_bid
    else:
        realtime_price = realtime_pre_close
    return realtime_price


@login_required
def get_trans_success_rate_by_period(request, period):
    if request.method == 'GET':
        try:
            trader = request.user
            today = date.today()
            total_attempt = 0
            total_success = 0
            total_attempt_yoy = 0
            avg_attempt = 0
            yoy_ratio = 0
            label = []
            success_rate = []
            fail_rate = []
            yoy_success_rate = []
            yoy_fail_rate = []
            max_attempt = 0
            cal = calendar.Calendar()
            if period == 'w':  # 本周交易成功率
                start_day = today - \
                    timedelta(days=today.weekday())  # 当前时间所在周的周一
                end_day = start_day_wk + timedelta(days=4)  # 当前时间所在周周五
                relative_start_day = start_day - \
                    timedelta(days=7)  # 当前时间前一周的周一
                relative_end_day = relative_start_day + \
                    timedelta(days=4)  # 当前时间所在周周五
                for i in range(0, 5):
                    date_label = start_day + timedelta(i)
                    label.append(date_label)
                success_rate = [3, 1, 0, 3, 1]
                yoy_success_rate = [1, 0, 1, -1, 3]
            elif period == 'm':  # 本月收益，按周统计收益
                pass
            elif period == 'y':  # 本年收益，按月统计收益
                year = today.year
                month = today.month
                day_last_year = today - datedelta.YEAR
                for i in range(1, 13):
                    success_count = 0
                    fail_count = 0
                    # 日期标签
                    month_label = date(year, i, 1)
                    label.append(month_label.strftime('%Y-%m'))
                    trade_recs = TradeRec.objects.filter(trader=trader, trade_time__year=year, trade_time__month=month_label.strftime(
                        '%m'), created_or_mod_by='human').order_by('trade_time')
                    total_attempt += len(trade_recs)
                    for trade_rec in trade_recs:
                        # 买入交易已经被卖出
                        if trade_rec.direction == 'b' and trade_rec.is_sold is True:
                            sys_recs = TradeRec.objects.filter(
                                trader=trader, created_or_mod_by='system', rec_ref_number=trade_rec.rec_ref_number)
                            for sys_rec in sys_recs:
                                sell_rec = TradeRec.objects.get(
                                    id=sys_rec.sell_stock_refer_id)
                                if trade_rec.price < sell_rec.price:
                                    success_count += 1
                                else:
                                    fail_count += 1
                        else:  # 还处于持仓阶段,与当前最新价格比较，如果小于最新价，买入成功次数+1，否则-1
                            # 买入交易判断
                            if trade_rec.direction == 'b':
                                if trade_rec.price < trade_rec.current_price:
                                    success_count += 1
                                else:
                                    fail_count += 1
                            # 卖出交易判断
                            # else:

                            #     if trade_rec.price < get_realtime_price(trade_rec.stock_code):
                            #         success_count += 1
                            #     else:
                            #         fail_count += 1
                    total_success += success_count
                    success_rate.append(success_count)
                    fail_rate.append(fail_count)
                    # 同比去年交易成功率
                    success_count = 0
                    fail_count = 0
                    trade_recs = TradeRec.objects.filter(trader=trader, trade_time__year=day_last_year.year, trade_time__month=month_label.strftime(
                        '%m'), created_or_mod_by='human').order_by('trade_time')
                    total_attempt_yoy += len(trade_recs)
                    for trade_rec in trade_recs:
                        # 买入交易已经被卖出
                        if trade_rec.direction == 'b' and (trade_rec.sold_time is not None or trade_rec.is_sold is True):
                            sys_recs = TradeRec.objects.filter(
                                trader=trader, created_or_mod_by='system', rec_ref_number=trade_rec.rec_ref_number)
                            for sys_rec in sys_recs:
                                sell_rec = TradeRec.objects.get(
                                    id=sys_rec.sell_stock_refer_id)
                                if trade_rec.price < sell_rec.price:
                                    success_count += 1
                                else:
                                    fail_count += 1
                        else:  # 还处于持仓阶段,与当前最新价格比较，如果小于最新价，买入成功次数+1，否则-1
                            if trade_rec.price < trade_rec.current_price:
                                success_count += 1
                            else:
                                fail_count += 1
                    yoy_success_rate.append(success_count)
                    yoy_fail_rate.append(fail_count)
            
            success_ratio = str(round(total_success / total_attempt * 100, 2) ) + '%'
            if total_attempt != 0:
                yoy_ratio = str(round((total_attempt - total_attempt_yoy) / total_attempt, 2) * 100) + '%'
            avg_attempt = round(total_attempt / len(label), 2)
            max_attempt = max(success_rate) if max(success_rate) > max(
                yoy_success_rate) else max(yoy_success_rate)
            min_attempt = min(success_rate) if min(success_rate) < min(
                yoy_success_rate) else min(yoy_success_rate)
            if True:
                return JsonResponse(
                    {
                        'code': 'OK',
                        'label': label,
                        'max_attempt': max_attempt,
                        'min_attempt': min_attempt,
                        'total_attempt': total_attempt,
                        'success_ratio': success_ratio,
                        'avg_attempt': avg_attempt,
                        'yoy_ratio': yoy_ratio,
                        'success_rate': success_rate,
                        'fail_rate': fail_rate,
                        'yoy_success_rate': yoy_success_rate,
                        'yoy_fail_rate': yoy_fail_rate,
                    }, safe=False)
            else:
                return JsonResponse({'code': 'NULL'}, safe=False)
        except Exception as e:
            logger.error(e)

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
            round(total_avail / total_target * 100, 2)) + '%'
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
        realtime_pre_close = decimal.Decimal(
            round(realtime_df['pre_close'].mean(), 2))
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
        try:
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
            # trade_time = data.get('tradeTime').split('T')
            trade_account = TradeAccount.objects.get(id=data.get('tradeAcc'))
            # trade_time = trade_time[0] + ' ' + trade_time[1]
            new_trade = TradeRec(trader=trader, market=market, stock_name=company_name, stock_code=code, direction=direction, current_price=current_price, price=price,
                                board_lots=quantity, lots_remain=quantity, cash=cash, strategy=strategy[0],
                                target_position=target_position, trade_time=datetime.strptime(trade_time, '%Y-%m-%dT%H:%M:%S'),
                                created_or_mod_by='human', trade_account=trade_account)
            # if direction == 'b':
            is_ok = new_trade.save()
            # else:
            #     # 卖出操作需要split买入的先前持仓
            #     new_trade.allocate_stock_for_sell()
            # result = StockNameCodeMap.objects.filter(stock_name=stock_name)
            if is_ok:
                return JsonResponse({'success': _('交易成功')}, safe=False)
        except Exception as e:
            logger.error(e)

    return JsonResponse({'error': _('交易失败')}, safe=False)


@login_required
def create_account(request):
    if request.method == 'POST':
        try:
            data = request.POST.copy()
            trader = request.user
            trade_account_id = data.get("accountId")
            trade_account_provider = data.get('accountProvider')
            trade_account_type = data.get('accountType')
            trade_account_capital = data.get('accountCapital')
            trade_account_balance = data.get('accountBalance')
            service_charge = data.get('tradeFee')
            trade_account_valid_since = data.get('accountValidSince')
            if trade_account_id is None or trade_account_id == '':
                trade_account = TradeAccount(trader=trader, account_provider=trade_account_provider,
                                            account_type=trade_account_type, account_capital=trade_account_capital,
                                            service_charge=service_charge, account_balance=trade_account_balance,
                                            activate_date=datetime.strptime(trade_account_valid_since, '%Y-%m-%d'))
            else:
                trade_account = TradeAccount.objects.get(id=trade_account_id)
                trade_account.account_capital = trade_account_capital
                trade_account.account_balance = trade_account_balance
                trade_account.service_charge = service_charge
            # if direction == 'b':
            acc_id = trade_account.save()
            # else:
            #     # 卖出操作需要split买入的先前持仓
            #     new_trade.allocate_stock_for_sell()
            # result = StockNameCodeMap.objects.filter(stock_name=stock_name)
            if acc_id is not None:
                return JsonResponse({'code': 'success', 'id': acc_id, 'message': _('保存成功')}, safe=False)
            else:
                return JsonResponse({'code': 'error', 'message': _('保存失败')}, safe=False)
        except Exception as e:
            logger.error(e)
    return JsonResponse({'code': 'error', 'message': _('保存失败')}, safe=False)

def sync_stock_price_for_investor(position_pk, realtime_quotes=[]):
    '''
    将持仓股的价格更新到最新报价
    '''
    try:
        if len(realtime_quotes) > 0:
            linked_traderecs = TradeRec.objects.select_for_update().filter(in_stock_positions=position_pk)
            with transaction.atomic():
                for entry in linked_traderecs:
                    entry.current_price = realtime_quotes[entry.stock_code]
                    entry.save()
    except Exception as e:
        logger.error(e)

def sync_stock_position_for_investor(investor):
    '''
    根据stock_symbol更新最新的价格
    '''
    stock_symbols = []
    updated_positions = []
    realtime_quotes = []
    # in_stock_symbols = Positions.objects.filter(trader=investor).exclude(is_liquadated=True,).distinct().values('stock_code')
    # if in_stock_symbols is not None and len(in_stock_symbols) > 0:
    #     for stock_symbol in in_stock_symbols:
    #         stock_symbols.append(stock_symbol['stock_code'])
    try:
        in_stock_positions = Positions.objects.select_for_update().filter(trader=investor).exclude(is_liquadated=True,)
        with transaction.atomic():
            if in_stock_positions is not None and len(in_stock_positions) > 0:
                for position in in_stock_positions:
                    stock_symbols.append(position.stock_code)
                realtime_quotes = utils.get_realtime_price(list(set(stock_symbols)))
            for entry in in_stock_positions:
                entry.make_profit_updated(realtime_quotes[entry.stock_code])
                sync_stock_price_for_investor(entry.pk, realtime_quotes)
                updated_positions.append(
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
        return updated_positions
    except Exception as e:
        logger.error(e)

@login_required
def refresh_my_position(request):
    if request.method == 'GET':
        investor = request.user
        updated_positions = sync_stock_position_for_investor(investor)

        return JsonResponse(updated_positions, safe=False)

    return JsonResponse({'code': 'error', 'message': _('系统错误，请稍后再试')}, safe=False)


@login_required
def get_position_by_symbol(request, account_id, symbol):
    if request.method == 'GET':
        try:
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
        except Exception as e:
            logger.error(e)
    return JsonResponse({'code': 'ERR', 'content': _('系统错误，请稍后再试')}, safe=False)

# class UserDetailView(LoginRequiredMixin, DetailView):
#     model = User

# custom 404, 403, 500 pages


def page_not_found_view(request, exception):
     # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'pages/404.html'
    return render(request, template_name)
