from datetime import date, datetime, timedelta
import time
import tushare as ts
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.daily_basic import handle_daily_basic
from stockmarket.models import CompanyBasic, CompanyDailyBasic, CompanyManagers, ManagerRewards, StockNameCodeMap
# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


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
            company_basic()
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

        companies = StockNameCodeMap.objects.all()
        if data is not None and len(data) > 0:
            if companies.count() != len(data):
                for v in data.values:
                    try:
                        if str(v[1])[0] == '3':
                            v[7] = 'CYB'
                        elif str(v[1])[0] == '0':
                            v[7] = 'ZXB'
                        else:
                            if str(v[1])[:3] == '688':
                                v[7] = 'KCB'
                            else:
                                v[7] = 'ZB'
                        company = StockNameCodeMap.objects.get(ts_code=v[0])
                        company.stock_name = v[2]
                        company.list_status = v[9]
                        company.delist_date = v[11]
                    except Exception as e:
                        # cn_tz = pytz.timezone("Asia/Shanghai")
                        company = StockNameCodeMap(ts_code=v[0], stock_code=v[1], stock_name=v[2], area=v[3],
                                                   industry=v[4], fullname=v[5], en_name=v[6], market=v[7], exchange=v[8],
                                                   list_status=v[9], list_date=datetime.strptime(v[10], '%Y%m%d'), delist_date=v[11],
                                                   is_hs=v[12])
                    company.save()
    except Exception as e:
        print(e)


def company_basic():
    try:
        pro = ts.pro_api()

        # 查询当前所有正常上市交易的股票列表
        companies = StockNameCodeMap.objects.filter(asset='E')
        for company in companies:
            print('starting for ' + company.ts_code)
            data = pro.stock_company(
                ts_code=company.ts_code, fields='ts_code,exchange,chairman,manager,reg_capital,setup_date,province,city,introduction,website,email,office,employees,main_business,business_scope')

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
                    except Exception as e:
                        # cn_tz = pytz.timezone("Asia/Shanghai")
                        # print(e)
                        cb = CompanyBasic(ts_code=row['ts_code'], stock_code=row['ts_code'].split('.')[0], chairman=row['chairman'], manager=row['manager'], reg_capital=row['reg_capital'],
                                          setup_date=datetime.strptime(row['setup_date'], '%Y%m%d'), province=row['province'], city=row['city'], exchange=row['exchange'],
                                          introduction=row['introduction'], website=row[
                                              'website'], email=row['email'], office=row['office'],
                                          employees=row['employees'], main_business=row['main_business'], business_scope=row['business_scope'],
                                          index_category=index_ctg, company=company)
                    cb.save()
            print('ending for ' + company.ts_code)
            print('waiting for 12 sec')
            time.sleep(12)

    except Exception as e:
        print(e)


def company_manager():
    try:
        pro = ts.pro_api()

        companies = StockNameCodeMap.objects.filter(asset='E')
        for company in companies:
            print('starting for ' + company.ts_code)

            # 查询当前所有正常上市交易的股票列表
            managers = pro.stk_managers(ts_code=company.ts_code)
            cur_managers = CompanyManagers.objects.filter(
                ts_code=company.ts_code)
            if len(managers) != len(cur_managers):
                for index, row in managers.iterrows():
                    try:
                        entry = CompanyManagers.objects.filter(
                            ts_code=row['ts_code'], begin_date=row['begin_date'], end_date=row['end_date'], name=row['name'])
                        pass
                    except Exception as e:
                        # cn_tz = pytz.timezone("Asia/Shanghai")
                        # print(row['end_date'])
                        managers = CompanyManagers(ts_code=row['ts_code'], announce_date=datetime.strptime(row['ann_date'], '%Y%m%d') if row['ann_date'] is not None else row['ann_date'], name=row['name'], gender=row['gender'],
                                                   level=row['lev'], title=row['title'], edu=row[
                                                       'edu'], national=row['national'], birthday=row['birthday'],
                                                   begin_date=datetime.strptime(row['begin_date'], '%Y%m%d') if row['begin_date'] is not None else row['begin_date'], end_date=datetime.strptime(row['end_date'], '%Y%m%d') if row['end_date'] is not None else row['end_date'], company=company)
                    managers.save()

            print('ending for ' + company.ts_code)
            print('waiting for 12 sec')
            time.sleep(12)
    except Exception as e:
        print(e)


def manager_rewards():
    try:
        pro = ts.pro_api()

        companies = StockNameCodeMap.objects.filter(asset='E')
        for company in companies:
            print('starting for ' + company.ts_code)
            # 查询当前所有正常上市交易的股票列表
            rewards = pro.stk_rewards(ts_code=company.ts_code)
            cur_rewards = ManagerRewards.objects.filter(
                ts_code=company.ts_code)

            if rewards is not None and len(rewards) > 0:
                if cur_rewards.count() != len(rewards):
                    for index,row in rewards.iterrows():
                        try:
                            cur_reward = ManagerRewards.objects.get(
                                ts_code=row['ts_code'], announce_date=row['ann_date'], end_date=row['end_date'], name=row['name'])
                            pass
                        except Exception as e:
                            # cn_tz = pytz.timezone("Asia/Shanghai")
                            cur_reward = ManagerRewards(ts_code=row['ts_code'], announce_date=datetime.strptime(row['ann_date'], '%Y%m%d') if row['ann_date'] is not None else row['ann_date'], end_date=datetime.strptime(row['end_date'], '%Y%m%d') if row['end_date'] is not None else row['end_date'], name=row['name'],
                                                        title=row['title'], reward=row['reward'], hold_value=row['hold_vol'])
                        cur_reward.save()
            print('ending for ' + company.ts_code)
            print('waiting for 12 sec')
            time.sleep(12)
    except Exception as e:
        print(e)
