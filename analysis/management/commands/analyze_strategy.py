from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.strategy_stat import analyze_trade_strategy


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--period',
            type=str,
            help='Which period you want to apply the snapshot',
        )
        pass

    def handle(self, *args, **options):
        period = options['period']
        if period == 'daily':
            pass
        elif period == 'weekly':
            pass
        elif period == 'monthly':
            pass
        analyze_trade_strategy()
