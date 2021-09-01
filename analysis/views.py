import decimal
import logging
from calendar import monthrange
from datetime import date, datetime, timedelta

import pandas as pd
import pytz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from investors.models import StockFollowing
from stockmarket.models import StockNameCodeMap
from stockmarket.utils import get_realtime_quotes, get_stocknames

from analysis.dl_daily_basic import handle_daily_basic
from analysis.stock_hist import process_stock_download
from analysis.utils import (get_pct_val_from, get_qt_period_on_exppct,
                            get_qt_updownpct)

from .models import (BStrategyOnFixedPctTest, BStrategyOnPctTest,
                     PickedStocksMeetStrategy, StockHistoryDaily,
                     StrategyTestLowHigh)

logger = logging.getLogger(__name__)

# Create your views here.

