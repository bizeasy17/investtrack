# import datetime
import json
from datetime import date, datetime, timedelta

import tushare as ts
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.db.models.functions import ExtractWeek

from .models import (StockNameCodeMap, TradeRec, Positions, TradeProfitSnapshot)
from users.models import User


# Create your views here.
def get_realtime_price(request, stock_name_or_code):
    if request.method == 'GET':
        ts_code = ''
        if not stock_name_or_code.isnumeric():
            map = StockNameCodeMap.objects.filter(
                stock_name=stock_name_or_code)
            if map.count() > 0:
                ts_code = map[0].stock_code
        else:
            ts_code = stock_name_or_code

        # 获得实时报价
        realtime_df = ts.get_realtime_quotes(
            str(ts_code))  # 需要再判断一下ts_code
        realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                                   'high', 'low', 'bid', 'ask', 'volume', 'amount', 'time']]
        realtime_price = realtime_df['price'].mean()

    return JsonResponse({'price': realtime_price}, safe=False)


def get_realtime_price_for_kdata(request, code):
    # 获得实时报价
    realtime_df = ts.get_realtime_quotes(code)  # 需要再判断一下ts_code
    realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                               'high', 'low', 'bid', 'ask', 'volume', 'amount', 'date', 'time']]
    realtime_price = {}
    if len(realtime_df) > 0:
        if realtime_df['open'].mean() != 0:
            t = datetime.strptime(str(
                realtime_df['date'][0]) + ' ' + str(realtime_df['time'][0]), "%Y-%m-%d %H:%M:%S")
            realtime_price = {
                't': t,
                'o': realtime_df['open'].mean(),
                'h': realtime_df['high'].mean(),
                'l': realtime_df['low'].mean(),
                'c': realtime_df['price'].mean(),
            }

    return realtime_price
    # if request.method == 'GET':
    #     return JsonResponse(realtime_price, safe=False)
    # else:
    #     return realtime_price


def get_realtime_price_for_linechart(request, code):
    # 获得实时报价
    # realtime_df = ts.get_realtime_quotes(code)  # 需要再判断一下ts_code
    today_hist_df = ts.get_today_ticks(code)
    today_hist_df = today_hist_df[['time', 'price',
                                   'pchange', 'change', 'volume', 'amount', 'type']]
    # today_hist = {}
    today_hist_dict = json.loads(today_hist_df.to_json(orient='index'))

    if len(today_hist_dict) > 0:
        if request.method == 'GET':
            return JsonResponse(today_hist_dict, safe=False)
        else:
            return today_hist_df


def get_tscode_by(request, stock_name_or_code):
    if request.method == 'GET':
        ts_code = ''
        if not stock_name_or_code.isnumeric():
            map = StockNameCodeMap.objects.filter(
                stock_name=stock_name_or_code)
        else:
            map = StockNameCodeMap.objects.filter(
                stock_code=stock_name_or_code)

        if map.count() > 0:
            ts_code = map[0].stock_code
            # 获得ts_code
            return JsonResponse(ts_code, safe=False)

    return JsonResponse('err', safe=False)


def get_company_info_autocomplete(request, name_or_code):
    # Sample format
    # {
        # "results": [
    #         {
    #             "id": 1, "text": "Google Cloud Platform",
    #             "icon": "https://pbs.twimg.com/profile_images/966440541859688448/PoHJY3K8_400x400.jpg"
    #         },
    #         {
    #             "id": 2, "text": "Amazon AWS",
    #             "icon": "http://photos3.meetupstatic.com/photos/event/5/d/e/0/highres_263124032.jpeg"
    #         },
    #         {
    #             "id": 3, "text": "Docker",
    #             "icon": "https://www.docker.com/sites/default/files/legal/small_v.png"
    #         }
        # ]
    # }

    if request.method == 'GET':
        if not name_or_code.isnumeric():
            companies = StockNameCodeMap.objects.filter(
                stock_name__startswith=name_or_code)[:10]
        else:
            companies = StockNameCodeMap.objects.filter(
                stock_code__startswith=name_or_code)[:10]

        # results = {}
        c_list = []
        if companies is not None and companies.count() > 0:
            for c in companies:
                # 获得ts_code
                c_list.append({
                    'id': c.stock_code,
                    'ts_code': c.ts_code,
                    'text': c.stock_name,
                    'market': c.market,
                })
            # c_str = 'results:[' + c_str + ']'
            # c_dict = json.loads(c_str)
            return JsonResponse({'results': c_list}, safe=False)
    empty = {'results': []}
    return JsonResponse(empty, safe=False)


