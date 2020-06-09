from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.strategy_test_pct import test_exp_pct


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--ts_code',
            type=str,
            help='Which ts_code you want to apply the snapshot',
        )
        # Named (optional) arguments
        parser.add_argument(
            '--strategy_code',
            type=str,
            help='Which strategy_code you want to apply the snapshot',
        )
        # Named (mandatory) arguments
        parser.add_argument(
            '--freq',
            type=str,
            help='Which freq you want to apply the snapshot',
        )
        pass

    def handle(self, *args, **options):
        ts_code = options['ts_code']
        strategy_code = options['strategy_code']
        freq = options['freq']
        if strategy_code is not None and freq is not None:
            if ts_code is not None:
                ts_code_list = ts_code.split(',')
                if ts_code_list is not None and len(ts_code_list) >= 1:
                    # print(ts_code_list)
                    test_exp_pct(strategy_code, ts_code_list, test_freq=freq)
            else:
                test_exp_pct(strategy_code, test_freq=freq)
        else:
            print('please input the mandatory strategy code')
            pass
        
