import json
from datetime import datetime

import tushare as ts
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from .models import StockNameCodeMap, TradeRec


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
            return JsonResponse({'results':c_list}, safe=False)
    empty = {'results':[]}
    return JsonResponse(empty, safe=False)


def get_index_price_by(request, index_name, start_date, end_date, period):
    df = []
    index_list = ['sh', 'sz', 'hs300', 'sz50', 'zxb', 'cyb', 'kcb']
    if request.method == 'GET':
        if index_name in index_list:
            df = ts.get_hist_data(index_name, start=start_date,
                                  end=end_date, ktype=period)

            stock_his_data_dic = json.loads(df.to_json(orient='index'))

            data = []
            if not stock_his_data_dic:
                return JsonResponse(df, safe=False)

            for k, v in stock_his_data_dic.items():
                t = datetime.strptime(k, "%Y-%m-%d")
                for kk, vv in v.items():
                    if kk == 'open':
                        o = vv
                    elif kk == 'high':
                        h = vv
                    elif kk == 'close':
                        c = vv
                    elif kk == 'low':
                        l = vv

                data.append(
                    {
                        't': t,
                        'o': o,
                        'h': h,
                        'l': l,
                        'c': c,
                    }
                )

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
            return JsonResponse(data[::-1], safe=False)
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


def get_traderec_direction(request, stock_code, trade_date):
    code = stock_code.split('.')[0] #original format is 000001.SZ, only 000001 needed
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


def get_history_stock_price_by1(request, stock_name_or_code, start_date, end_date, period):
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
                traderec = get_traderec(
                    request, stock_name_or_code, trade_date.date())
                data.append(
                    {
                        't': trade_date,
                        'o': d[2],
                        'h': d[3],
                        'l': d[4],
                        'c': d[5],
                        'r': traderec,
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
