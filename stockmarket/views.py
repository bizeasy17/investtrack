import tushare as ts
import logging

from django.shortcuts import render
from datetime import date, datetime, timedelta
from django.http import HttpResponse, JsonResponse
from stockmarket.models import StockNameCodeMap
from django.db.models import Q
# Create your views here.

logger = logging.getLogger(__name__)


def realtime_quotes(request, symbols):
    '''
    根据请求的股票代码列表，获得实时报价
    '''
    if request.method == 'GET':
        quote_list = []
        symbol_list = symbols.split(',')
        try:
            realtime_df = ts.get_realtime_quotes(symbol_list)
            realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                                       'high', 'low', 'bid', 'ask', 'volume', 'amount', 'date', 'time']]
            for quote in realtime_df.values:
                quote_list.append(
                    {
                        'code': quote[0],
                        'open': quote[1],
                        'pre_close': round(float(quote[2]),2),
                        'price': round(float(quote[3]),2),
                        'high': quote[4],
                        'low': quote[5],
                        'bid': quote[6],
                        'volume': quote[8],
                        'amount': quote[9],
                        'datetime': datetime.strptime(quote[10] + ' ' + quote[11], "%Y-%m-%d %H:%M:%S"),
                    }
                )
            return JsonResponse(quote_list, safe=False)
        except IndexError as err:
            logging.error(err)
            return HttpResponse(status=404)


def listed_companies(request, name_or_code):
    '''
    根据输入获得上市公司信息
    '''
    market_exch_map = {
        'ZB': '主板',
        'ZXB':'中小板',
        'CYB':'创业板',
        'KCB':'科创板',
    }
    if request.method == 'GET':
        try:
            if not name_or_code.isnumeric():
                companies = StockNameCodeMap.objects.filter(
                    Q(stock_name__startswith=name_or_code) | Q(stock_name_pinyin__contains=name_or_code)).order_by('list_date')[:10]
            elif name_or_code.isnumeric():
                companies = StockNameCodeMap.objects.filter(
                    stock_code__startswith=name_or_code).order_by('list_date')[:10]
            else:  # 输入条件是拼音首字母
                pass
            company_list = []
            if companies is not None and companies.count() > 0:
                for c in companies:
                    # 获得ts_code
                    company_list.append({
                        'id': c.stock_code,
                        'ts_code': c.ts_code,
                        'text': c.stock_name,
                        'market': market_exch_map[c.market],
                        'industry': c.industry,
                        'list_date': c.list_date,
                        'area': c.area,
                    })
                # c_str = 'results:[' + c_str + ']'
                # c_dict = json.loads(c_str)
                return JsonResponse({'results':company_list}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as e:
            logger.error(e)
            return HttpResponse(status=500)

