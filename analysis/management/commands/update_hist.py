from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.stock_hist import update_stock_hist


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

        if ts_code is not None and freq is not None:
            ts_code_list = ts_code.split(',')
            if ts_code_list is not None and len(ts_code_list) >= 1:
                # print(ts_code_list)
                if asset is not None:
                    update_stock_hist(freq=freq, ts_code_list=ts_code_list, asset=asset)
                else:
                    update_stock_hist(freq=freq, ts_code_list=ts_code_list)
        else:
            if asset is not None:
                update_stock_hist(freq=freq, asset=asset)
            else:
                update_stock_hist(freq)
        
