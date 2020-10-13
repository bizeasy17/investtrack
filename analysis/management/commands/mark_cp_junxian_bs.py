from datetime import date, datetime

from analysis.analysis_junxian_bs_cp import mark_junxian_bs_listed
from analysis.v2.mark_junxian_cp_v2 import mark_junxian_since_listed,mark_junxian_cp
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from stockmarket.models import StockNameCodeMap
from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.utils import is_analyzed, get_analysis_task


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--ts_code',
            type=str,
            help='Which ts_code you want to apply the junxian',
        )
        # Named (mandatory) arguments
        parser.add_argument(
            '--freq',
            type=str,
            help='Which freq you want to apply the junxian',
        )
        # Named (mandatory) arguments
        parser.add_argument(
            '--ma_freq',
            type=str,
            help='Which freq you want to apply the junxian',
        )
        # Named (mandatory) arguments
        parser.add_argument(
            '--ver',
            type=str,
            help='Which freq you want to apply the junxian',
        )
        pass

    def handle(self, *args, **options):
        ts_code = options['ts_code']
        freq = options['freq']
        ma_freq = options['ma_freq']
        version = options['ver']

        if freq is None:
            freq = 'D'
        
        if version is None:
            version = 'v2'
        
        if ma_freq is None:
            ma_freq = '25'

        if not is_analyzed(ts_code, 'MARK_CP', 'junxian'+ma_freq+'_bs_'+version, freq):
            pass
                
        if ts_code is not None and freq is not None:
            ts_code_list = ts_code.split(',')
            if len(ts_code_list) == 0:
                listed_companies = StockNameCodeMap.objects.filter(
                    is_hist_downloaded=True)
            else:
                listed_companies = StockNameCodeMap.objects.filter(
                    is_hist_downloaded=True, ts_code__in=ts_code_list)
            print(len(listed_companies))
            if listed_companies is not None and len(listed_companies) > 0:
                for list_company in listed_companies:
                    if list_company.hist_update_date is None:
                        mark_junxian_cp(list_company.ts_code, list_company.list_date, ma_freq=ma_freq, version=version)

                    if list_company.list_date != start_date: #q更新交易记录开始时间需要往前获取日期为MA周期的时间
                        start_date = start_date - timedelta(days=int(ma_freq))
                        mark_junxian_cp(list_company.ts_code, list_company.list_date, ma_freq=ma_freq, version=version)
