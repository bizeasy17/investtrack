from datetime import date, datetime, timedelta

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from analysis.algorithm import calc_enhanced_rsv
from analysis.commands import pop_rsv_indic
from analysis.models import StockHistoryDaily, StockHistory, StockHistoryIndicators
from stockmarket.models import StockNameCodeMap


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        # Named (optional) arguments
        parser.add_argument(
            '--ts_code',
            type=str,
            help='Which ts_code you want to apply the collect',
        )
        parser.add_argument(
            '--freq',
            type=str,
            help='Which freq you want to apply the collect',
        )
        parser.add_argument(
            '--type',
            type=str,
            help='Which start date you want to apply the collect',
        )

        parser.add_argument(
            '--update_flag',
            type=str,
            help='Which start date you want to apply the collect',
        )

    def handle(self, *args, **options):
        # sys_event_list = ['MARK_CP']
        freq = options['freq']
        ts_code = options['ts_code']
        type = options['type']
        update_flag = options['update_flag']

        # if period is None:
        #     period = '60'

        if freq is None:
            freq = 'D'

        # if update_flag is None:
        #     update_flag = 0

        if ts_code is None:
            return

        if type == 'rsv+':
            pop_rsv_indic(ts_code, freq=freq,)
        
        # end_date = date.today()
        # if freq == 'D':
        #     hist = StockHistoryDaily.objects.filter(
        #         ts_code=ts_code, freq=freq).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('trade_date')
        #     # print(hist)
        # elif freq == 'W' or freq == 'M':
        #     hist = StockHistory.objects.filter(
        #         ts_code=ts_code, freq=freq).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('trade_date')

        # df = pd.DataFrame(hist)
        # # print(df.head())
        # enhanced_ema(df, update_flag=int(update_flag))
        # print(df['vol'].head())
        # print(b)
        # print(c)
        # print(d)
        # print(e)
        # print(f)
