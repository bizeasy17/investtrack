
import logging
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import tushare as ts
from analysis.models import (AnalysisDateSeq, IndustryBasicQuantileStat,
                             StockHistoryDaily)
from analysis.utils import get_ip
from django.contrib.auth.models import AnonymousUser
from django.db.models import Count, Q
from django.http import (Http404, HttpResponse, HttpResponseServerError,
                         JsonResponse)
from django.shortcuts import render
from numpy.lib.function_base import append
from rest_framework.response import Response
from rest_framework.views import APIView
from search.utils import pinyin_abbrev
from users.models import UserActionTrace, UserBackTestTrace, UserQueryTrace

from stockmarket.models import (City, CompanyBasic, Industry, Province,
                                StockNameCodeMap)

from .models import (CompanyBasic, CompanyDailyBasic, Industry, ManagerRewards,
                     StockNameCodeMap)
from .serializers import (CompanyDailyBasicSerializer, CompanySerializer,
                          IndustryBasicQuantileSerializer, IndustrySerializer,
                          StockCloseHistorySerializer, CitySerializer, ProvinceSerializer)
from .utils import get_ind_basic, str_eval

# Create your views here.

logger = logging.getLogger(__name__)


class IndustryList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, industry):
        industry_filter = industry.split(',')
        industry_list = []
        try:
            stocks = StockNameCodeMap.objects.filter(
                asset='E', industry__in=industry_filter).values('industry').annotate(total=Count('ts_code')).order_by('industry')

            for stock in stocks:
                ibqs = get_ind_basic(
                    stock['industry'], ['pe', 'pb', 'ps'])

                si = Industry(industry=stock['industry'], stock_count=stock['total'], pe_10pct=ibqs['pe0.1'] if 'pe0.1' in ibqs else 0,
                              pe_50pct=ibqs['pe0.5'] if 'pe0.5' in ibqs else 0, pe_90pct=ibqs['pe0.9'] if 'pe0.9' in ibqs else 0,
                              pb_10pct=ibqs['pb0.1'] if 'pb0.1' in ibqs else 0, pb_50pct=ibqs['pb0.5'] if 'pb0.5' in ibqs else 0,
                              pb_90pct=ibqs['pb0.9'] if 'pb0.9' in ibqs else 0, ps_10pct=ibqs['ps0.1'] if 'ps0.1' in ibqs else 0,
                              ps_50pct=ibqs['ps0.5'] if 'ps0.5' in ibqs else 0, ps_90pct=ibqs['ps0.9'] if 'ps0.9' in ibqs else 0,)
                industry_list.append(si)
            serializer = IndustrySerializer(industry_list, many=True)
            return Response(serializer.data)
        except Industry.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


class IndustryBasicList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, industry, basic_type, quantile, start_date, end_date):
        try:
            ibqs = IndustryBasicQuantileStat.objects.filter(industry=industry, basic_type=basic_type, quantile=float(quantile),
                                                            snap_date__lte=datetime.strptime(
                                                                end_date, '%Y%m%d'),
                                                            snap_date__gte=datetime.strptime(
                                                                start_date, '%Y%m%d')).values('industry', 'snap_date', 'basic_type',
                                                                                              'stk_quantity', 'quantile', 'quantile_val').order_by('snap_date')
            serializer = IndustryBasicQuantileSerializer(
                ibqs, many=True)
            return Response(serializer.data)
        except Industry.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


class CityList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, province, top):
        try:
            if province != '-1':
                cities = City.objects.filter(province__name=province).values('name')[0:top]
            else:  # period = 0 means all stock history
                cities = City.objects.all().values('name')[0:top]

            serializer = CitySerializer(cities, many=True)
            return Response(serializer.data)
        except StockHistoryDaily.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


class ProvinceList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, country):
        try:
            if country != '-1':
                provinces = Province.objects.filter(
                    country=country).values('name')
            else:  # period = 0 means all stock history
                provinces = Province.objects.all().values('name')

            serializer = ProvinceSerializer(provinces, many=True)
            return Response(serializer.data)
        except StockHistoryDaily.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError

class CompanyList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    queryset = StockNameCodeMap.objects.filter(asset='E')
    # def get_queryset(self):
    #     queryset = StockNameCodeMap.objects.all()
    #     # serializer_class = CompanySerializer
    #     return queryset

    def get(self, request, input_text=None):
        try:
            companies = StockNameCodeMap.objects.filter(
                Q(ts_code__contains=input_text)
                | Q(stock_name__contains=input_text)
                | Q(stock_name_pinyin__icontains=input_text)).order_by('list_date')[:10]
            serializer = CompanySerializer(companies, many=True)
            return Response(serializer.data)
        except StockNameCodeMap.DoesNotExist:
            raise Http404
        except Exception as err:
            raise HttpResponseServerError


