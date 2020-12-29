from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.strategy_test_period import btest_pct_on_period


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--ts_code',
            type=str,
            help='Which ts_code you want to apply the snapshot',
        )
        # # Named (optional) arguments
        # parser.add_argument(
        #     '--strategy_code',
        #     type=str,
        #     help='Which strategy_code you want to apply the snapshot',
        # )
        # Named (mandatory) arguments
        parser.add_argument(
            '--freq',
            type=str,
            help='Which freq you want to apply the snapshot',
        )
        parser.add_argument(
            '--strategy_code',
            type=str,
            help='Which strategy you want to apply the snapshot',
        )
        pass

    def handle(self, *args, **options):
        ts_code = options['ts_code']
        # strategy_code = options['strategy_code']
        freq = options['freq']
        s_code = options['strategy_code']

        strategy_codes = ['jiuzhuan_count_b', 'jiuzhuan_count_s', 'dibu_b', 'dingbu_s', 'w_di',
                          'm_ding', 'tupo_b', 'diepo_s',
                          'ma25_zhicheng', 'ma25_tupo', 'ma25_diepo', 'ma25_yali',
                          'ma60_zhicheng', 'ma60_tupo', 'ma60_diepo', 'ma60_yali',
                          'ma200_zhicheng', 'ma200_tupo', 'ma200_diepo', 'ma200_yali', ]

        if freq is None:
            freq = 'D'

        if s_code is None:
            print('strategy code is mandatory')
            return

        if s_code not in strategy_codes:
            print('strategy code should be in the below list')
            print(strategy_codes)
            return

        # for strategy_code in strategy_codes:
        btest_pct_on_period(ts_code, freq, s_code, )

        # if ts_code is not None:
        #     ts_code_list = ts_code.split(',')
        #     if ts_code_list is not None and len(ts_code_list) >= 1:
        #         # print(ts_code_list)
        #         if freq is not None:
        #             for strategy_code in strategy_codes:
        #                 test_by_period(strategy_code, freq, ts_code_list)
        #         else:
        #             print('please input the mandatory freq')
        #     else:
        #         if freq is not None:
        #             test_by_period(strategy_code, freq)
        #         else:
        #             print('please input the mandatory freq')
        # else:
        #     if freq is not None:
        #         for strategy_code in strategy_codes:
        #             test_by_period(strategy_code, freq)
        #     else:
        #         print('please input the mandatory freq')
