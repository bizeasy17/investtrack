from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.xuangu.pick_stocks import handle_stocks_pick
from stockmarket.models import StockNameCodeMap


class Command(BaseCommand):
    '''
    1. 判断数据已经下载？如果没有，就下载
    2. 判断关键点是否已经标注？如果没有，就标注
    3. 如果上述条件符合，则将所有符合策略选股条件的数据存入选股表
    4. 结束
    '''
    help = 'Xuangu for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        # Named (optional) arguments
        parser.add_argument(
            '--freq',
            type=str,
            help='Which freq you want to apply the download',
        )
        parser.add_argument(
            '--forcerun',
            type=str,
            help='force to run anyway',
        )
        # parser.add_argument(
        #     '--end_date',
        #     type=str,
        #     help='Which end date you want to apply the download',
        # )
        pass

    def handle(self, *args, **options):
        freq = options['freq']
        force_run = options['forcerun']
        # end_date = options['end_date']

        if freq is None:
            freq = 'D'
        
        if force_run is None:
            force_run = '0'

        handle_stocks_pick(freq, force_run)
