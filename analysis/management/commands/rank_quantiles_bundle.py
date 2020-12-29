import time
from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from analysis.strategy_quantiles_stats import rank_updown_test, rank_target_pct_test
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
        strategy_code = options['strategy_code']
        freq = options['freq']
        strategy_codes = ['jiuzhuan_count_b', 'jiuzhuan_count_s', 'dibu_b', 'dingbu_s', 'w_di',
                          'm_ding', 'tupo_b', 'diepo_s',
                          'ma25_zhicheng', 'ma25_tupo', 'ma25_diepo', 'ma25_yali',
                          'ma60_zhicheng', 'ma60_tupo', 'ma60_diepo', 'ma60_yali',
                          'ma200_zhicheng', 'ma200_tupo', 'ma200_diepo', 'ma200_yali', ]

        if freq is None:
            print('please input the mandatory freq')
            return

        if strategy_code is None:
            print('strategy code is mandatory')
            return

        if strategy_code not in strategy_codes:
            print('strategy code should be in the scope')
            print(strategy_codes)
            return

        rank_updown_test(strategy_code, freq)
        rank_target_pct_test(strategy_code, freq)
