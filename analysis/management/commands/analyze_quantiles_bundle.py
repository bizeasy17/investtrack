import time
from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from analysis.strategy_quantiles_stats import updown_pct_quantiles_stat,target_pct_quantiles_stat
from stockmarket.models import StockNameCodeMap


class Command(BaseCommand):
    '''
    select * from public.analysis_stockstrategytestlog where analysis_code='jiuzhuan_b' order by ts_code 

    select t1.datname AS db_name,  
        pg_size_pretty(pg_database_size(t1.datname)) as db_size
    from pg_database t1
    order by pg_database_size(t1.datname) desc;

    SELECT pg_size_pretty(pg_relation_size('public.analysis_bstrategyonfixedpcttest'));
    SELECT pg_size_pretty(pg_relation_size('public.analysis_bstrategyonpcttest'));
    SELECT pg_size_pretty(pg_relation_size('public.analysis_bstrategytestresultondays'));
    SELECT pg_size_pretty(pg_relation_size('public.analysis_stockhistorydaily'));
    SELECT pg_size_pretty(pg_relation_size('public.analysis_stockstrategytestlog'));

    SELECT nspname || '.' || relname AS "relation",
        pg_size_pretty(pg_total_relation_size(C.oid)) AS "total_size"
    FROM pg_class C
    LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
    WHERE nspname NOT IN ('pg_catalog', 'information_schema')
        AND C.relkind <> 'i'
        AND nspname !~ '^pg_toast'
    ORDER BY pg_total_relation_size(C.oid) DESC
    LIMIT 5;
    '''
    help = 'Taking snapshot for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--ts_code',
            type=str,
            help='Which ts_code you want to apply the snapshot',
        )
        # Named (optional) arguments
        parser.add_argument(
            '--strategy_code',
            type=str,
            help='Which strategy_code you want to apply the snapshot',
        )
        # Named (mandatory) arguments
        parser.add_argument(
            '--freq',
            type=str,
            help='Which freq you want to apply the snapshot',
        )
        pass

    def handle(self, *args, **options):
        ts_code = options['ts_code']
        strategy_code = options['strategy_code']
        freq = options['freq']
        strategy_codes = ['jiuzhuan_b', 'jiuzhuan_s', 'dibu_b', 'dingbu_s', 'w_di', 'm_ding', 'tupo_yali_b',
                         'diepo_zhicheng_s', 'ma25_zhicheng_b', 'ma25_tupo_b', 'ma25_diepo_s', 'ma25_yali_s']

        if freq is None:
            print('please input the mandatory freq')
            return

        if ts_code is not None:
            ts_code_list = ts_code.split(',')
            listed_companies = StockNameCodeMap.objects.filter(is_hist_downloaded=True, ts_code__in=ts_code_list)
        else:
            # print(ts_code_list)
            listed_companies = StockNameCodeMap.objects.filter(is_hist_downloaded=True)
            # print(len(listed_companies))
            # hist_list = []
        if listed_companies is not None and len(listed_companies) > 0:
            for listed_company in listed_companies:
                if strategy_code is not None:
                    updown_pct_quantiles_stat(strategy_code, listed_company.ts_code, listed_company.stock_name, freq)
                    target_pct_quantiles_stat(strategy_code, listed_company.ts_code, listed_company.stock_name, freq)
                else:
                    for scode in strategy_codes:
                        updown_pct_quantiles_stat(scode, listed_company.ts_code, listed_company.stock_name, freq)
                        target_pct_quantiles_stat(scode, listed_company.ts_code, listed_company.stock_name, freq)
