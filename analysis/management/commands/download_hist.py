from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.stock_hist import download_stock_hist


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        # Named (optional) arguments
        parser.add_argument(
            '--ts_code',
            type=str,
            help='Which ts_code you want to apply the snapshot',
        )
        parser.add_argument(
            '--freq',
            type=str,
            help='Which period you want to apply the snapshot',
        )
        pass

    def handle(self, *args, **options):
        freq = options['freq']
        ts_code = options['ts_code']
        if ts_code is not None and freq is not None:
            ts_code_list = ts_code.split(',')
            if ts_code_list is not None and len(ts_code_list) >= 1:
                # print(ts_code_list)
                download_stock_hist(freq, ts_code_list)
        else:
            download_stock_hist(freq)
        
