
# from analysis.models import IndustryBasicQuantileStat
from django.core.management.base import BaseCommand, CommandError
from stockmarket.models import CompanyBasicFilter, Industry, StockNameCodeMap
from search.utils import pinyin_abbrev

# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def handle(self, *args, **options):
        try:
            industries = Industry.objects.all().exclude(pe_10pct=None)
            companies = StockNameCodeMap.objects.order_by('ts_code').all()
            for company in companies:
                try:
                    filter = CompanyBasicFilter.objects.filter(company=company).first()
                    if filter is None:
                        filter = CompanyBasicFilter(
                            company=company, ts_code=company.ts_code)
                        filter.save()
                        print(company.ts_code + ' filter created.')
                    else:
                        print(company.ts_code + ' filter already exist.')
                except Exception as err:
                    print(err)

                    
            for ind in industries:
                stocks = StockNameCodeMap.objects.filter(ind=ind).order_by('ts_code')
                print(ind.industry + ' in processing')
                for stock in stocks:
                    filter = CompanyBasicFilter.objects.get(company=stock)
                    db = stock.get_latest_daily_basic()
                    if db is not None:
                        if db.pe is not None and db.pe <= ind.pe_10pct if ind.pe_10pct is not None else 0 * 1.1:
                            filter.pe = 1
                        if db.pe is not None and (db.pe >= ind.pe_50pct * 0.9 and db.pe <= ind.pe_50pct * 1.1):
                            filter.pe = 2
                        if db.pe is not None and db.pe >= ind.pe_90pct * 0.9:
                            filter.pe = 3
                        if db.pe == 0 or db.pe is None:
                            filter.pe = -1

                        # if db.pe_ttm < ind.pe_10pct * 1.1:
                        #     filter.pe = 1
                        # if db.pe > ind.pe_50pct * 0.9 and db.pe < ind.pe_50pct * 1.1:
                        #     filter.pe = 2
                        # if db.pe > ind.pe_90pct * 0.9:
                        #     filter.pe = 3
                        # if db.pe == 0:
                        #     filter.pe = -1

                        if db.pb is not None and db.pb <= ind.pb_10pct * 1.1:
                            filter.pb = 1
                        if db.pb is not None and (db.pb >= ind.pb_50pct * 0.9 and db.pb <= ind.pb_50pct * 1.1):
                            filter.pb = 2
                        if db.pb is not None and db.pb >= ind.pb_90pct * 0.9:
                            filter.pb = 3

                        if db.ps is not None and db.ps <= ind.ps_10pct * 1.1:
                            filter.ps = 1
                        if db.ps is not None and (db.ps >= ind.ps_50pct * 0.9 and db.ps <= ind.ps_50pct * 1.1):
                            filter.ps = 2
                        if db.ps is not None and db.ps >= ind.ps_90pct * 0.9:
                            filter.ps = 3
                    
                        filter.save()
                        print(stock.ts_code + ' filter populated.')
                print(ind.industry + ' processed')
        except Exception as err:
            print(err)