def get_stock_price_by(request, code, start_date, end_date, period):
    df = []
    index_list = ['sh', 'sz', 'hs300', 'sz50', 'zxb', 'cyb', 'kcb']
    if request.method == 'GET':
        # if code in index_list:
        df = ts.get_hist_data(code, start=start_date,
                              end=end_date, ktype=period)

        stock_his_data_dic = json.loads(df.to_json(orient='index'))

        data = []
        if not stock_his_data_dic:
            return JsonResponse(df, safe=False)

        # 按照从end date（从大到小）的顺序获取历史交易数据
        isClosed = False
        for k, v in stock_his_data_dic.items():
            dt = str(k).split(' ')
            if len(dt) > 1:
                t = datetime.strptime(k, "%Y-%m-%d %H:%M:%S")
            else:
                t = datetime.strptime(k + ' 15:00:00', "%Y-%m-%d %H:%M:%S")

            for kk, vv in v.items():
                if kk == 'open':
                    o = vv
                elif kk == 'high':
                    h = vv
                elif kk == 'close':
                    c = vv
                elif kk == 'low':
                    l = vv
            buy_sell = ''
            if code not in index_list:
                buy_sell = get_traderec_direction_by_period(
                    request, code, t, period)
            data.append(
                {
                    't': t,
                    'o': o,
                    'h': h,
                    'l': l,
                    'c': c,
                    'd': buy_sell,
                }
            )
        # 是否需要加入当天的k线数据
        realtime_price = get_realtime_price_for_kdata(request, code)
        # 如果实时行情数据和当前history行情数据比较，两者的时间不同，则需要将实时行情append到返回dataset
        if len(realtime_price) > 0 and realtime_price['t'].date() == data[0]['t'].date():
            # if realtime_price['t'].date() < date.today():
            isClosed = True

        # 未收盘，需要从实时行情append
        data = data[::-1]
        if not isClosed and period == 'D':
            data.append(realtime_price)

            # if df is not None and len(df) > 0:
            #     for d in df.values:
            #         data.append(
            #             {
            #                 't': datetime.strptime(d[1], "%Y%m%d"),
            #                 'o': d[2],
            #                 'h': d[3],
            #                 'l': d[4],
            #                 'c': d[5],
            #             }
            #         )
        return JsonResponse(data, safe=False)
        # return JsonResponse(stock_his_data_dic, safe=False)

    return JsonResponse({'error': _('输入信息有误，无相关数据')}, safe=False)


def get_traderec(request, stock_code, trade_date):
    traderec_list = TradeRec.objects.filter(trader=request.user.id,
                                            stock_code=stock_code, trade_time__startswith=trade_date,)

    traderec = []
    if traderec_list is not None and len(traderec_list) > 0:
        for rec in traderec_list:
            traderec.append({
                'name': rec.stock_name,
                'code': rec.stock_code,
                'direction': rec.direction,
                'price': rec.price,
                'cash': rec.cash,
            })

    return traderec


