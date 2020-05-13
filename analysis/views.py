import decimal
import logging
from datetime import date, datetime, timedelta

import pytz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from investors.models import StockFollowing, TradeStrategy
from stockmarket.models import StockNameCodeMap
from .models import TradeStrategyStat
from .strategy_stat import calc_strategy_on_days

logger = logging.getLogger(__name__)

# Create your views here.


class AnalysisHomeView(LoginRequiredMixin, TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'analysis/index.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'analysis'

def strategies_by_category(strategy_ctg):
    
    pass

def bstrategy_test_result_incr(strategy, stock_symbol, test_period):
    pass

def bstrategy_test_result_drop(strategy, stock_symbol, test_period):
    pass

def sstrategy_test_result_incr(strategy, stock_symbol, test_period):
    pass

def sstrategy_test_result_drop(strategy, stock_symbol, test_period):
    pass