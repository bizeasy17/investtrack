
from analysis.models import StockHistoryDaily
from django.core.management.base import BaseCommand, CommandError
from stockmarket.models import StockNameCodeMap, Industry
from search.utils import pinyin_abbrev

# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def handle(self, *args, **options):
        try:
            companies_bef = StockNameCodeMap.objects.filter(asset='E').order_by().values('industry').distinct()
            # companies = StockNameCodeMap.objects.all()
            for c in companies_bef:
                if c['industry'] is not None:
                    try:
                        i = Industry.objects.get(industry=c['industry'])
                    except Industry.DoesNotExist:
                        i = Industry(industry=c['industry'], industry_pinyin=pinyin_abbrev(
                            c['industry']))
                        i.save()
                        print(c['industry'] + ' created.')

                    companies_aft = StockNameCodeMap.objects.filter(industry=c['industry'])
                    for c in companies_aft:
                        c.ind = i
                        c.save()
                        print(i.industry + ' FK updated for '+ c.ts_code +' StockNameCode.')
        except Exception as err:
            print(err)

