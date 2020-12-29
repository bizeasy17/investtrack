from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.analysis_wm_cp import mark_wm_listed, handle_wm_cp


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--ts_code',
            type=str,
            help='Which ts_code you want to apply the w di, m tou',
        )
        # Named (mandatory) arguments
        parser.add_argument(
            '--freq',
            type=str,
            help='Which freq you want to apply the w di, m tou',
        )
        # Named (mandatory) arguments
        parser.add_argument(
            '--vers',
            type=str,
            help='Which version you want to apply the w di, m tou',
        )
        pass

    def handle(self, *args, **options):
        ts_code = options['ts_code']
        freq = options['freq']
        version = options['vers']


        if freq is None:
            freq = 'D'

        if version is None:
            version = 'v1'

        handle_wm_cp(ts_code, freq, version)

        
        