def get_traderec_direction_by_period(request, code, trade_date, period):
    # original format is 000001.SZ, only 000001 needed
    buy_sell = ''
    buy = False
    sell = False
    input_year = trade_date.strftime('%Y')
    input_month = trade_date.strftime('%m')
    input_week = trade_date.strftime('%W')
    input_day = trade_date.strftime('%d')
    input_hour = trade_date.strftime('%H')
    input_min = trade_date.strftime('%M')
    # trade_date = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:S')
    # import datetime
    delta_hour = timedelta(hours=1)
    delta_gmt8_hour = timedelta(hours=8)  # GMT+8, China Time

    if period == 'M':  # month
        traderec_list = TradeRec.objects.filter(trader=request.user.id,
                                                stock_code=code, trade_time__year=input_year, trade_time__month=input_month).order_by('direction').distinct('direction')
    elif period == 'W':  # week
        traderec_list = TradeRec.objects.annotate(week=ExtractWeek('trade_time')).filter(trader=request.user.id,
                                                stock_code=code, trade_time__year=input_year, week=input_week).order_by('direction').distinct('direction')
    elif period == 'D':  # day
        traderec_list = TradeRec.objects.filter(trader=request.user.id,
                                                stock_code=code,
                                                trade_time__startswith=trade_date.strftime('%Y-%m-%d')).order_by('direction').distinct('direction')
    elif period == '60':  # 60 min
        delta_hour = timedelta(hours=1)
        traderec_list = TradeRec.objects.filter(trader=request.user.id,
                                                stock_code=code, trade_time__year=input_year,
                                                trade_time__month=input_month, trade_time__day=input_day,
                                                trade_time__hour=(trade_date-delta_hour).strftime('%H')).order_by('direction').distinct('direction')
    elif period == '30':  # 30 min
        startMin = '0'
        endMin = '29'
        delta_hour = timedelta(hours=0)
        if input_min == '00':
            startMin = '30'
            endMin = '59'
            delta_hour = timedelta(hours=1)
        elif input_min == '30':
            startMin = '0'
            endMin = '29'

        traderec_list = TradeRec.objects.filter(trader=request.user.id,
                                                stock_code=code, trade_time__year=input_year,
                                                trade_time__month=input_month, trade_time__day=input_day,
                                                trade_time__hour=(
                                                    trade_date-delta_hour).strftime('%H'),
                                                trade_time__minute__gte=startMin, trade_time__minute__lte=endMin,
                                                ).order_by('direction').distinct('direction')
    elif period == '15':  # 15 min
        startMin = '0'
        endMin = '29'
        delta_hour = timedelta(hours=0)
        if input_min == '00':
            startMin = '45'
            endMin = '59'
            delta_hour = timedelta(hours=1)
        elif input_min == '15':
            startMin = '0'
            endMin = '14'
        elif input_min == '30':
            startMin = '15'
            endMin = '29'
        elif input_min == '45':
            startMin = '30'
            endMin = '44'
            
        traderec_list = TradeRec.objects.filter(trader=request.user.id,
                                                stock_code=code, trade_time__year=input_year,
                                                trade_time__month=input_month, trade_time__day=input_day,
                                                trade_time__hour=(
                                                    trade_date-delta_hour).strftime('%H'),
                                                trade_time__minute__gte=startMin, trade_time__minute__lte=endMin,
                                                ).order_by('direction').distinct('direction')

    for rec in traderec_list:
        if rec.direction == 'b':
            buy = True
        else:
            sell = True

    # traderec_list = TradeRec.objects.filter(trader=request.user.id,
    #                                         stock_code=code).order_by('direction')
    # if traderec_list is not None and len(traderec_list) > 0:
    #     for rec in traderec_list:
    #         rec_trade_local_time = rec.trade_time + delta_gmt8_hour
    #         recYear = rec_trade_local_time.strftime('%Y')
    #         recMonth = rec_trade_local_time.strftime('%m')
    #         recWeek = rec_trade_local_time.strftime('%W')
    #         recDay = rec_trade_local_time.strftime('%d')
    #         recHour = rec_trade_local_time.strftime('%H')
    #         recMin = rec_trade_local_time.strftime('%M')
    #         if period == 'M':  # month
    #             traderec_list = TradeRec.objects.filter(trader=request.user.id,
    #                                                     stock_code=code, trade_time__year=input_year, trade_time__month=input_month).order_by('direction').distinct('direction')
    #             for rec in traderec_list:
    #                 if recYear == input_year and recMonth == input_month:
    #                     if rec.direction == 'b':
    #                         buy = True
    #                     else:
    #                         sell = True
    #         elif period == 'W':  # week
    #             if recYear == input_year and recWeek == input_week:
    #                 if rec.direction == 'b':
    #                     buy = True
    #                 else:
    #                     sell = True
    #         elif period == 'D':  # day
    #             if recYear == input_year and recMonth == input_month and recDay == input_day:
    #                 if rec.direction == 'b':
    #                     buy = True
    #                 else:
    #                     sell = True
    #         elif period == '60':  # 60 min
    #             if recYear == input_year and recMonth == input_month and recDay == input_day and recHour == input_hour:
    #                 if rec.direction == 'b':
    #                     buy = True
    #                 else:
    #                     sell = True
    #         elif period == '30':  # 15 min or # 30 min
    #             if recYear == input_year and recMonth == input_month and recDay == input_day:
    #                 inputHm = input_hour + ':' + input_min
    #                 if input_min == '00':
    #                     inputStartHm = (
    #                         trade_date - minus_hour).strftime('%H') + ':30'
    #                 elif input_min == '30':
    #                     inputStartHm = input_hour + ':00'
    #                 recHm = recHour + ':' + recMin
    #                 if recHm > inputStartHm and recHm < inputHm:
    #                     if rec.direction == 'b':
    #                         buy = True
    #                     else:
    #                         sell = True
    #         elif period == '15':  # 15 min
    #             if recYear == input_year and recMonth == input_month and recDay == input_day and recHour == input_hour:
    #                 inputHm = input_hour + ':' + input_min
    #                 if input_min == '00':
    #                     inputStartHm = (
    #                         trade_date - minus_hour).strftime('%H') + ':45'
    #                 elif input_min == '15':
    #                     inputStartHm = input_hour + ':00'
    #                 elif input_min == '30':
    #                     inputStartHm = input_hour + ':15'
    #                 elif input_min == '45':
    #                     inputStartHm = input_hour + ':30'
    #                 recHm = recHour + ':' + recMin
    #                 if recHm > inputStartHm and recHm < inputHm:
    #                     if rec.direction == 'b':
    #                         buy = True
    #                     else:
    #                         sell = True

        if buy and sell:
            buy_sell = 'b&s'
        elif buy:
            buy_sell = 'b'
        elif sell:
            buy_sell = 's'
    return buy_sell


