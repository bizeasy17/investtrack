import time
from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from analysis.analysis_diepo_s_cp import mark_diepo_s_listed
from analysis.analysis_dingdi import mark_dingdi_listed
from analysis.analysis_junxian_bs_cp import mark_junxian_bs_listed
from analysis.analysis_tupo_b_cp import mark_tupo_yali_listed
from analysis.analysis_wm_cp import mark_wm_listed
from analysis.stock_hist import download_stock_hist
from analysis.analysis_jiuzhuan_cp import mark_jiuzhuan
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
            help='Which ts_code you want to apply the diepo',
        )
        # Named (mandatory) arguments
        parser.add_argument(
            '--freq',
            type=str,
            help='Which freq you want to apply the diepo',
        )
        parser.add_argument(
            '--asset',
            type=str,
            help='Which asset you want to apply the download',
        )
        pass

    def handle(self, *args, **options):
        ts_code = options['ts_code']
        freq = options['freq']
        asset = options['asset']
        if ts_code is not None and freq is not None:
            ts_code_list = ts_code.split(',')
            if ts_code_list is not None and len(ts_code_list) >= 1:
                # print(ts_code_list)
                if asset is not None:
                    download_stock_hist(freq, ts_code_list, asset)
                else:
                    download_stock_hist(freq, ts_code_list)
                # download_stock_hist(freq, ts_code_list)
                time.sleep(1)
                mark_jiuzhuan(freq, ts_code_list)
                time.sleep(1)
                mark_dingdi_listed(freq, ts_code_list)
                time.sleep(1)
                mark_tupo_yali_listed(freq, ts_code_list)
                time.sleep(1)
                mark_diepo_s_listed(freq, ts_code_list)
                time.sleep(1)
                mark_wm_listed(freq, ts_code_list)
                time.sleep(1)
                mark_junxian_bs_listed(freq, ts_code_list)
        elif freq is None:
            print('freq must be provided')
        else:
            if asset is not None:
                download_stock_hist(freq, asset)
            else:
                download_stock_hist(freq)
            # download_stock_hist(freq)
            time.sleep(1)
            mark_jiuzhuan(freq)
            time.sleep(1)
            mark_dingdi_listed(freq)
            time.sleep(1)
            mark_tupo_yali_listed(freq)
            time.sleep(1)
            mark_diepo_s_listed(freq)
            time.sleep(1)
            mark_wm_listed(freq)
            time.sleep(1)
            mark_junxian_bs_listed(freq)
