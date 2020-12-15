from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.analysis_dingdi import mark_dingdi_listed, pre_handle_dd


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

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
        version = options['ver']
        
        if freq is None:
            freq = 'D'
        
        if version is None:
            version = 'v2'

        pre_handle_dd(ts_code, freq, version)

        # if ts_code is not None and freq is not None:
        #     ts_code_list = ts_code.split(',')
        #     if ts_code_list is not None and len(ts_code_list) >= 1:
        #         # print(ts_code_list)
        #         mark_dingdi_listed(freq, ts_code_list)
        # elif freq is None:
        #     print('freq must be provided')
        # else:
        #     mark_dingdi_listed(freq)
        
