import tushare as ts
import json
from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from .models import StockNameCodeMap


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

            for k,v in stock_his_data_dic.items():
                t = datetime.strptime(k, "%Y-%m-%d")
                for kk, vv in v.items():
                    if kk == 'open':
                        o = vv
                    elif kk == 'high':
                        h = vv
                    elif kk == 'low':
                        l = vv
                    elif kk == 'close':
                        c = vv

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

    return JsonResponse(df, safe=False)


def get_history_stock_price_by(request, stock_name_or_code, period):
    # if this is a GET request we need to process the form data
    pro = ts.pro_api()
    start_date = ''
    end_date = ''
    ts_code = ''

    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        df = pro.daily(ts_code=ts_code, start_date=start_date,
                       end_date=end_date)
        data = []
        if df is not None and len(df) > 0:
            for d in df.values:
                data.append(
                    {
                        't': datetime.strptime(d[1], "%Y%m%d"),
                        'o': d[2],
                        'h': d[3],
                        'l': d[4],
                        'c': d[5],
                    }
                )
        return JsonResponse(data[::-1], safe=False)
