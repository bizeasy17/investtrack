from datetime import date, datetime, timedelta

import pandas as pd
from analysis.models import StockHistoryDaily, StockHistoryDailyArc
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from investors.models import StockFollowing
from users.models import User

# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'
    CLOST_HISTORY = 'close_history'

    def add_arguments(self, parser):
        # Named (optional) arguments
        # Named (optional) arguments
        parser.add_argument(
            '--type',
            type=str,
            help='Which ts_code you want to apply the collect',
        )
        parser.add_argument(
            '--freq',
            type=str,
            help='Which freq you want to apply the collect',
        )
        parser.add_argument(
            '--period',
            type=str,
            help='Which start date you want to apply the collect',
        )

    def handle(self, *args, **options):
        # sys_event_list = ['MARK_CP']
        freq = options['freq']
        type = options['type']
        period = options['period']

        if period is None:
            period = 3

        if type is None:
            type = self.CLOST_HISTORY

        if freq is None:
            freq = 'D'

        archive_history_data(type, period, freq)


def archive_history_data(type, period, freq):
    hist_arc_list = []
    end_date = date.today()
    start_date = end_date - timedelta(days=365 * int(period))

    try:
        if type == Command.CLOST_HISTORY:
            print('archiving start for ' + type)
            close_hist = StockHistoryDailyArc.objects.filter(
                freq=freq, trade_date__gte=start_date, trade_date__lte=end_date).order_by('trade_date')

            for hist in close_hist:
                shda = StockHistoryDaily(ts_code=hist.ts_code, trade_date=hist.trade_date, open=hist.open, high=hist.high,
                                        low=hist.low, close=hist.close, pre_close=hist.pre_close, change=hist.change,
                                        pct_chg=hist.pct_chg, vol=hist.vol, amount=hist.amount, chg4=hist.chg4,
                                        jiuzhuan_count_b=hist.jiuzhuan_count_b, jiuzhuan_count_s=hist.jiuzhuan_count_s,
                                        ma25=hist.ma25, ma25_slope=hist.ma25_slope, ma60=hist.ma60, ma60_slope=hist.ma60_slope,
                                        ma200=hist.ma200, ma200_slope=hist.ma200_slope, slope=hist.slope, freq=hist.freq, )
                hist_arc_list.append(shda)
            StockHistoryDaily.objects.bulk_create(hist_arc_list)

            for hist in close_hist:
                hist.delete()
                
            print('archiving finished for ' + type)
    except Exception as err:
        print(err)
