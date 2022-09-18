
# from analysis.models import IndustryBasicQuantileStat
from datetime import date, datetime
from django.core.management.base import BaseCommand, CommandError
from analysis.models import StockHistoryIndicatorFilters, StockHistoryIndicators
from stockmarket.models import CompanyBasicFilter, CompanyTop10FloatHolders, CompanyTop10FloatHoldersFilter, Industry, StockNameCodeMap
from search.utils import pinyin_abbrev

# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'
    def add_arguments(self, parser):
        # Named (optional) arguments
        # Named (optional) arguments
        parser.add_argument(
            '--freq',
            type=str,
            help='Which ts_code you want to apply the download',
        )

    def handle(self, *args, **options):
        freq = options['freq']

        try:
            today = datetime.today()
            companies = StockNameCodeMap.objects.order_by('ts_code').all()
            for company in companies:
                try:
                    indic = company.get_latest_indicator(freq)
                    if indic is not None:
                        # print(company.top10_holder_date)
                        if freq == 'D':
                            # indic = StockHistoryIndicators.objects.filter(
                            #     company=company, trade_date=company.pop2eema_date, freq='D').first()
                            pop_date = company.pop2eema_date
                        if freq == 'W':
                            # indic = StockHistoryIndicators.objects.filter(
                            #     company=company, trade_date=company.pop2eema_date_w, freq='W').first()
                            pop_date = company.pop2eema_date_w
                        if freq == 'M':
                            # indic = StockHistoryIndicators.objects.filter(
                            #     company=company, trade_date=company.pop2eema_date_m, freq='M').first()
                            pop_date = company.pop2eema_date_m
                        
                        # indics = indic_d | indic_w | indic_m
                        if indic is not None:
                            try:
                                filter = StockHistoryIndicatorFilters.objects.get(
                                    ts_code=company.ts_code, freq=freq, trade_date=pop_date)
                                filter.var1 = indic.var1
                                filter.var2 = indic.var2
                                filter.var3 = indic.var3
                                filter.rsv = indic.rsv
                                filter.eema_b = indic.eema_b
                                filter.eema_s = indic.eema_s
                                filter.freq = indic.freq
                                filter.save()
                                print(
                                    company.ts_code + ' indicator rsv filter updated. ' + today.strftime('%Y%m%d %H:%M:%S'))
                            except StockHistoryIndicatorFilters.DoesNotExist:
                                filter = StockHistoryIndicatorFilters(
                                    company=company, ts_code=company.ts_code, var1=indic.var1, var2=indic.var2,
                                    var3=indic.var3, rsv=indic.rsv, eema_b=indic.eema_b, eema_s=indic.eema_s, freq=indic.freq, trade_date=pop_date,)
                                filter.save()
                                print(
                                    company.ts_code + ' indicator filter created. ' + today.strftime('%Y%m%d %HH:%MM:%SS'))
                    else:
                        print(company.ts_code + ' indicator not available. ' +
                              today.strftime('%Y%m%d %HH:%MM:%SS'))
                except Exception as err:
                    print(err)
        except Exception as err:
            print(err)
