import time
from datetime import date, datetime, timedelta

import tushare as ts
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
# from analysis.utils import init_eventlog, set_event_completed, is_event_completed
from search.utils import pinyin_abbrev
from stockmarket.models import (CompanyBasic, CompanyDailyBasic,
                                CompanyManagers, CompanyTop10FloatHolders, ManagerRewards,
                                StockNameCodeMap, Province, City)
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

    def handle(self, *args, **options):
        ts_code = options['ts_code']
        collect_top10_holders(ts_code)

def collect_top10_holders(ts_code):
    try:
        pro = ts.pro_api()

        # 查询当前所有正常上市交易的股票列表
        end_year = date.today().year
        if ts_code is None:
            companies = StockNameCodeMap.objects.filter(
                asset='E').order_by('ts_code')
        else:
            companies = StockNameCodeMap.objects.filter(ts_code=ts_code)
        for company in companies:
            list_year = company.list_date.year
            for year in range(list_year, end_year+1):
                data = pro.top10_floatholders(
                    ts_code=company.ts_code, start_date=str(year)+'0101', end_date=str(year)+'1231')
                for index, row in data.iterrows():
                    print('starting for ' + company.ts_code)
                    try:
                        top10_holders = CompanyTop10FloatHolders.objects.get(
                            ts_code=company.ts_code, announce_date=row['ann_date'], end_date=row['end_date'])
                        top10_holders.announce_date = datetime.strptime(row['ann_date'],'%Y%m%d')
                        top10_holders.holder_name = row['holder_name']
                        top10_holders.end_date = datetime.strptime(row['end_date'],'%Y%m%d')
                        top10_holders.hold_amount = row['hold_amount']
                        # company.save()
                    except Exception as e:
                        print(company.ts_code +
                                ' does not exist, create new entry')
                        # cn_tz = pytz.timezone("Asia/Shanghai")
                        top10_holders = CompanyTop10FloatHolders(ts_code=company.ts_code, announce_date=datetime.strptime(row['ann_date'], '%Y%m%d'), 
                                                            end_date=datetime.strptime(row['end_date'],'%Y%m%d'),
                                                            holder_name=row['holder_name'], hold_amount=row['hold_amount'],company=company)
                        print(company.ts_code + ' created new object')

                    top10_holders.save()
                    print('end for ' + company.ts_code)
                time.sleep(0.3)
    except Exception as e:
        print(e)
