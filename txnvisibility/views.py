import json
import logging
import decimal
from datetime import date, datetime, timedelta

import tushare as ts
from django.contrib.auth.decorators import login_required
from django.db.models.functions import ExtractWeek
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from stockmarket.utils import get_single_realtime_quote
from stocktrade.models import Transactions
from tradeaccounts.models import Positions, TradeAccount

# Create your views here.

logger = logging.getLogger(__name__)


@login_required
def stock_transaction_history(request, account_id, symbol, start_date, end_date, type):
    if request.method == 'GET':
        hist_df = []
        stock_hist_list = []
        index_list = ['sh', 'sz', 'hs300', 'sz50', 'zxb', 'cyb', 'kcb']
        try:
            # if code in index_list:
            # get_hist_date depreciated
            hist_df = ts.pro_bar(ts_code=symbol, adj=None, freq=type,
                                 start_date=start_date, end_date=end_date)

            # hist_df = ts.get_hist_data(symbol, start=start_date,
            #                            end=end_date, ktype=type)
            stock_hist_dict = json.loads(hist_df.to_json(orient='index'))
            # 按照从end date（从大到小）的顺序获取历史交易数据
            is_closed = False
            for k, v in stock_hist_dict.items():
                date = str(v['trade_date']).split(' ')
                if len(date) > 1:
                    time = datetime.strptime(v['trade_date'], "%Y%m%d %H:%M:%S")
                else:
                    time = datetime.strptime(
                        v['trade_date'] + ' 15:00:00', "%Y%m%d %H:%M:%S")
                open = v['open']
                high = v['high']
                close = v['close']
                low = v['low']
                # date = str(k).split(' ')
                # if len(date) > 1:
                #     time = datetime.strptime(k, "%Y-%m-%d %H:%M:%S")
                # else:
                #     time = datetime.strptime(
                #         k + ' 15:00:00', "%Y-%m-%d %H:%M:%S")
                # for kk, vv in v.items():
                #     if kk == 'open':
                #         open = vv
                #     elif kk == 'high':
                #         high = vv
                #     elif kk == 'close':
                #         close = vv
                #     elif kk == 'low':
                #         low = vv
                transaction_hist = ''
                if symbol not in index_list:
                    transaction_hist = retrieve_transaction_hist(
                        request, symbol, time, type, account_id)
                stock_hist_list.append(
                    {
                        't': time, 'o': open, 'h': high,
                        'l': low, 'c': close, 'd': transaction_hist,
                    }
                )
            # 是否需要加入当天的k线数据
            if start_date != end_date:
                realtime_price = get_single_realtime_quote(symbol)
                # 如果实时行情数据和当前history行情数据比较，两者的时间不同，则需要将实时行情append到返回dataset
                if len(realtime_price) > 0 and realtime_price['t'].date() == stock_hist_list[0]['t'].date():
                    # if realtime_price['t'].date() < date.today():
                    is_closed = True
                # 未收盘，需要从实时行情append
                stock_hist_list = stock_hist_list[::-1]
                if not is_closed and type == 'D':
                    stock_hist_list.append(realtime_price)
            return JsonResponse(stock_hist_list, safe=False)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=404)


