import signal

from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from users.models import User
from analysis.dailybasic import download_dailybasic
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

        try:
            if start_date is not None:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except:
            print('date should be YYYY-mm-dd format')
            return

        try:
            if end_date is not None:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except:
            print('date should be YYYY-mm-dd format')
            return
        
        if freq is None:
            freq = 'D'

        download_dailybasic(ts_code, start_date,
                               end_date, freq)


# # 自定义信号处理函数
# def my_handler(signum, frame):
#     global stop
#     stop = True
#     print('进程被终止')

# # 设置相应信号处理的handler
# signal.signal(signal.SIGINT, my_handler)

# stop = False

# while True:
#     try:
#         if stop:
#             # 中断时需要处理的代码
#             break
#     except Exception as e:
#         print(str(e))
#         break
