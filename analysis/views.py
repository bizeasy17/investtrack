import decimal
import logging
from datetime import date, datetime, timedelta

import pytz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from investors.models import StockFollowing, TradeStrategy
from stockmarket.models import StockNameCodeMap

logger = logging.getLogger(__name__)

# Create your views here.


class AnalysisHomeView(LoginRequiredMixin, View):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'analysis/index.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'analysis'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        if req_user is not None:
            try:
                strategy_list = TradeStrategy.objects.filter(is_visible=True)
                
                return render(request, self.template_name, {self.context_object_name: queryset})
            except Exception as e:
                logger.error(e)
                return HttpResponse(status=404)
        else:
            return HttpResponse(status=404)

