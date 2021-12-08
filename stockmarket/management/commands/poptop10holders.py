
# from analysis.models import IndustryBasicQuantileStat
from datetime import date, datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Sum
from stockmarket.models import CompanyBasicFilter, CompanyTop10FloatHolders, CompanyTop10FloatHoldersFilter, CompanyTop10FloatHoldersStat, Industry, StockNameCodeMap
from search.utils import pinyin_abbrev

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

    def handle(self, *args, **options):
        ts_code = options['ts_code']

        try:
            today = datetime.today()
            if ts_code is None:
                companies = StockNameCodeMap.objects.filter(
                    asset='E').order_by('ts_code')
            else:
                companies = StockNameCodeMap.objects.filter(ts_code=ts_code)

            for company in companies:
                try:
                    # ann_date = None
                    # hold_amount = 0
                    # hold_pct = 0.0
                    # if db is not None:
                    # print(company.top10_holder_date)
                    stat = CompanyTop10FloatHoldersStat.objects.filter(
                        company=company).order_by('-end_date').first()
                    print(stat.end_date)
                    # return
                    if stat is not None and stat.end_date < company.top10_holder_date:
                        # Province.objects.annotate(count_num=Count('city_province')).values(
                        #     'name', 'count_num').order_by('-count_num')[0:6]
                        holders = CompanyTop10FloatHolders.objects.values('announce_date', 'end_date', 'ts_code').filter(
                            ts_code=company.ts_code, end_date__gt=stat.end_date).annotate(
                            total_amount=Sum('hold_amount'))
                    else:
                        holders = CompanyTop10FloatHolders.objects.filter(
                            ts_code=company.ts_code,).values('announce_date', 'end_date', 'ts_code').annotate(total_amount=Sum('hold_amount'))
                    # print(len(holders))
                    # return
                    for holder in holders:
                        # print(holders)
                        #     hold_amount += holder.hold_amount
                        #     ann_date = holder.announce_date
                        db = company.get_daily_basic_by_date(
                            holder['end_date'])

                        if db is None:
                            print(company.ts_code + ' daily basic not available. ' +
                                  datetime.now().strftime('%Y%m%d %H:%M:%S'))
                        else:
                            # hold_pct = round(
                            #     holder.total_amount / (db.float_share * 10000) * 100, 2)
                            # print(holder['announce_date'])
                            # print(holder['end_date'])
                            # print(holder['total_amount'])

                            try:
                                top10_stat = CompanyTop10FloatHoldersStat.objects.get(
                                    ts_code=company.ts_code, end_date=holder['end_date'])
                                top10_stat.hold_pct = round(holder['total_amount'] / (
                                    db.float_share * 10000), 2)
                                top10_stat.hold_amount = holder['total_amount']
                                top10_stat.float_amount = round(db.float_share * 10000)
                                top10_stat.announce_date = holder['announce_date']
                                top10_stat.end_date = holder['end_date']
                                top10_stat.close = db.close
                                top10_stat.pe = db.pe
                                top10_stat.pe_ttm = db.pe_ttm
                                top10_stat.pb = db.pb
                                top10_stat.ps = db.ps
                                top10_stat.ps_ttm = db.ps_ttm
                                top10_stat.save()
                                # print(
                                #     company.ts_code + ' top10 holder filter updated. ' + today.strftime('%Y%m%d %H:%M:%S'))
                            except CompanyTop10FloatHoldersStat.DoesNotExist:
                                top10_stat = CompanyTop10FloatHoldersStat(
                                    company=company, ts_code=company.ts_code, hold_amount=holder[
                                        'total_amount'], float_amount=round(db.float_share * 10000),
                                    announce_date=holder['announce_date'], end_date=holder['end_date'], 
                                    hold_pct=round(holder['total_amount'] / (db.float_share * 10000), 2),
                                    close=db.close, pe=db.pe, pe_ttm=db.pe_ttm, pb=db.pb, ps=db.ps, ps_ttm=db.ps_ttm)
                                top10_stat.save()
                                # print(
                                #     company.ts_code + ' top10 holder filter created. ' + today.strftime('%Y%m%d %H:%M:%S'))
                    print(company.ts_code + ' top10 holder created. ' + datetime.now().strftime('%Y%m%d %H:%M:%S'))
                except Exception as err:
                    print(err)
        except Exception as err:
            print(err)
