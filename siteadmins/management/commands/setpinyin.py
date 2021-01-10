from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from search.utils import pinyin_abbrev
from stockmarket.models import StockNameCodeMap

class Command(BaseCommand):
    help = 'Taking synch for company'

    def add_arguments(self, parser):
        # Named (optional) arguments
        pass

    def handle(self, *args, **options):
        print('set pinyin...')
        companies = StockNameCodeMap.objects.all()
        for company in companies:
            company.stock_name_pinyin = pinyin_abbrev(company.stock_name)
            print(company.stock_name)
            print(company.stock_name_pinyin)
            company.save()
        print('set pinyin finished...')

        

