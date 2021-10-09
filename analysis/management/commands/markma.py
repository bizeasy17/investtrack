from datetime import date, datetime, timedelta

from analysis.mark_ma import handle_ma
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from stockmarket.models import StockNameCodeMap
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

        if freq is None:
            freq = 'D'

        if ma_freq is None:
            ma_freq = '25'

        handle_ma(ts_code, freq, ma_freq)
