from datetime import date, datetime, timedelta

from analysis.v2.mark_junxian_cp_v2 import pre_handle_jx
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from stockmarket.models import StockNameCodeMap
from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User


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
        
        pre_handle_jx(ts_code, freq, ma_freq, version)

    