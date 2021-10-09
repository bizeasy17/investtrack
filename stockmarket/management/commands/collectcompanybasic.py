import time
from datetime import date, datetime, timedelta

import tushare as ts
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
# from analysis.utils import init_eventlog, set_event_completed, is_event_completed
from search.utils import pinyin_abbrev
from stockmarket.models import (CompanyBasic, CompanyDailyBasic,
                                CompanyManagers, ManagerRewards,
                                StockNameCodeMap)
from users.models import User


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        # Named (optional) arguments
        parser.add_argument(
            '--ts_code',
            type=str,
            help='Which ts_code you want to apply the download',
        )

        parser.add_argument(
            '--type',
            type=str,
            help='Which ts_code you want to apply the download',
        )

    def handle(self, *args, **options):
        ts_code = options['ts_code']
        basic_type = options['type']

        if basic_type == 'basic':
            company_basic(ts_code)
        elif basic_type == 'manager':
            company_manager()
        elif basic_type == 'rewards':
            manager_rewards()
        elif basic_type == 'list':
            company_list(),
        else:
            basic_bundle()


def basic_bundle():
    company_list()
    company_basic()
    company_manager()
    manager_rewards()


def company_list():
    try:
        pro = ts.pro_api()

        # 查询当前所有正常上市交易的股票列表
        data = pro.stock_basic(
            fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,list_status,list_date,delist_date,is_hs')

        companies = StockNameCodeMap.objects.filter(
            asset='E').order_by('ts_code')
        if data is not None and len(data) > 0:
            if companies.count() != len(data):
                for index, row in data.iterrows():
                    print('starting  for ' + row['ts_code'])
                    ts_code = row['ts_code']
                    market = ''

                    if ts_code[0] == '3':
                        market = 'CYB'
                    elif ts_code[0] == '0':
                        if ts_code[:3] == '002':
                            market = 'ZXB'
                        else:
                            market = 'SZZB'
                    else:
                        if ts_code[:3] == '688':
                            market = 'KCB'
                        else:
                            market = 'SHZB'

                    print(pinyin_abbrev(row['name']))
                    try:
                        company = StockNameCodeMap.objects.get(ts_code=ts_code)
                        company.stock_name = row['name']
                        company.list_status = row['list_status']
                        company.delist_date = row['delist_date']
                        company.market = market
                        company.stock_name_pinyin = pinyin_abbrev(
                            company.stock_name)
                        # company.save()
                    except Exception as e:
                        print(row['symbol'] +
                              ' does not exist, create new entry')
                        # cn_tz = pytz.timezone("Asia/Shanghai")
                        company = StockNameCodeMap(ts_code=ts_code, stock_code=row['symbol'], stock_name=row['name'], area=row['area'],
                                                   industry=row['industry'], fullname=row['fullname'], en_name=row[
                                                       'enname'], market=market, exchange=row['exchange'],
                                                   list_status=row['list_status'], list_date=datetime.strptime(row['list_date'], '%Y%m%d'), delist_date=row['delist_date'],
                                                   is_hs=row['is_hs'], stock_name_pinyin=pinyin_abbrev(row['name']))
                        print(row['symbol'] + ' created new object')

                    company.save()
                    print('end for ' + row['symbol'])
    except Exception as e:
        print(e)


def company_basic(ts_code):
    try:
        pro = ts.pro_api()

        # 查询当前所有正常上市交易的股票列表
        if ts_code is None:
            companies = StockNameCodeMap.objects.filter(
                asset='E').order_by('ts_code')

            for company in companies:
                print('starting all company basic for ' + company.ts_code)
                data = pro.stock_company(
                    ts_code=company.ts_code, fields='ts_code,exchange,chairman,manager,reg_capital,setup_date,province,secretary,city,introduction,website,email,office,employees,main_business,business_scope')
                store_company_basic(company, data)

                print('ending company for ' + company.ts_code)
                print('waiting for 12 sec')
                time.sleep(12)
        else:
            print('starting company basic for ' + ts_code)
            company = StockNameCodeMap.objects.get(ts_code=ts_code)
            data = pro.stock_company(
                ts_code=ts_code, fields='ts_code,exchange,chairman,manager,reg_capital,setup_date,province,secretary,city,introduction,website,email,office,employees,main_business,business_scope')
            store_company_basic(company, data)
            print('ending company basic for ' + ts_code)
    except Exception as e:
        print(e)


def store_company_basic(company, data):
    if data is not None and len(data) > 0:
        for index, row in data.iterrows():
            try:
                if str(row['ts_code'])[0] == '3':
                    index_ctg = 'CYB'
                elif str(row['ts_code'])[0] == '0':
                    index_ctg = 'ZXB'
                else:
                    if str(row['ts_code'])[:3] == '688':
                        index_ctg = 'KCB'
                    else:
                        index_ctg = 'ZB'
                cb = CompanyBasic.objects.get(ts_code=row['ts_code'])
                cb.chairman = row['chairman']
                cb.manager = row['manager']
                cb.reg_capital = row['reg_capital']
                cb.setup_date = datetime.strptime(
                    row['setup_date'], '%Y%m%d')
                cb.province = row['province']
                cb.city = row['city']
                cb.introduction = row['introduction']
                cb.website = row['website']
                cb.email = row['email']
                cb.office = row['office']
                cb.employees = row['employees']
                cb.main_business = row['main_business']
                cb.business_scope = row['business_scope']
                cb.secretary = row['secretary']
            except Exception as e:
                # cn_tz = pytz.timezone("Asia/Shanghai")
                # print(e)
                cb = CompanyBasic(ts_code=row['ts_code'], stock_code=row['ts_code'].split('.')[0], chairman=row['chairman'], manager=row['manager'], reg_capital=row['reg_capital'],
                                  setup_date=datetime.strptime(row['setup_date'], '%Y%m%d'), province=row['province'], city=row['city'], exchange=row['exchange'],
                                  introduction=row['introduction'], website=row[
                    'website'], email=row['email'], office=row['office'], secretary=row['secretary'],
                    employees=row['employees'], main_business=row['main_business'], business_scope=row['business_scope'],
                    index_category=index_ctg, company=company)
            cb.save()


def company_manager():
    try:
        pro = ts.pro_api()

        companies = StockNameCodeMap.objects.filter(
            asset='E').order_by('ts_code')
        for company in companies:
            print('starting company mgr for ' + company.ts_code)

            # 查询当前所有正常上市交易的股票列表
            managers = pro.stk_managers(ts_code=company.ts_code)
            cur_managers = CompanyManagers.objects.filter(
                ts_code=company.ts_code)
            if len(managers) != len(cur_managers):
                print(len(managers))
                print(len(cur_managers))
                for index, row in managers.iterrows():
                    try:
                        entry = CompanyManagers.objects.get(
                            ts_code=row['ts_code'], begin_date=row['begin_date'], end_date=row['end_date'], name=row['name'])
                        pass
                    except Exception as e:
                        # cn_tz = pytz.timezone("Asia/Shanghai")
                        # print(row['end_date'])
                        entry = CompanyManagers(ts_code=row['ts_code'], announce_date=datetime.strptime(row['ann_date'], '%Y%m%d') if row['ann_date'] is not None else row['ann_date'], name=row['name'], gender=row['gender'],
                                                level=row['lev'], title=row['title'], edu=row[
                            'edu'], national=row['national'], birthday=row['birthday'],
                            begin_date=row['begin_date'], end_date=row['end_date'], company=company)
                    entry.save()

            print('ending company mgr for ' + company.ts_code)
            print('waiting for 12 sec')
            time.sleep(12)
    except Exception as e:
        print(e)


def manager_rewards():
    try:
        pro = ts.pro_api()

        companies = StockNameCodeMap.objects.filter(
            asset='E').order_by('ts_code')
        for company in companies:
            print('starting company rewards for ' + company.ts_code)
            # 查询当前所有正常上市交易的股票列表
            rewards = pro.stk_rewards(ts_code=company.ts_code)
            cur_rewards = ManagerRewards.objects.filter(
                ts_code=company.ts_code)

            if rewards is not None and len(rewards) > 0:
                if cur_rewards.count() != len(rewards):
                    for index, row in rewards.iterrows():
                        try:
                            mr = ManagerRewards.objects.get(
                                ts_code=row['ts_code'], announce_date=row['ann_date'], end_date=row['end_date'], name=row['name'])
                            pass
                        except Exception as e:
                            # cn_tz = pytz.timezone("Asia/Shanghai")
                            mr = ManagerRewards(ts_code=row['ts_code'], announce_date=datetime.strptime(row['ann_date'], '%Y%m%d') if row['ann_date'] is not None else row['ann_date'], end_date=datetime.strptime(row['end_date'], '%Y%m%d') if row['end_date'] is not None else row['end_date'], name=row['name'],
                                                title=row['title'], reward=row['reward'], hold_value=row['hold_vol'])
                        mr.save()
            print('ending company rewards for ' + company.ts_code)
            print('waiting for 12 sec')
            time.sleep(12)
    except Exception as e:
        print(e)
