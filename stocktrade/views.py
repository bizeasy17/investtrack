import decimal
import logging
import pytz
from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from investors.models import StockFollowing, TradeStrategy
from stockmarket.models import StockNameCodeMap
from tradeaccounts.models import Positions, TradeAccount
from tradeaccounts.utils import calibrate_realtime_position
from stocktrade.models import Transactions
from .utils import *

logger = logging.getLogger(__name__)

# Create your views here.


class TransactionHomeView(LoginRequiredMixin, View):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'stocktrade/create.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'trade_info'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        stock_symbol = self.kwargs['symbol']
        account_id = kwargs['account_id'] if 'account_id' in kwargs else ''
        if req_user is not None:
            try:
                queryset = get_stock_queryset_for_trade(
                    req_user, account_id, stock_symbol)
                return render(request, self.template_name, {self.context_object_name: queryset})
            except Exception as e:
                logger.error(e)
                return HttpResponse(status=404)
        else:
            return HttpResponse(status=404)

@login_required
def make_transaction(request):
    if request.method == 'POST':
        try:
            data = request.POST.copy()
            trader = request.user
            company_name = data.get('name')
            code = data.get('code')
            market = data.get('market')
            current_price = round(decimal.Decimal(data.get('currentPrice')), 2)
            price = round(decimal.Decimal(data.get('price')), 2)
            cash = round(decimal.Decimal(data.get('cash').replace(',', '')), 2)
            strategy = TradeStrategy.objects.filter(pk=data.get('strategy'))
            quantity = int(data.get('quantity'))
            target_position = data.get('targetPosition')
            direction = data.get('direction')
            cn_tz = pytz.timezone('Asia/Shanghai')
            trade_time = cn_tz.localize(datetime.strptime(
                data.get('tradeTime'), '%Y-%m-%dT%H:%M:%S'))
            # trade_time = data.get('tradeTime').split('T')
            trade_account = TradeAccount.objects.get(id=data.get('tradeAcc'))
            force_calculate = data.get('forceCalculate')
            # trade_time = trade_time[0] + ' ' + trade_time[1]
            transaction = Transactions(trader=trader, market=market, stock_name=company_name, stock_code=code, direction=direction, current_price=current_price, price=price,
                                     board_lots=quantity, lots_remain=quantity, cash=cash, strategy=strategy[0],
                                     target_position=target_position, trade_time=trade_time,
                                     created_or_mod_by='human', trade_account=trade_account)
            # if direction == 'b':
            is_ok = transaction.save()
            # if force_calculate:
            #     calibrate_realtime_position(transaction.in_stock_positions)
            if is_ok:
                return JsonResponse({'success': _('交易成功')}, safe=False)
        except Exception as e:
            logger.error(e)
            return HttpResponse(status=500)
