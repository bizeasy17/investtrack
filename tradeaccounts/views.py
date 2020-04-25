import logging
from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from rest_framework import serializers
from users.models import User

from .models import TradeAccount

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
