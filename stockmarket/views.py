import logging
from datetime import date, datetime, timedelta

import numpy as np
from numpy.lib.function_base import append
import pandas as pd
import tushare as ts
from analysis.models import (StockHistoryDaily,
                             StockIndexHistory)
from analysis.utils import get_ip
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from users.models import UserActionTrace, UserBackTestTrace, UserQueryTrace

from stockmarket.models import StockNameCodeMap, CompanyBasic, CompanyDailyBasic, ManagerRewards
from analysis.models import IndustryBasicQuantileStat

from .utils import str_eval

# Create your views here.

logger = logging.getLogger(__name__)


def stock_close_hist(request, ts_code, freq='D', period=3):
    '''
    用户需要授权可以使用策略
    '''
    # 从当前时间为获取历史的最后一天
    if request.method == 'GET':
        end_date = date.today()
        try:
            quantile = []
            qt_10 = []
            qt_90 = []
            close_result = []
            # ticks_result = []
            ma25_result = []
            ma60_result = []
            ma200_result = []
            amount_result = []
            lbl_trade_date = []

            if period != 0:
                start_date = end_date - timedelta(days=365 * period)
                results = StockHistoryDaily.objects.filter(
                    ts_code=ts_code, freq=freq, trade_date__gte=start_date, trade_date__lte=end_date).order_by('trade_date')
            else:  # period = 0 means all stock history
                results = StockHistoryDaily.objects.filter(
                    ts_code=ts_code, freq=freq, trade_date__lte=end_date).order_by('trade_date')
            # df = pd.DataFrame(results.values('stage_low_pct'))
            for result in results:
                ma25_result.append(result.ma25)
                ma60_result.append(result.ma60)
                ma200_result.append(result.ma200)
                close_result.append(result.close)
                # ticks_result.append(
                #     {
                #         't': result.trade_date, 'o': result.open, 'h': result.high,
                #         'l': result.low, 'c': result.close, 'd': '',
                #         'ma25': result.ma25, 'ma60': result.ma60, 'ma200': result.ma200,
                #     }
                # )
                amount_result.append(result.amount)
                lbl_trade_date.append(result.trade_date)
            df = pd.DataFrame(close_result, columns=['close'])
            close_qtiles = df.close.quantile(
                [0.1, 0.25, 0.5, 0.75, 0.9])
            for index, value in close_qtiles.items():
                quantile.append(round(value, 2))
            for rst in close_result:
                qt_10.append(quantile[0])  # 低价格的前10%
                qt_90.append(quantile[4])  # 高价格的前10%

            # if type == 'ticks':
            #     return JsonResponse({'ticks': ticks_result, 'ma25': ma25_result, 'ma60': ma60_result, 'ma200': ma200_result, 'amount': amount_result, 'label': lbl_trade_date}, safe=False)
            return JsonResponse({'close': close_result, 'close10': qt_10, 'close90': qt_90, 'ma25': ma25_result, 'ma60': ma60_result, 'ma200': ma200_result, 'amount': amount_result, 'label': lbl_trade_date}, safe=False)
        except Exception as err:
            logging.error(err)
            return HttpResponse(status=500)


def get_companies(request, input_text):
    '''
    根据输入获得上市公司信息
    需要更新板块，SQL如下
    update public.stockmarket_stocknamecodemap
    set market='SHZB'
    where market='ZB'

    update  public.stockmarket_stocknamecodemap
    set market='SZZB'
    where market='ZXB'

    update  public.stockmarket_stocknamecodemap
    set market='ZXB'
    where stock_code like '002%'
    '''
    board_list = {
        'SHZB': '上海主板',
        'SZZB': '深圳主板',
        'ZXB': '中小板',
        'CYB': '创业板',
        'KCB': '科创板',
    }
    if request.method == 'GET':
        try:
            if not input_text.isnumeric():
                companies = StockNameCodeMap.objects.filter(
                    Q(stock_name__contains=input_text) | Q(stock_name_pinyin__contains=input_text)).order_by('list_date')[:10]
            elif input_text.isnumeric():
                companies = StockNameCodeMap.objects.filter(
                    stock_code__contains=input_text).order_by('list_date')[:10]
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
                        'market': board_list[c.market],
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


