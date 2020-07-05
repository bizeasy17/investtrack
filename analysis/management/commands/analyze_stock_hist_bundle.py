import time
from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from analysis.strategy_test_pct import test_exp_pct
from analysis.strategy_test_period import test_by_period
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
        # strategy_code = options['strategy_code']
        freq = options['freq']
        strategy_codes = ['jiuzhuan_b', 'jiuzhuan_s', 'dibu_b', 'dingbu_s', 'w_di', 'm_ding', 'tupo_yali_b',
                         'diepo_zhicheng_s', 'ma25_zhicheng_b', 'ma25_tupo_b', 'ma25_diepo_s', 'ma25_yali_s']
        if freq is not None:
            for strategy_code in strategy_codes:
                if ts_code is not None:
                    ts_code_list = ts_code.split(',')
                    if ts_code_list is not None and len(ts_code_list) >= 1:
                        # print(ts_code_list)
                        test_by_period(strategy_code, freq, ts_code_list)
                        time.sleep(1)
                        test_exp_pct(strategy_code, ts_code_list, freq)
                else:
                    # print('all stock')
                    test_by_period(strategy_code, freq)
                    time.sleep(1)
                    test_exp_pct(strategy_code, freq)
        else:
            print('please input the mandatory freq')
            pass
