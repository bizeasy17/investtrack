from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.stock_hist import download_stock_hist
from stockmarket.models import StockNameCodeMap
from analysis.utils import hist_downloaded, last_download_date, generate_systask, log_download_hist


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
            '--asset',
            type=str,
            help='Which asset you want to apply the download',
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
        sdate = options['start_date']
        edate = options['end_date']

        if freq is None:
            freq = 'D'

        if asset is None:
            asset = 'E'

        if ts_code is not None and freq is not None:
            start_date = None
            end_date = None
            today = date.today()
            ts_code_list = ts_code.split(',')

            if ts_code_list is not None and len(ts_code_list) >= 1:
                for ts_code in ts_code_list:
                    try:
                        listed_company = StockNameCodeMap.objects.get(ts_code=ts_code)
                        last_date = last_download_date(ts_code, 'HIST_DOWNLOAD', freq)
                        
                        if sdate is not None and edate is not None: # 给定下载开始和结束时间
                            start_date = sdate
                            end_date = edate
                            download_stock_hist(
                                ts_code, listed_company.list_date, today, asset, freq, )
                        else: # 根据日志记录下载相应历史记录    
                            if last_date is not None:
                                if last_date[1] < today: 
                                    # 已完成首次下载
                                    # print('not first time')
                                    start_date = last_date[1] + timedelta(days=1)
                                    download_stock_hist(
                                        ts_code, last_date[1] + timedelta(days=1), today, asset, freq, )
                            else:
                                # 需要进行首次下载
                                # print('first time')
                                start_date = listed_company.list_date
                                download_stock_hist(
                                    ts_code, listed_company.list_date, today, asset, freq, )
                            end_date = today
                        if start_date is not None and end_date is not None:
                            log_download_hist(ts_code, 'HIST_DOWNLOAD', start_date, end_date, freq)
                            generate_systask(ts_code, freq, start_date, end_date, sys_event_list)
                        else:
                            print('no history to be downloaded for give period')
                    except Exception as e:
                        print(e)