def get_fcf(request, ts_code):
    '''
    第一种：自由现金流＝息税前利润－税金 + 折旧与摊销－资本支出－营运资本追加
    pro = ts.pro_api()
    df = pro.income(ts_code='600000.SH', start_date='20180101', end_date='20180730', 
        fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,basic_eps,diluted_eps')
    df = pro.cashflow(ts_code='600000.SH', start_date='20180101', end_date='20180730')
    '''


def get_company_basic(request, ts_code):
    if request.method == 'GET':
        company_basic_list = []
        req_user = request.user
        try:
            pro = ts.pro_api()
            ts_code_list = ts_code.split(',')
            if len(ts_code_list) > 0:
                for code in ts_code_list:
                    if req_user.is_anonymous:
                        req_user = None
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
    '''
    tbd 分隔成多个方法
    '''
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
        pe_10qt_list = []
        pe_90qt_list = []
        pe_ttm_50qt_list = []
        pe_ttm_10qt_list = []
        pe_ttm_90qt_list = []
        ps_50qt_list = []
        ps_10qt_list = []
        ps_90qt_list = []
        ps_ttm_50qt_list = []
        ps_ttm_10qt_list = []
        ps_ttm_90qt_list = []
        to_50qt_list = []
        to_10qt_list = []
        to_90qt_list = []
        vr_50qt_list = []
        vr_10qt_list = []
        vr_90qt_list = []
        pb_50qt_list = []
        pb_10qt_list = []
        pb_90qt_list = []

        try:
            cdb = CompanyDailyBasic.objects.filter(
                ts_code=ts_code, trade_date__gte=datetime.strptime(start_date, '%Y%m%d'), trade_date__lte=datetime.strptime(end_date, '%Y%m%d'),).order_by('-trade_date')
            df = pd.DataFrame(cdb.values('pe', 'pe_ttm', 'ps', 'ps_ttm', 'turnover_rate', 'volume_ratio',
                                         'pb', 'trade_date', 'total_mv', 'circ_mv', 'total_share', 'free_share', 'float_share'))
            # df = pro.daily_basic(ts_code=ts_code, start_date=start_date, end_date=end_date,
            #                      fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pe_ttm,pb,ps_ttm,ps')
            # pe_50qt = df['pe'].quantile() if df['pe'].quantile(
            # ) is not None and not np.isnan(df['pe'].quantile()) else 0
            # pe_ttm_50qt = df['pe_ttm'].quantile() if df['pe_ttm'].quantile(
            # ) is not None and not np.isnan(df['pe_ttm'].quantile()) else 0
            # ps_50qt = df['ps'].quantile()
            # ps_ttm_50qt = df['ps_ttm'].quantile()
            # to_50qt = df['turnover_rate'].quantile()
            # vr_50qt = df['volume_ratio'].quantile()
            # pb_50qt = df['pb'].quantile()

            pe_qt = df['pe'].quantile([0.1, 0.25, 0.5, 0.75, 0.9])
            pe_ttm_qt = df['pe_ttm'].quantile([0.1, 0.25, 0.5, 0.75, 0.9])
            ps_qt = df['ps'].quantile([0.1, 0.25, 0.5, 0.75, 0.9])
            ps_ttm_qt = df['ps_ttm'].quantile([0.1, 0.25, 0.5, 0.75, 0.9])
            to_qt = df['turnover_rate'].quantile([0.1, 0.25, 0.5, 0.75, 0.9])
            vr_qt = df['volume_ratio'].quantile([0.1, 0.25, 0.5, 0.75, 0.9])
            pb_qt = df['pb'].quantile([0.1, 0.25, 0.5, 0.75, 0.9])

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
                    vr_list.append(row['volume_ratio'] if row['volume_ratio'] is not None and not np.isnan(
                        row['volume_ratio']) else 0)
                    pe_list.append(
                        row['pe'] if row['pe'] is not None and not np.isnan(row['pe']) else 0)
                    pe_ttm_list.append(
                        row['pe_ttm'] if row['pe_ttm'] is not None and not np.isnan(row['pe_ttm']) else 0)
                    pb_list.append(row['pb'])
                    ps_ttm_list.append(row['ps_ttm'])
                    ps_list.append(row['ps'])

                    pe_10qt_list.append(
                        round(pe_qt.values[0] if not np.isnan(pe_qt.values[0]) else 0, 3))
                    pe_50qt_list.append(
                        round(pe_qt.values[2] if not np.isnan(pe_qt.values[2]) else 0, 3))
                    pe_90qt_list.append(
                        round(pe_qt.values[4] if not np.isnan(pe_qt.values[4]) else 0, 3))

                    pe_ttm_10qt_list.append(
                        round(pe_ttm_qt.values[0] if not np.isnan(pe_ttm_qt.values[0]) else 0, 3))
                    pe_ttm_50qt_list.append(
                        round(pe_ttm_qt.values[2] if not np.isnan(pe_ttm_qt.values[0]) else 0, 3))
                    pe_ttm_90qt_list.append(
                        round(pe_ttm_qt.values[4] if not np.isnan(pe_ttm_qt.values[0]) else 0, 3))

                    ps_10qt_list.append(round(ps_qt.values[0], 3))
                    ps_50qt_list.append(round(ps_qt.values[2], 3))
                    ps_90qt_list.append(round(ps_qt.values[4], 3))

                    ps_ttm_10qt_list.append(round(ps_ttm_qt.values[0], 3))
                    ps_ttm_50qt_list.append(round(ps_ttm_qt.values[2], 3))
                    ps_ttm_90qt_list.append(round(ps_ttm_qt.values[4], 3))

                    to_10qt_list.append(round(to_qt.values[0], 3))
                    to_50qt_list.append(round(to_qt.values[2], 3))
                    to_90qt_list.append(round(to_qt.values[4], 3))

                    vr_10qt_list.append(round(vr_qt.values[0], 3))
                    vr_50qt_list.append(round(vr_qt.values[2], 3))
                    vr_90qt_list.append(round(vr_qt.values[4], 3))

                    pb_10qt_list.append(round(pb_qt.values[0], 3))
                    pb_50qt_list.append(round(pb_qt.values[2], 3))
                    pb_90qt_list.append(round(pb_qt.values[4], 3))

                return JsonResponse({'date_label': date_label[::-1], 'turnover_rate': to_list[::-1],
                                     'volume_ratio': vr_list[::-1],
                                     'pe': pe_list[::-1], 'pe_ttm': pe_ttm_list[::-1],
                                     'pb': pb_list[::-1], 'ps_ttm': ps_ttm_list[::-1],
                                     'ps': ps_list[::-1], 'pe_10qt': pe_10qt_list,
                                     'pe_50qt': pe_50qt_list, 'pe_90qt': pe_90qt_list,
                                     'pe_ttm_10qt': pe_ttm_10qt_list, 'pe_ttm_50qt': pe_ttm_50qt_list,
                                     'pe_ttm_90qt': pe_ttm_90qt_list, 'ps_10qt': ps_10qt_list,
                                     'ps_50qt': ps_50qt_list, 'ps_90qt': ps_90qt_list,
                                     'ps_ttm_10qt': ps_ttm_10qt_list, 'ps_ttm_50qt': ps_ttm_50qt_list,
                                     'ps_ttm_90qt': ps_ttm_90qt_list, 'to_10qt': to_10qt_list,
                                     'to_50qt': to_50qt_list, 'to_90qt': to_90qt_list,
                                     'vr_10qt': vr_10qt_list, 'vr_50qt': vr_50qt_list,
                                     'vr_90qt': vr_90qt_list, 'pb_10qt': pb_10qt_list,
                                     'pb_50qt': pb_50qt_list, 'pb_90qt': pb_90qt_list,
                                     'pe_range': pe_range, 'ps_range': ps_range,
                                     'pb_range': pb_range, 'to_range': to_range,
                                     'vr_range': vr_range}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)


def get_industry_basic(request, industry, type):
    ind_dict = {}
    ind_basic = []
    industries = industry.split(',')

    try:
        req_user = request.user

        for ind in industries:
            ibqs = IndustryBasicQuantileStat.objects.filter(industry=ind, basic_type=type).exclude(quantile=.25).exclude(quantile=.75).order_by('-snap_date')[:3]

            if ibqs is not None and len(ibqs) > 0:
                for ibq in ibqs:
                    ind_basic.append(
                        {
                            'type':ibq.basic_type,
                            'qt':ibq.quantile,
                            'val':ibq.quantile_val
                        }
                    )
                ind_dict[ind] = ind_basic
        return JsonResponse({'content': ind_dict}, safe=False)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)
    pass
