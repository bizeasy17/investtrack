from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.stock_hist import handle_hist_download
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
        pass

    def handle(self, *args, **options):
        sys_event_list = ['MARK_CP']
        freq = options['freq']
        ts_code = options['ts_code']
        asset = options['asset']
        start_date = options['start_date']
        end_date = options['end_date']

        if freq is None:
            freq = 'D'

        if asset is None:
            asset = 'E'  # 股票， I - 指数

        handle_hist_download(ts_code, start_date, end_date,
                             asset, freq, sys_event_list)