def retrieve_transaction_hist(request, symbol, transaction_date, type, account_id=-1):
    # original format is 000001.SZ, only 000001 needed
    bs_entry = ''
    has_buy = False
    has_sell = False
    try:
        delta_hour = timedelta(hours=1)
        input_year = transaction_date.strftime('%Y')
        input_month = transaction_date.strftime('%m')
        input_week = transaction_date.strftime('%W')
        input_day = transaction_date.strftime('%d')
        input_min = transaction_date.strftime('%M')
        if type == 'M':  # month
            transaction_list = Transactions.objects.filter(trader=request.user.id, trade_account=account_id,
                                                           stock_code=symbol, trade_time__year=input_year,
                                                           trade_time__month=input_month).exclude(created_or_mod_by='system').order_by('direction').distinct('direction')
        elif type == 'W':  # week
            transaction_list = Transactions.objects.annotate(week=ExtractWeek('trade_time')).filter(trader=request.user.id,
                                                                                                    stock_code=symbol, trade_time__year=input_year,
                                                                                                    week=input_week).exclude(created_or_mod_by='system').order_by('direction').distinct('direction')
        elif type == 'D':  # day
            transaction_list = Transactions.objects.filter(trader=request.user.id, trade_account=account_id,
                                                           stock_code=symbol,
                                                           trade_time__startswith=transaction_date.strftime('%Y-%m-%d')).exclude(created_or_mod_by='system').order_by('direction').distinct('direction')
        elif type == '60':  # 60 min
            delta_hour = timedelta(hours=1)
            transaction_list = Transactions.objects.filter(trader=request.user.id, trade_account=account_id,
                                                           stock_code=symbol, trade_time__year=input_year,
                                                           trade_time__month=input_month, trade_time__day=input_day,
                                                           trade_time__hour=(transaction_date-delta_hour).strftime('%H')).exclude(created_or_mod_by='system').order_by('direction').distinct('direction')
        elif type == '30':  # 30 min
            start_min = '0'
            end_min = '29'
            delta_hour = timedelta(hours=0)
            if input_min == '00':
                start_min = '30'
                end_min = '59'
                delta_hour = timedelta(hours=1)
            elif input_min == '30':
                start_min = '0'
                end_min = '29'

            transaction_list = Transactions.objects.filter(trader=request.user.id, trade_account=account_id,
                                                           stock_code=symbol, trade_time__year=input_year,
                                                           trade_time__month=input_month, trade_time__day=input_day,
                                                           trade_time__hour=(
                                                               transaction_date-delta_hour).strftime('%H'),
                                                           trade_time__minute__gte=start_min, trade_time__minute__lte=end_min,
                                                           ).exclude(created_or_mod_by='system').order_by('direction').distinct('direction')
        elif type == '15':  # 15 min
            start_min = '0'
            end_min = '29'
            delta_hour = timedelta(hours=0)
            if input_min == '00':
                start_min = '45'
                end_min = '59'
                delta_hour = timedelta(hours=1)
            elif input_min == '15':
                start_min = '0'
                end_min = '14'
            elif input_min == '30':
                start_min = '15'
                end_min = '29'
            elif input_min == '45':
                start_min = '30'
                end_min = '44'
            transaction_list = Transactions.objects.filter(trader=request.user.id, trade_account=account_id,
                                                           stock_code=symbol, trade_time__year=input_year,
                                                           trade_time__month=input_month, trade_time__day=input_day,
                                                           trade_time__hour=(
                                                               transaction_date-delta_hour).strftime('%H'),
                                                           trade_time__minute__gte=start_min, trade_time__minute__lte=end_min,
                                                           ).exclude(created_or_mod_by='system').order_by('direction').distinct('direction')
        for rec in transaction_list:
            if rec.direction == 'b':
                has_buy = True
            else:
                has_sell = True
            if has_buy and has_sell:
                bs_entry = 'b&s'
            elif has_buy:
                bs_entry = 'b'
            elif has_sell:
                bs_entry = 's'
    except Exception as e:
        logger.error(e)
    return bs_entry

@login_required
def stock_for_trade(request, account_id, symbol):
    if request.method == 'GET':
        req_user = request.user
        try:
            # 获得实时报价
            realtime_price = get_single_realtime_quote(symbol)
            stock_position = Positions.objects.filter(
                trader=req_user.id, stock_code=symbol, trade_account=account_id).exclude(is_liquidated=True)
            account_id = TradeAccount.objects.filter(id=account_id)
            if account_id is not None and len(account_id) == 1:
                remain_to_buy = round(
                    account_id[0].account_balance / decimal.Decimal(realtime_price['c']), 0)
            else:
                remain_to_buy = 0
            if len(str(remain_to_buy)) > 2:
                remain_to_buy = int(str(remain_to_buy)[:-2]) * 100
            else:
                remain_to_buy = 0
            if stock_position is not None and len(stock_position) == 1:
                remain_to_sell = stock_position[0].lots
                target_cash_amount = round(
                    stock_position[0].target_position * int(realtime_price['c']), 0)
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
        except Exception as e:
            logger.error(e)
    return JsonResponse(data, safe=False)
