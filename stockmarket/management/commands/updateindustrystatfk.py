
from analysis.models import IndustryBasicQuantileStat
from django.core.management.base import BaseCommand, CommandError
from stockmarket.models import Industry
from search.utils import pinyin_abbrev

# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def handle(self, *args, **options):
        try:
            industries = Industry.objects.all()
            # companies = StockNameCodeMap.objects.all()
            for ind in industries:
                ibqs = IndustryBasicQuantileStat.objects.filter(industry=ind.industry)
                for ibq in ibqs:
                    ibq.ind = ind
                    ibq.save()
                print(ind.industry + ' FK updated.')
        except Exception as err:
            print(err)

