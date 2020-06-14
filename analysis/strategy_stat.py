from django.db.models import Count
from django.db.models import Q, F
from .models import TradeStrategyStat
from investors.models import TradeStrategy
import pandas as pd


def analyze_trade_strategy():
    num_s = Count('transactions', filter=Q(
        transactions__price__lt=F('transactions__sell_price'), transactions__is_sold=True, transactions__created_or_mod_by='human'))
    num_f = Count('transactions', filter=Q(
        transactions__price__gt=F('transactions__sell_price'), transactions__is_sold=True, transactions__created_or_mod_by='human'))
    strategies = TradeStrategy.objects.exclude(parent_strategy=None).annotate(num_used=Count(
        'transactions')).annotate(num_s=num_s).annotate(num_f=num_f)
    print(len(strategies))
    for s in strategies:
        try:
            stat = TradeStrategyStat.objects.get(
                applied_period=s.applied_period, code=s.ana_code.analysis_code)
        except Exception as error:
            stat = TradeStrategyStat()
            stat.applied_period = s.applied_period
            if s.category =='B':
                stat.category = '买策略'
            elif s.category == 'S':
                stat.category = '卖策略'
            elif s.category == 'H':
                stat.category = '持仓策略'
            stat.name = s.name
            stat.creator = s.creator
            stat.code = s.ana_code.analysis_code
        stat.count = s.num_used
        stat.success_count = s.num_s
        stat.fail_count = s.num_f
        if s.num_s + s.num_f != 0:
            stat.success_rate = round(s.num_s / (s.num_s + s.num_f) * 100, 2)
        else:
            stat.success_rate = 0
        stat.save()
    pass
