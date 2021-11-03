
from analysis.models import StockHistoryDaily
from django.core.management.base import BaseCommand, CommandError
from stockmarket.models import StockNameCodeMap, Industry, CompanyBasic, Province, City
from search.utils import pinyin_abbrev

# from analysis.utils import init_eventlog, set_event_completed, is_event_completed


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def handle(self, *args, **options):
        try:
            companies_bef = CompanyBasic.objects.filter(
            ).order_by().values('province', 'city').distinct()
            # print(len(companies_bef))
            # companies = StockNameCodeMap.objects.all()
            for c in companies_bef:
                print(c['province'])
                print(c['city'])
                if c['province'] is not None and c['city'] is not None:
                    p = Province.objects.filter(name=c['province']).first()
                    if p is None:
                        prov = Province(name=c['province'], province_pinyin=pinyin_abbrev(
                            c['province']))
                        prov.save()
                        print(c['province'] + ' created.')
                    else:
                        prov = p

                    ct = City.objects.filter(
                        name=c['city'], province=prov,).first()
                    if ct is None:
                        city = City(name=c['city'], province=prov, city_pinyin=pinyin_abbrev(
                            c['city']))
                        city.save()

                        print(c['city'] + ' created.')
                    else:
                        city = ct

                    cb = CompanyBasic.objects.filter(
                        province=c['province'], city=c['city']).exclude(shengfen__isnull=False).exclude(chengshi__isnull=False)
                    for b in cb:
                        b.shengfen = prov
                        b.chengshi = city
                        b.save()
                        print(prov.name + ',' + city.name + ' FK updated for ' +
                              b.ts_code + ' CompanyBasic.')

                    companies = StockNameCodeMap.objects.filter(
                        area=c['province']).exclude(province__isnull=False)
                    for company in companies:
                        company.province = prov
                        company.save()
                        print(prov.name + ' FK updated for ' +
                              company.ts_code + ' StockNameCode.')
        except Exception as err:
            print(err)
