from investors.models import StockFollowing
import pandas as pd
from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from users.models import User
from analysis.models import StockHistoryDaily
from analysis.models import StockQuantileStat
from investors.models import StockFollowing
# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


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
            '--period',
            type=str,
            help='Which start date you want to apply the collect',
        )
        parser.add_argument(
            '--quantile',
            type=str,
            help='Which quantile you want to apply the collect',
        )

    def handle(self, *args, **options):
        # sys_event_list = ['MARK_CP']
        freq = options['freq']
        ts_code = options['ts_code']
        period = options['period']
        quantile = options['quantile']

        if period is None:
            period = '1,3,5,10,99'

        if quantile is None:
            quantile = '0.1,0.25,0.5,0.75,0.9'

        if freq is None:
            freq = 'D'

        if ts_code is None:
            stocks = StockFollowing.objects.filter().values('ts_code').distinct()
            if stocks is not None and len(stocks) > 0:
                for stock in stocks:
                    collect_close_quantile(stock['ts_code'], period, quantile,
                                           freq)


def collect_close_quantile(ts_code, period, quantile,
                           freq):
    period_list = period.split(',')
    quantile_list = quantile.split(',')
    for p in period_list:
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * int(p))

        close_results = StockHistoryDaily.objects.filter(
            ts_code=ts_code, freq=freq, trade_date__gte=start_date, trade_date__lte=end_date).order_by('trade_date').values('close')

        df = pd.DataFrame(close_results, columns=['close'])

        for quantile in quantile_list:
            close_qt_price = round(df.close.quantile([float(quantile)]),2)
            
            try:
                stock_qt_stat = StockQuantileStat.objects.get(
                    ts_code=ts_code, stat_type='CLOSE', period=int(p), quantile=float(quantile), freq=freq)
                print('update calculation ' + p + 'yr quantile ' + quantile + ' for ' + ts_code)

                stock_qt_stat.price = close_qt_price
                stock_qt_stat.save()
            except Exception as err:
                print('new calculation ' + p + 'yr quantile ' +
                      quantile + ' for ' + ts_code)
                new_stat = StockQuantileStat(
                    ts_code=ts_code, stat_type='CLOSE', period=p, quantile=float(quantile), price=close_qt_price, freq=freq)
                new_stat.save()
