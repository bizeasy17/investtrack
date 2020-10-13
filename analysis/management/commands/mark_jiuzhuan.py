from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User
from analysis.analysis_jiuzhuan_cp import mark_jiuzhuan
from stockmarket.models import StockNameCodeMap
from analysis.utils import get_analysis_task, set_task_completed,get_trade_cal_diff


class Command(BaseCommand):
    help = 'Taking jiuzhuan for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--ts_code',
            type=str,
            help='Which ts_code you want to apply the snapshot',
        )
        # Named (mandatory) arguments
        parser.add_argument(
            '--freq',
            type=str,
            help='Which freq you want to apply the snapshot',
        )
        pass

    def handle(self, *args, **options):
        # print('test test')
        ts_code = options['ts_code']
        freq = options['freq']

        if freq is None:
            freq = 'D'
        
        if ts_code is not None and freq is not None:
            start_date = None
            end_date = None
            today = date.today()
            ts_code_list = ts_code.split(',')

            if ts_code_list is not None and len(ts_code_list) >= 1:
                for ts_code in ts_code_list:
                    try:
                        listed_company = StockNameCodeMap.objects.get(
                            ts_code=ts_code)
                        task = get_analysis_task(
                            ts_code, 'MARK_CP', 'jiuzhuan_bs', freq)
                        if task is not None:
                            atype = '1'  # 标记更新的股票历史记录
                            # 如何差额取之前的历史记录？9
                            if task.start_date == listed_company.list_date:
                                print('第一次处理，从上市日开始。。。')
                                atype = '0'  # 从上市日开始标记
                                start_date = task.start_date
                            else:
                                print('更新处理，从上一次更新时间-4d - 开盘日 开始...')
                                start_date = task.start_date - timedelta(days=get_trade_cal_diff(task.start_date))

                            mark_jiuzhuan(ts_code, freq, start_date,
                                          task.end_date, atype)
                            # print(task.start_date)
                            # print(task.end_date)
                            # set_task_completed(listed_company.ts_code, 'MARK_CP',
                            #                    freq, 'jiuzhuan_bs', task.start_date, task.end_date)
                        else:
                            print('no jiuzhuan mark cp task')
                    except Exception as e:
                        print(e)
