from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.strategy_test_pct import handle_exp_pct_test


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
        pass

    def handle(self, *args, **options):
        ts_code = options['ts_code']
        # strategy_code = options['strategy_code']
        freq = options['freq']
        strategy_codes = ['jiuzhuan_b', 'jiuzhuan_s', 'dibu_b', 'dingbu_s', 'w_di', 'm_ding', 'tupo_yali_b',
                          'diepo_zhicheng_s', 'ma25_zhicheng_b', 'ma25_tupo_b', 'ma25_diepo_s', 'ma25_yali_s']
        
        if freq is None:
            freq = 'D'

        if ts_code is None:
            print('ts_code is mandatory')
            return
        
        for strategy_code in strategy_codes:
            handle_exp_pct_test(strategy_code, ts_code, freq)
        
        # if ts_code is not None:
        #     ts_code_list = ts_code.split(',')
        #     if ts_code_list is not None and len(ts_code_list) >= 1:
        #         if freq is not None:
        #             for strategy_code in strategy_codes:
        #                 # print(ts_code_list)
        #                 test_exp_pct(strategy_code, ts_code_list=ts_code_list, test_freq=freq, )
        #         else:
        #             print('please input the mandatory freq')
        #     else:
        #         if freq is not None:
        #             test_exp_pct(strategy_code, test_freq=freq)
        #         else:
        #             print('please input the mandatory freq')
        # else:
        #     if freq is not None:
        #         for strategy_code in strategy_codes:
        #             # print(ts_code_list)
        #             test_exp_pct(strategy_code, test_freq=freq, )
        #     else:
        #         print('please input the mandatory freq')
        
        if freq is not None:
            freq = 'D'

        # print(ts_code_list)
        target_pct_backtesting(ts_code, freq, )

        # if ts_code is not None:
        #     ts_code_list = ts_code.split(',')
        #     if ts_code_list is not None and len(ts_code_list) >= 1:
        #         if freq is not None:
        #             for strategy_code in strategy_codes:
        #                 # print(ts_code_list)
        #                 test_exp_pct(strategy_code, ts_code_list=ts_code_list, test_freq=freq, )
        #         else:
        #             print('please input the mandatory freq')
        #     else:
        #         if freq is not None:
        #             test_exp_pct(strategy_code, test_freq=freq)
        #         else:
        #             print('please input the mandatory freq')
        # else:
        #     if freq is not None:
        #         for strategy_code in strategy_codes:
        #             # print(ts_code_list)
        #             test_exp_pct(strategy_code, test_freq=freq, )
        #     else:
        #         print('please input the mandatory freq')
