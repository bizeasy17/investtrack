
from analysis.models import StockHistoryDaily
from django.core.management.base import BaseCommand, CommandError
from stockmarket.models import StockNameCodeMap

# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def handle(self, *args, **options):
        try:
            history_list = []
            companies = StockNameCodeMap.objects.all().order_by('-ts_code')
            for c in companies:
                close_results = StockHistoryDaily.objects.filter(
                    ts_code=c.ts_code, company=None)
                for history in close_results:
                    history.company = c
                    history_list.append(history)
                    # history.save()
                StockHistoryDaily.objects.bulk_update(history_list, ['company'])
                history_list.clear()
                print(c.ts_code + ' updated.')
        except Exception as err:
            print(err)

