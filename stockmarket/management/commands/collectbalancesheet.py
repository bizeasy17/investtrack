
import tushare as ts
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
# from analysis.utils import init_eventlog, set_event_completed, is_event_completed
from search.utils import pinyin_abbrev
from stockmarket.utils import collect_balance_sheet
from users.models import User


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

    def handle(self, *args, **options):
        ts_code = options['ts_code']
        collect_balance_sheet(ts_code)