def get_traderec_direction(request, code, trade_date):
    # original format is 000001.SZ, only 000001 needed
    code = code.split('.')[0]
    traderec_list = TradeRec.objects.filter(trader=request.user.id,
                                            stock_code=code, trade_time__startswith=trade_date,).order_by('direction').distinct('direction')
    buy_sell = ''
    if traderec_list is not None and len(traderec_list) > 0:
        for rec in traderec_list:
            if buy_sell == '':
                buy_sell = rec.direction
            else:
                buy_sell = buy_sell + '&' + rec.direction

    return buy_sell


def get_history_stock_price_by(request, stock_name_or_code, start_date, end_date, period):
    # if this is a GET request we need to process the form data
    pro = ts.pro_api()
    # start_date = ''
    # end_date = ''
    # ts_code = ''

    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        df = pro.daily(ts_code=stock_name_or_code, start_date=start_date,
                       end_date=end_date)
        data = []
        if df is not None and len(df) > 0:
            for d in df.values:
                trade_date = datetime.strptime(d[1], '%Y%m%d')
                buy_sell = get_traderec_direction(
                    request, stock_name_or_code, trade_date.date())
                data.append(
                    {
                        't': trade_date,
                        'o': d[2],
                        'h': d[3],
                        'l': d[4],
                        'c': d[5],
                        'd': buy_sell,
                    }
                )
        return JsonResponse(data[::-1], safe=False)

    return JsonResponse({'error': _('输入信息有误，无相关数据')}, safe=False)


@login_required
def sync_company_list(request):
    if request.method == 'GET':
        pro = ts.pro_api()

        # 查询当前所有正常上市交易的股票列表
        data = pro.stock_basic(exchange='', list_status='',
                               fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,list_status,list_date,delist_date,is_hs')
        company_list = StockNameCodeMap.objects.all()
        if data is not None and len(data) > 0:
            if company_list.count() != len(data):
                for v in data.values:
                    if str(v[1])[0] == '3':
                        v[7] = 'CYB'
                    elif str(v[1])[0] == '0':
                        v[7] = 'ZXB'
                    else:
                        if str(v[1])[:3] == '688':
                            v[7] = 'KCB'
                        else:
                            v[7] = 'ZB'

                    company_list = StockNameCodeMap(ts_code=v[0], stock_code=v[1], stock_name=v[2], area=v[3],
                                                    industry=v[4], fullname=v[5], en_name=v[6], market=v[7], exchange=v[8],
                                                    list_status=v[9], list_date=datetime.strptime(v[10], '%Y%m%d'), delist_date=v[11],
                                                    is_hs=v[12])
                    company_list.save()
        # result = StockNameCodeMap.objects.filter(stock_name=stock_name)
        return JsonResponse({'success': _('公司信息同步成功')}, safe=False)

    return JsonResponse({'error': _('无法创建交易记录')}, safe=False)


@login_required
def execute_stock_snapshot(request, applied_period):
    if request.method == 'GET':
        snapshot_date = date.today()
        users = User.objects.filter(is_active=True)
        if users is not None and len(users):
            for user in users:     
                user_positions = Positions.objects.filter(trader=user)
                if user_positions is not None and len(user_positions)>=1:
                    for position in user_positions:
                        snapshot = TradeProfitSnapshot(trader=user)
                        snapshot.take_snapshot(
                            position, snapshot_date, applied_period)
            return JsonResponse({'info': _('股票快照成功')}, safe=False)
    return JsonResponse({'error': _('无法创建股票快照')}, safe=False)


