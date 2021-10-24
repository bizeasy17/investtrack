
from analysis.models import AnalysisDateSeq, IndustryBasicQuantileStat, StockHistoryDaily
from django.core.management.base import BaseCommand, CommandError
from stockmarket.models import StockNameCodeMap, Industry

# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def handle(self, *args, **options):
        try:
            a = {}
            b = []
            date_seq = AnalysisDateSeq.objects.filter().order_by('-analysis_date').first()
            industries = Industry.objects.all()
            # ibqs_list = IndustryBasicQuantileStat.objects.filter(
            #     snap_date=date_seq.analysis_date)
            for ind in industries:
                print('start industry ' + ind.industry)
                # print(date_seq.analysis_date)
                daily_basic_list = ind.get_latest_daily_basic().filter(
                    snap_date=date_seq.analysis_date)
                for daily_basic in daily_basic_list:
                    # a[daily_basic.quantile] = {daily_basic.basic_type: daily_basic.quantile_val}
                    # pass
                    if daily_basic.basic_type == 'pe' and daily_basic.quantile == 0.1:
                        ind.pe_10pct = daily_basic.quantile_val
                    if daily_basic.basic_type == 'pe' and daily_basic.quantile == 0.5:
                        ind.pe_50pct = daily_basic.quantile_val
                    if daily_basic.basic_type == 'pe' and daily_basic.quantile == 0.9:
                        ind.pe_90pct = daily_basic.quantile_val

                    if daily_basic.basic_type == 'pb' and daily_basic.quantile == 0.1:
                        ind.pb_10pct = daily_basic.quantile_val
                    if daily_basic.basic_type == 'pb' and daily_basic.quantile == 0.5:
                        ind.pb_50pct = daily_basic.quantile_val
                    if daily_basic.basic_type == 'pb' and daily_basic.quantile == 0.9:
                        ind.pb_90pct = daily_basic.quantile_val

                    if daily_basic.basic_type == 'ps' and daily_basic.quantile == 0.1:
                        ind.ps_10pct = daily_basic.quantile_val
                    if daily_basic.basic_type == 'ps' and daily_basic.quantile == 0.5:
                        ind.ps_50pct = daily_basic.quantile_val
                    if daily_basic.basic_type == 'ps' and daily_basic.quantile == 0.9:
                        ind.ps_90pct = daily_basic.quantile_val

                    ind.stock_count = daily_basic.stk_quantity
                    ind.snap_date = date_seq.analysis_date
                # ind = Industry.objects.filter(industry=ibqs.industry)
                ind.save()
                print(ind.industry + ' updated.')
        except Exception as err:
            print(err)