class StockCloseHistoryList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, ts_code, freq='D', period=3):
        try:
            if period <= 5:
                start_date = date.today() - timedelta(days=365 * period)
                close_history = StockHistoryDaily.objects.filter(
                    ts_code=ts_code, freq=freq, trade_date__gte=start_date,
                    trade_date__lte=date.today()).values('close', 'trade_date').order_by('trade_date')
            else:  # period = 0 means all stock history
                close_history = StockHistoryDaily.objects.filter(
                    ts_code=ts_code, freq=freq, trade_date__lte=date.today()).values('close', 'trade_date').order_by('trade_date')

            # df = pd.DataFrame(close_history, columns=['close','trade_date'])
            # close_qtiles = df.close.quantile(
            #     [0.1, 0.25, 0.5, 0.75, 0.9])

            # df['close_10pct'] = close_qtiles[.1]
            # df['close_50pct'] = close_qtiles[.5]
            # df['close_90pct'] = close_qtiles[.9]

            serializer = StockCloseHistorySerializer(close_history, many=True)
            return Response(serializer.data)
        except StockHistoryDaily.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


class StockDailyBasicHistoryList(APIView):
    # queryset = StockHistoryDaily.objects.filter(freq='D')

    def get(self, request, ts_code, start_date, end_date):
        try:
            cdb = CompanyDailyBasic.objects.filter(
                ts_code=ts_code, trade_date__gte=datetime.strptime(
                    start_date, '%Y%m%d'),
                trade_date__lte=datetime.strptime(end_date, '%Y%m%d'),).values('trade_date', 'pe', 'pe_ttm',
                                                                               'pb', 'ps', 'ps_ttm', 'turnover_rate',
                                                                               'volume_ratio').order_by('trade_date')

            serializer = CompanyDailyBasicSerializer(cdb, many=True)
            # serializer.fields = basic_type.split(',')
            return Response(serializer.data)
        except CompanyDailyBasic.DoesNotExist:
            raise Http404
        except Exception as err:
            print(err)
            raise HttpResponseServerError


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

    if request.method == 'GET':
        try:
            if not input_text.isnumeric():
                companies = StockNameCodeMap.objects.filter(
                    Q(stock_name__contains=input_text) | Q(stock_name_pinyin__icontains=input_text)).order_by('list_date')[:10]
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


def get_industry_basic(request, industry, type):
    ind_dict = {}
    ind_basic = []
    industries = industry.split(',')
    basic_types = type.split(',')

    try:
        req_user = request.user
        last_analysis = AnalysisDateSeq.objects.filter(
            applied=True, seq_type='INDUSTRY_BASIC_QUANTILE').order_by('-analysis_date').first()

        for ind in industries:
            ibqs = IndustryBasicQuantileStat.objects.filter(industry=ind, basic_type__in=basic_types, snap_date=last_analysis.analysis_date).exclude(
                quantile=.25).exclude(quantile=.75).order_by('-snap_date')

            if ibqs is not None and len(ibqs) > 0:
                for ibq in ibqs:
                    ind_basic.append(
                        {
                            'type': ibq.basic_type,
                            'qt': ibq.quantile,
                            'val': ibq.quantile_val
                        }
                    )
                ind_dict[ind] = ind_basic
        return JsonResponse({'content': ind_dict}, safe=False)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)
    pass


def get_latest_daily_basic(request, ts_code):
    basic_list = []
    try:
        cdb = CompanyDailyBasic.objects.filter(
            ts_code=ts_code,).order_by('-trade_date').first()
        if cdb is not None:
            basic_list.append({
                'pe': round(cdb.pe, 2) if cdb.pe is not None else 0,
                'pe_ttm': round(cdb.pe_ttm, 2) if cdb.pe_ttm is not None else 0,
                'pb': round(cdb.pb, 2) if cdb.pb is not None else 0,
                'ps': round(cdb.ps, 2) if cdb.ps is not None else 0,
                'ps_ttm': round(cdb.ps_ttm, 2) if cdb.ps_ttm is not None else 0,
            })
        return JsonResponse({'latest_basic': basic_list}, safe=False)
    except Exception as err:
        return HttpResponse(status=500)
    pass


def command_test(request):
    try:
        companies_bef = CompanyBasic.objects.filter(
        ).order_by().values('province', 'city').distinct()
        # print(len(companies_bef))
        # companies = StockNameCodeMap.objects.all()
        for c in companies_bef:
            print(c['province'])
            print(c['city'])
            prov = Province(name=c['province'], province_pinyin=pinyin_abbrev(
                c['province']))
            prov.save()
            city = City(name=c['city'], proince=c['province'], city_pinyin=pinyin_abbrev(
                c['city']))
            city.save()

            print(c['province'] + ' created.')
            print(c['city'] + ' created.')

            cb = CompanyBasic.objects.filter(
                province=c['province'])
            for b in cb:
                b.shengfen = prov
                b.chengshi = city
                b.save()
                print(prov.name + ',' + city.name + ' FK updated for ' +
                        b.ts_code + ' CompanyBasic.')

            companies = StockNameCodeMap.objects.filter(
                area=c['province'])
            for company in companies:
                company.province = prov
                company.save()
                print(prov.name + ' FK updated for ' +
                        company.ts_code + ' StockNameCode.')
    except Exception as err:
        print(err)
