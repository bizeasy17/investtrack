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

from analysis.dailybasic import process_industrybasic_quantile
from analysis.utils import next_date


logger = logging.getLogger(__name__)

# Create your views here.
def analysis_command(request, cmd, params):
    p = params.split(',')
    
    try:
        plist = params.split(',')
        if cmd == 'ibq':
            quantile = [.1, .25, .5, .75, .9]
            # get last end date
            next_dates = next_date()
            process_industrybasic_quantile(
                quantile, next_dates,)
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=500)
