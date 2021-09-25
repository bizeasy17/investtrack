from datetime import date, datetime

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from analysis.dailybasic import process_industrybasic_quantile
from analysis.utils import generate_date_seq, next_date, apply_analysis_date
# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


class Command(BaseCommand):
    SHA_LIST_DATE = '1990-11-26'
    IND_BASIC_QUANTILE = 'INDUSTRY_BASIC_QUANTILE'

    help = 'Taking snapshot for investors trade account'
    list_date = datetime.strptime(SHA_LIST_DATE, '%Y-%m-%d').date()

    def add_arguments(self, parser):
        # Named (optional) arguments
        # Named (optional) arguments
        parser.add_argument(
            '--industry',
            type=str,
            help='Which industry you want to apply the collect',
        )
        parser.add_argument(
            '--quantile',
            type=str,
            help='Which quantile you want to apply the collect',
        )
        parser.add_argument(
            '--date',
            type=str,
            help='Which date you want to apply the collect',
        )
        parser.add_argument(
            '--test',
            type=str,
            help='test print',
        )

    def handle(self, *args, **options):
        # sys_event_list = ['MARK_CP']
        industry = options['industry']
        quantile = options['quantile']
        snap_date = options['date']
        test = options['test']

        if quantile is None:
            quantile = [.1, .25, .5, .75, .9]

        if snap_date is not None:
            snap_date = datetime.strptime(snap_date, '%Y-%m-%d')

        # get last end date
        generate_date_seq(self.IND_BASIC_QUANTILE, 'M', self.list_date)
        next_dates = next_date(self.IND_BASIC_QUANTILE)
        # start_date + timedelta(days=monthrange(start_date.year, start_date.month)[1])

        # this_month_end = datetime.datetime(
        #     now.year, now.month, calendar.monthrange(now.year, now.month)[1])
        
        process_industrybasic_quantile(
            quantile, next_dates, self.IND_BASIC_QUANTILE)

        
