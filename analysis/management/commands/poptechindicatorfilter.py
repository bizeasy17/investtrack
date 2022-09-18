
# from analysis.models import IndustryBasicQuantileStat
from datetime import date, datetime
from django.core.management.base import BaseCommand, CommandError
from stockmarket.models import StockNameCodeMap
from analysis.models import CompanyTechIndicatorFilters
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
                    db = company.get_latest_rsvplus_indicators()
                    if db is not None:
                        # print(company.top10_holder_date)
                        holders = CompanyTechIndicatorFilters.objects.filter(
                            company=company, end_date=company.top10_holder_date)
                        if len(holders) > 0:
                            for holder in holders:
                                hold_amount += holder.hold_amount
                                ann_date = holder.announce_date
                            hold_pct = round(
                                hold_amount / (db.float_share * 10000) * 100, 2)
                            # print(ann_date)
                            # print(db.float_share)

                            try:
                                filter = CompanyTechIndicatorFilters.objects.get(
                                    ts_code=company.ts_code, end_date=company.top10_holder_date)
                                filter.hold_pct = hold_pct
                                filter.hold_amount = hold_amount
                                filter.float_amount = db.float_share * 10000
                                filter.announce_date = ann_date
                                filter.save()
                                print(
                                    company.ts_code + ' top10 holder filter updated. ' + today.strftime('%Y%m%d HH:MM:SS'))
                            except CompanyTechIndicatorFilters.DoesNotExist:
                                filter = CompanyTechIndicatorFilters(
                                    company=company, ts_code=company.ts_code, hold_amount=hold_amount, float_amount=db.float_share * 10000,
                                    announce_date=ann_date, end_date=company.top10_holder_date, hold_pct=hold_pct)
                                filter.save()
                                print(
                                    company.ts_code + ' top10 holder filter created. ' + today.strftime('%Y%m%d HH:MM:SS'))
                    else:
                        print(company.ts_code + ' daily basic not available. ' +
                              today.strftime('%Y%m%d %HH:%MM:%SS'))
                except Exception as err:
                    print(err)
        except Exception as err:
            print(err)
