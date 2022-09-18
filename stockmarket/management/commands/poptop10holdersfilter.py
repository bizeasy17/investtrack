
# from analysis.models import IndustryBasicQuantileStat
from datetime import date, datetime
from django.core.management.base import BaseCommand, CommandError
from stockmarket.models import CompanyBasicFilter, CompanyTop10FloatHolders, CompanyTop10FloatHoldersFilter, CompanyTop10FloatHoldersStat, Industry, StockNameCodeMap
from search.utils import pinyin_abbrev

# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def handle(self, *args, **options):
        try:
            today = datetime.today()
            companies = StockNameCodeMap.objects.order_by('ts_code').all()
            for company in companies:
                try:
                    ann_date = None
                    hold_amount = 0
                    hold_pct = 0.0
                    # db = company.get_latest_daily_basic()
                    # if db is not None:
                        # print(company.top10_holder_date)
                    holder_stat = CompanyTop10FloatHoldersStat.objects.get(
                        company=company, end_date=company.top10_holder_date)
                    # if len(holder_stat) > 0:
                    #     for holder in holder_stat:
                    #         hold_amount += holder.hold_amount
                    #         ann_date = holder.announce_date
                    #     hold_pct = round(
                    #         hold_amount / (db.float_share * 10000) * 100, 2)
                        # print(ann_date)
                        # print(db.float_share)

                    try:
                        filter = CompanyTop10FloatHoldersFilter.objects.get(
                            ts_code=company.ts_code,)
                        filter.hold_pct = holder_stat.hold_pct
                        filter.hold_amount = holder_stat.hold_amount
                        filter.float_amount = holder_stat.float_amount
                        filter.announce_date = holder_stat.announce_date
                        filter.save()
                        print(
                            company.ts_code + ' top10 holder filter updated. ' + today.strftime('%Y%m%d HH:MM:SS'))
                    except CompanyTop10FloatHoldersFilter.DoesNotExist:
                        filter = CompanyTop10FloatHoldersFilter(
                            company=company, ts_code=company.ts_code, hold_amount=holder_stat.hold_amount, float_amount=holder_stat.float_amount,
                            announce_date=holder_stat.announce_date, end_date=holder_stat.end_date, hold_pct=holder_stat.hold_pct)
                        filter.save()
                        print(
                            company.ts_code + ' top10 holder filter created. ' + today.strftime('%Y%m%d HH:MM:SS'))
                    # else:
                    #     print(company.ts_code + ' daily basic not available. ' +
                    #           today.strftime('%Y%m%d %HH:%MM:%SS'))
                except Exception as err:
                    print(err)
        except Exception as err:
            print(err)
