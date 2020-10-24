import logging
from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

# from rest_framework import serializers
from users.models import User
from dashboard.utils import days_to_now
from stockmarket.utils import get_single_realtime_quote

from .models import TradeAccount, PositionComments, Positions

logger = logging.getLogger(__name__)

# Create your views here.

class TradeAccountsHomeView(LoginRequiredMixin, View):
    # template_name属性用于指定使用哪个模板进行渲染
    model = User
    template_name = 'tradeaccount/create.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'trade_account'

    def get(self, request, *args, **kwargs):
        # username = self.kwargs['username']
        req_user = request.user
        total_balance = 0
        if req_user is not None:
            trade_accounts = TradeAccount.objects.filter(trader=req_user)
            for trade_account in trade_accounts:
                total_balance += trade_account.account_balance
            queryset = {
                'trade_accounts': trade_accounts,
                'total_balance': total_balance,
                'total_accounts': len(trade_accounts),
            }
            return render(request, self.template_name, {self.context_object_name: queryset})

@login_required
def create_tradeaccount(request):
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
            # 新建交易账户
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
            acc_id = trade_account.save()
            # return JsonResponse(trade_account, safe=False)
            # now still can not serialize the object
            return JsonResponse({'code': 'success', 'id': acc_id, 'message': _('保存成功')}, safe=False)
        except Exception as e:
            logger.error(e)
            return HttpResponse(status=500)

@login_required
def position_comments(request, ts_code, position_id):
    if request.method == 'GET':
        try:
            comment_list = []
            position_comments = PositionComments.objects.filter(stock_code=ts_code, position=position_id)
            # return JsonResponse(trade_account, safe=False)
            # now still can not serialize the object
            if position_comments is not None and len(position_comments) > 0:
                for comment in position_comments:
                    comment_list.append(
                        {
                            'created_time': comment.created_time,
                            'stock_name': comment.stock_name,
                            'stock_code': comment.stock_code,
                            'pct_chg': comment.pct_chg,
                            'current_price': comment.current_price,
                            'position_pct_chg': comment.position_pct_chg,
                            'period': comment.position_period,
                            'comment': comment.comments,
                        }
                    )
            return JsonResponse({'status': 200, 'comments': comment_list}, safe=False)
        except Exception as e:
            logger.error(e)
            return HttpResponse(status=500)
    elif request.method == 'POST':
        try:
            comment_list = []
            data = request.POST.copy()
            trader = request.user
            stock_code = ts_code
            rt_dict = get_single_realtime_quote(ts_code)

            position = Positions.objects.get(id=position_id)
            stock_name = position.stock_name
            pct_chg = round((rt_dict['c'] - rt_dict['p'])/rt_dict['p'] * 100,2)
            current_price = rt_dict['c']
            position_pct_chg = float(position.profit_ratio[:-1])
            period = days_to_now(position.ftd)
            comment_body = data.get('comment')
            # 新建交易账户
            comment = PositionComments(trader=trader, position=position,
                                        stock_name=stock_name, stock_code=stock_code,
                                        pct_chg=pct_chg, position_pct_chg=position_pct_chg, current_price=current_price,
                                        position_period=period, comments=comment_body)
            comment.save()

            comment_list.append({
                'created_time': comment.created_time,
                'pct_chg': comment.pct_chg,
                'current_price': comment.current_price,
                'position_pct_chg': comment.position_pct_chg,
                'period': comment.position_period,
                'content': comment.comments,
            })
            return JsonResponse({'status': 200, 'comment': comment_list}, safe=False)
        except Exception as e:
            logger.error(e)
            return HttpResponse(status=500)
