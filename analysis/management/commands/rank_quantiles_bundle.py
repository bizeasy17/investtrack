import time
from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from analysis.strategy_quantiles_stats import rank_updown_test,rank_target_pct_test
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
        strategy_codes = ['jiuzhuan_b', 'jiuzhuan_s', 'dibu_b', 'dingbu_s', 'w_di', 'm_ding', 'tupo_yali_b',
                         'diepo_zhicheng_s', 'ma25_zhicheng_b', 'ma25_tupo_b', 'ma25_diepo_s', 'ma25_yali_s']
        
        if freq is None:
            print('please input the mandatory freq')
            return
        
        if strategy_code is not None:
            rank_updown_test(strategy_code, freq)
            rank_target_pct_test(strategy_code, freq)
        else:
            for scode in strategy_codes:
                rank_updown_test(scode, freq)
                rank_target_pct_test(scode, freq)
