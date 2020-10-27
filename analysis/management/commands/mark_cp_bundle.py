import time
from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from analysis.analysis_diepo_s_cp import mark_diepo_s_listed
from analysis.analysis_dingdi import mark_dingdi_listed
from analysis.analysis_junxian_bs_cp import mark_junxian_bs_listed
from analysis.analysis_tupo_b_cp import mark_tupo_yali_listed
from analysis.analysis_wm_cp import mark_wm_listed
from analysis.stock_hist import handle_hist_download
from analysis.analysis_jiuzhuan_cp import handle_jiuzhuan_cp
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
        pass

    def handle(self, *args, **options):
        ts_code = options['ts_code']
        freq = options['freq']
        
        if freq is None:
            freq = 'D'

        handle_jiuzhuan_cp(ts_code, freq)
