from datetime import date, datetime

from analysis.utils import generate_date_seq
from django.core.management.base import BaseCommand, CommandError

# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


class Command(BaseCommand):
    SHA_LIST_DATE = '1990-11-26'
    IND_BASIC_QUANTILE = 'INDUSTRY_BASIC_QUANTILE'

    def add_arguments(self, parser):
        # Named (optional) arguments
        # Named (optional) arguments
        parser.add_argument(
            '--type',
            type=str,
            help='Which tyoe you want to apply the collect',
        )
        parser.add_argument(
            '--freq',
            type=str,
            help='Which freq you want to apply the collect',
        )

    def handle(self, *args, **options):
        # sys_event_list = ['MARK_CP']
        type = options['type']
        freq = options['freq']
        list_date = datetime.strptime(self.SHA_LIST_DATE, '%Y-%m-%d').date()

        if type is None:
            type = self.IND_BASIC_QUANTILE

        if freq is None:
            freq = 'M'

        generate_date_seq(
            type, freq, list_date)
