import tushare as ts
import numpy as np
import pandas as pd
import logging

from django.shortcuts import render
from datetime import date, datetime, timedelta
from django.http import HttpResponse, JsonResponse
from stockmarket.models import StockNameCodeMap
from analysis.models import StockHistoryDaily, StrategyTestLowHigh, BStrategyOnFixedPctTest
from django.db.models import Q
from users.models import UserActionTrace, UserQueryTrace, UserBackTestTrace
from analysis.utils import get_ip

# Create your views here.

logger = logging.getLogger(__name__)


def stock_close_hist(request, ts_code, freq='D', type='close', period=3):
    '''
    用户需要授权可以使用策略
    '''
    # 从当前时间为获取历史的最后一天
    if request.method == 'GET':
        end_date = date.today()
        try:
            close_result = []
            ticks_result = []
            ma25_result = []
            ma60_result = []
            ma200_result = []
            amount_result = []
            lbl_trade_date = []
            start_date = end_date - timedelta(days=365 * period)
            results = StockHistoryDaily.objects.filter(
                ts_code=ts_code, freq=freq, trade_date__gte=start_date, trade_date__lte=end_date).order_by('trade_date')
            # df = pd.DataFrame(results.values('stage_low_pct'))
            for result in results:
                ma25_result.append(result.ma25)
                ma60_result.append(result.ma60)
                ma200_result.append(result.ma200)
                close_result.append(result.close)
                ticks_result.append(
                    {
                        't': result.trade_date, 'o': result.open, 'h': result.high,
                        'l': result.low, 'c': result.close, 'd': '',
                        'ma25': result.ma25, 'ma60': result.ma60, 'ma200': result.ma200,
                    }
                )
                amount_result.append(result.amount)
                lbl_trade_date.append(result.trade_date)
            if type == 'ticks':
                return JsonResponse({'ticks': ticks_result, 'ma25': ma25_result, 'ma60': ma60_result, 'ma200': ma200_result, 'amount': amount_result, 'label': lbl_trade_date}, safe=False)
            if type == 'close':
                return JsonResponse({'close': close_result, 'ma25': ma25_result, 'ma60': ma60_result, 'ma200': ma200_result, 'amount': amount_result, 'label': lbl_trade_date}, safe=False)
        except Exception as err:
            logging.error(err)
            return HttpResponse(status=500)


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
                        'pre_close': round(float(quote[2]), 2),
                        'price': round(float(quote[3]), 2),
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
        'ZXB': '中小板',
        'CYB': '创业板',
        'KCB': '科创板',
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
                return JsonResponse({'results': company_list}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as e:
            logger.error(e)
            return HttpResponse(status=500)


def get_company_basic(request, ts_code):
    if request.method == 'GET':
        company_basic_list = []
        req_user = request.user
        try:
            pro = ts.pro_api()
            ts_code_list = ts_code.split(',')
            if len(ts_code_list) > 0:
                for code in ts_code_list:
                    query_trace = UserQueryTrace(
                        query_string=code, request_url=request.environ['HTTP_REFERER'], ip_addr=get_ip(request), uid=req_user)
                    query_trace.save()
                    
                    company_basic = StockNameCodeMap.objects.filter(
                        ts_code=code)
                    if company_basic is not None and len(company_basic) > 0:
                        df = pro.stock_company(
                            ts_code=code, fields='ts_code,chairman,manager,reg_capital,setup_date,province,city,website,employees,main_business')
                        if df is not None and len(df) > 0:
                            company_basic_list.append(
                                {
                                    'ts_code': code,
                                    'company_name': company_basic[0].fullname,
                                    'chairman': df['chairman'][0],
                                    'manager': df['manager'][0],
                                    'reg_capital': df['reg_capital'][0],
                                    'setup_date': df['setup_date'][0],
                                    'province': df['province'][0],
                                    'city': df['city'][0],
                                    'website': df['website'][0],
                                    'employees': int(df['employees'][0]),
                                    'main_business': df['main_business'][0],
                                }
                            )
                return JsonResponse(company_basic_list, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)


def get_daily_basic(request, ts_code, start_date, end_date):
    if request.method == 'GET':
        pro = ts.pro_api()
        company_daily_list = []
        pe_50qt = []
        pe_ttm_50 = []
        try:
            ts_code_list = ts_code.split(',')
            if len(ts_code_list) > 0:
                for code in ts_code_list:
                    part_basic = []
                    df = pro.daily_basic(ts_code=code, start_date=start_date, end_date=end_date,
                                         fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pe_ttm,pb,ps_ttm,ps')
                    if df is not None and len(df) > 0:
                        for index, row in df.iterrows():
                            part_basic.append({
                                'trade_date': row['trade_date'],
                                'turnover_rate': row['turnover_rate'],
                                'volume_ratio': row['volume_ratio'],
                                'pe': row['pe'],
                                'pe_ttm': row['pe_ttm'],
                                'pb': row['pb'],
                                'ps_ttm': row['ps_ttm'],
                                'ps': row['ps'],
                            })
                        company_daily_list.append({
                            code: part_basic
                        })
                return JsonResponse({'results': company_daily_list}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)


def get_single_daily_basic(request, ts_code, start_date, end_date):
    if request.method == 'GET':
        pro = ts.pro_api()
        company_daily_list = []
        to_list = []
        to_range = []
        vr_list = []
        vr_range = []
        pe_list = []
        pe_range = []
        pe_ttm_list = []
        pb_list = []
        pb_range = []
        ps_list = []
        ps_ttm_list = []
        ps_range = []
        date_label = []
        pe_50qt_list = []
        pe_ttm_50qt_list = []
        ps_50qt_list = []
        ps_ttm_50qt_list = []
        to_50qt_list = []
        vr_50qt_list = []
        pb_50qt_list = []
        try:
            df = pro.daily_basic(ts_code=ts_code, start_date=start_date, end_date=end_date,
                                 fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pe_ttm,pb,ps_ttm,ps')
            pe_50qt = df['pe'].quantile() if df['pe'].quantile(
            ) is not None and not np.isnan(df['pe'].quantile()) else 0
            pe_ttm_50qt = df['pe_ttm'].quantile() if df['pe_ttm'].quantile(
            ) is not None and not np.isnan(df['pe_ttm'].quantile()) else 0
            ps_50qt = df['ps'].quantile()
            ps_ttm_50qt = df['ps_ttm'].quantile()
            to_50qt = df['turnover_rate'].quantile()
            vr_50qt = df['volume_ratio'].quantile()
            pb_50qt = df['pb'].quantile()

            pe_range.append(75)
            pe_range.append(100)
            ps_range.append(75)
            ps_range.append(100)
            to_range.append(75)
            to_range.append(100)
            vr_range.append(75)
            vr_range.append(100)
            pb_range.append(75)
            pb_range.append(100)

            if df is not None and len(df) > 0:
                for index, row in df.iterrows():
                    date_label.append(row['trade_date'])
                    to_list.append(row['turnover_rate']
                                   if row['turnover_rate'] is not None and not np.isnan(row['turnover_rate']) else 0)
                    vr_list.append(row['volume_ratio'] if row['volume_ratio']is not None and not np.isnan(
                        row['volume_ratio']) else 0)
                    pe_list.append(
                        row['pe'] if row['pe'] is not None and not np.isnan(row['pe']) else 0)
                    pe_ttm_list.append(
                        row['pe_ttm'] if row['pe_ttm'] is not None and not np.isnan(row['pe_ttm']) else 0)
                    pb_list.append(row['pb'])
                    ps_ttm_list.append(row['ps_ttm'])
                    ps_list.append(row['ps'])

                    pe_50qt_list.append(pe_50qt)
                    pe_ttm_50qt_list.append(pe_ttm_50qt)
                    ps_50qt_list.append(ps_50qt)
                    ps_ttm_50qt_list.append(ps_ttm_50qt)
                    to_50qt_list.append(to_50qt)
                    vr_50qt_list.append(vr_50qt)
                    pb_50qt_list.append(pb_50qt)

                return JsonResponse({'date_label': date_label[::-1], 'turnover_rate': to_list[::-1],
                                     'volume_ratio': vr_list[::-1],
                                     'pe': pe_list[::-1], 'pe_ttm': pe_ttm_list[::-1],
                                     'pb': pb_list[::-1], 'ps_ttm': ps_ttm_list[::-1],
                                     'ps': ps_list[::-1], 'pe_50qt': pe_50qt_list,
                                     'pe_ttm_50qt': pe_ttm_50qt_list, 'ps_50qt': ps_50qt_list,
                                     'ps_ttm_50qt': ps_ttm_50qt_list, 'to_50qt': to_50qt_list,
                                     'vr_50qt': vr_50qt_list, 'pb_50qt': pb_50qt_list,
                                     'pe_range': pe_range, 'ps_range': ps_range,
                                     'pb_range': pb_range, 'to_range': to_range,
                                     'vr_range': vr_range}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)


def get_updown_pct(request, strategy, ts_code, test_period=80):
    '''
    用户需要授权可以使用策略
    '''
    req_user = request.user
    if request.method == 'GET':
        try:
            up_pct_list = []
            up_max_rounded = 0
            down_pct_list = []
            date_label = []
            up_qt = []
            up_50qt = []
            down_50qt = []
            down_qt = []
            results = StrategyTestLowHigh.objects.filter(
                strategy_code=strategy, ts_code=ts_code, test_period=test_period).order_by('trade_date')
            if results is not None and len(results) > 0:
                df = pd.DataFrame(results.values(
                    'stage_high_pct', 'stage_low_pct'))
                up_qtiles = df.stage_high_pct.quantile(
                    [0.1, 0.25, 0.5, 0.75, 0.9])
                down_qtiles = df.stage_low_pct.quantile(
                    [0.1, 0.25, 0.5, 0.75, 0.9])
                for qtile in up_qtiles:
                    up_qt.append(round(qtile, 3))
                for qtile in down_qtiles:
                    down_qt.append(round(qtile, 3))
                up_qt.append(round(df.mean().stage_high_pct, 3))
                up_qt.append(round(df.max().stage_high_pct, 3))
                down_qt.append(round(df.mean().stage_low_pct, 3))
                down_qt.append(round(df.min().stage_low_pct, 3))

                up_max_rounded = int(
                    np.around(df['stage_high_pct'].max() / 100)) * 100 + 50

                for result in results:
                    up_pct_list.append(round(result.stage_high_pct, 2))
                    down_pct_list.append(round(result.stage_low_pct, 2))
                    up_50qt.append(up_qt[2])
                    down_50qt.append(down_qt[2])
                    date_label.append(result.trade_date)
                
                query_trace = UserBackTestTrace(
                    ts_code=ts_code, strategy_code=strategy, btest_type='PERIOD_TEST', btest_param=test_period, request_url=request.environ['HTTP_REFERER'], ip_addr=get_ip(request), uid=req_user)
                query_trace.save()

                return JsonResponse({'date_label': date_label, 'up_pct': up_pct_list,
                                     'up_qt': up_qt, 'up_50qt': up_50qt,
                                     'down_pct': down_pct_list, 'down_qt': down_qt,
                                     'down_50qt': down_50qt, 'up_max': up_max_rounded}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logging.error(err)
            return HttpResponse(status=500)


def get_expected_pct(request, strategy, ts_code, exp_pct='pct20_period', freq='D',):
    if request.method == 'GET':
        try:
            exp_pct_data = []
            data_label = []
            quantile = []
            qt_50 = []
            results = BStrategyOnFixedPctTest.objects.filter(
                strategy_code=strategy, ts_code=ts_code,
                test_freq=freq).order_by('trade_date').values('trade_date', exp_pct)  # [:int(freq_count)]
            df = pd.DataFrame(results.values())
            qtiles = df[exp_pct].quantile([0.1, 0.25, 0.5, 0.75, 0.9])
            # for qtile in qtiles.values():
            for index, value in qtiles.items():
                quantile.append(value)
            quantile.append(round(df[exp_pct].mean(), 3))
            for rst in results:
                if rst[exp_pct] > 0 and rst[exp_pct] <= 480:
                    data_label.append(rst['trade_date'])
                    exp_pct_data.append(rst[exp_pct])
                    qt_50.append(quantile[2])
            
            query_trace = UserBackTestTrace(
                ts_code=ts_code, strategy_code=strategy, btest_type='EXP_PCT_TEST', btest_param=exp_pct, request_url=request.environ['HTTP_REFERER'], ip_addr=get_ip(request), uid=req_user)
            query_trace.save()

            return JsonResponse({'exp_pct': exp_pct_data, 'date_label': data_label, 'quantile': quantile, 'qt_50': qt_50}, safe=False)
        except Exception as err:
            print(err)
            logging.error(err)
            return HttpResponse(status=500)
