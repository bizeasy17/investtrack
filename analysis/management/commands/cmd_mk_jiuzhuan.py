from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.analysis_jiuzhuan_cp import handle_jiuzhuan_cp
from stockmarket.models import StockNameCodeMap


class Command(BaseCommand):
    help = 'Taking jiuzhuan for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--ts_code',
            type=str,
            help='Which ts_code you want to apply the snapshot',
        )
        # Named (mandatory) arguments
        parser.add_argument(
            '--freq',
            type=str,
            help='Which freq you want to apply the snapshot',
        )
        pass

    def handle(self, *args, **options):
        # print('test test')
        ts_code = options['ts_code']
        freq = options['freq']

        if freq is None:
            freq = 'D'
        
        handle_jiuzhuan_cp(ts_code, freq)
