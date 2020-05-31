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
    strategies = TradeStrategy.objects.exclude(applied_period=None).annotate(num_used=Count(
        'transactions')).annotate(num_s=num_s).annotate(num_f=num_f)
    for s in strategies:
        stat = TradeStrategyStat()
        stat.applied_period = s.applied_period
        # stat.parent_strategy = s.parent_strategy
        stat.name = s.name
        stat.creator = s.creator
        stat.count = s.num_used
        stat.success_count = s.num_s
        stat.fail_count = s.num_f
        if s.num_s + s.num_f != 0:
            stat.success_rate = round(s.num_s / (s.num_s + s.num_f) * 100, 2)
        else:
            stat.success_rate = 0
        stat.code = s.code
        stat.save()
    pass
