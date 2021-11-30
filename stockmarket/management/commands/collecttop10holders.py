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
        top10_holder_list = []
        end_year = date.today().year
        end_date = None
        if ts_code is None:
            companies = StockNameCodeMap.objects.filter(asset='E').order_by('ts_code')
        else:
            companies = StockNameCodeMap.objects.filter(ts_code=ts_code)
        
        for company in companies:
            print('starting for ' + company.ts_code +
                  ':' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            list_year = company.list_date.year

            if company.top10_holder_date is None:
                data = pro.top10_floatholders(
                    ts_code=company.ts_code, start_date=str(list_year)+'0101', end_date=str(end_year)+'1231')
            else:
                data = pro.top10_floatholders(
                    ts_code=company.ts_code, start_date=
                        company.top10_holder_date.strftime('%Y%m%d'), end_date=str(end_year)+'1231')
            
            old_holders = CompanyTop10FloatHolders.objects.filter(ts_code=company.ts_code)

            if len(data) > len(old_holders):
                for index, row in data.iterrows():
                    # try:
                        # print(datetime.strptime(
                        #     row['ann_date'], '%Y%m%d'))
                        # print(datetime.strptime(row['end_date'], '%Y%m%d'))
                    holders = CompanyTop10FloatHolders.objects.filter(
                        ts_code=company.ts_code, announce_date=datetime.strptime(
                            row['ann_date'], '%Y%m%d'), end_date=datetime.strptime(row['end_date'], '%Y%m%d'),
                        holder_name=row['holder_name'])
                    if len(holders) <= 0:
                        top10_holder = CompanyTop10FloatHolders(ts_code=company.ts_code, announce_date=datetime.strptime(row['ann_date'], '%Y%m%d'),
                                                                end_date=datetime.strptime(
                            row['end_date'], '%Y%m%d'),
                            holder_name=row['holder_name'], hold_amount=row['hold_amount'], company=company)
                        # top10_holder.save()
                        top10_holder_list.append(top10_holder)
                        # top10_holders.announce_date = datetime.strptime(row['ann_date'],'%Y%m%d')
                        # top10_holders.holder_name = row['holder_name']
                        # top10_holders.end_date = datetime.strptime(row['end_date'],'%Y%m%d')
                        # top10_holders.hold_amount = row['hold_amount']
                        # company.save()
                    # except CompanyTop10FloatHolders.DoesNotExist:
                        
                        # cn_tz = pytz.timezone("Asia/Shanghai")
                        # end_date = row['end_date']
                        # print(company.ts_code + ' created new object')
                if len(top10_holder_list) > 0:
                    CompanyTop10FloatHolders.objects.bulk_create(top10_holder_list)
                    # if company.top10_holder_date != datetime.strptime(row['end_date'], '%Y%m%d'):
                        # company.top10_holder_date = datetime.strptime(row['end_date'], '%Y%m%d')
                        # company.save()
                    company.top10_holder_date = top10_holder_list[0].end_date
                    top10_holder_list.clear()
                # time.sleep(0.3)
            print('end for ' + company.ts_code +
                ':' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        StockNameCodeMap.objects.bulk_update(companies, ['top10_holder_date'])
    except Exception as e:
        print(e)
