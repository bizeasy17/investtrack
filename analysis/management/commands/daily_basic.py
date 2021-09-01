from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from users.models import User
from analysis.dl_daily_basic import handle_daily_basic
# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        # Named (optional) arguments
        parser.add_argument(
            '--ts_code',
            type=str,
            help='Which ts_code you want to apply the download',
        )
        parser.add_argument(
            '--freq',
            type=str,
            help='Which freq you want to apply the download',
        )
        parser.add_argument(
            '--start_date',
            type=str,
            help='Which start date you want to apply the download',
        )
        parser.add_argument(
            '--end_date',
            type=str,
            help='Which end date you want to apply the download',
        )

    def handle(self, *args, **options):
        # sys_event_list = ['MARK_CP']
        freq = options['freq']
        ts_code = options['ts_code']
        start_date = options['start_date']
        end_date = options['end_date']
        
        if freq is None:
            freq = 'D'

        handle_daily_basic(ts_code, start_date,
                               end_date, freq)
