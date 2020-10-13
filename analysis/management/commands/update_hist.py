from datetime import date, datetime, timedelta

from analysis.stock_hist import update_stock_hist
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from stockmarket.models import StockNameCodeMap
from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.utils import generate_systask


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
            '--freq',
            type=str,
            help='Which freq you want to apply the download',
        )
        parser.add_argument(
            '--asset',
            type=str,
            help='Which asset you want to apply the download',
        )
        pass

    def handle(self, *args, **options):
        freq = options['freq']
        ts_code = options['ts_code']
        asset = options['asset']
        end_date = date.today()
        
        if freq is None:
            freq = 'D'

        if asset is None:
            asset = 'E'

        if ts_code is not None:
            ts_code_list = ts_code.split(',')
            if ts_code_list is not None and len(ts_code_list) >= 1:
                listed_companies = StockNameCodeMap.objects.filter(
                    is_hist_downloaded=True, ts_code__in=ts_code_list)
            else:
                listed_companies = StockNameCodeMap.objects.filter(
                    is_hist_downloaded=True)
            if listed_companies is not None and len(listed_companies) > 0:
                for listed_company in listed_companies:
                    update_stock_hist(freq=freq, ts_code=listed_company.ts_code,
                                      last_upd_date=listed_company.hist_update_date, asset=asset)

                    generate_systask(ts_code, freq, listed_company.hist_update_date + timedelta(days=1), end_date)
                    listed_company.is_hist_updated = True
                    listed_company.hist_update_date = end_date
                    listed_company.save()
