import pandas as pd
import logging
import pytz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from users.models import UserActionTrace, UserQueryTrace
from analysis.utils import get_ip
from stockmarket.models import StockNameCodeMap
from investors.models import StockFollowing
# Create your views here.

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'zixuan/home.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'zixuan'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        # if req_user is not None:
        #     pass
        # else:
        #     pass
        stk_ind_dic = {}
        stk_dic = {}
        try:
            industries = StockFollowing.objects.order_by().values('industry').distinct()
            if len(industries) > 0:
                for ind in industries:
                    stocks = StockFollowing.objects.filter(
                        industry=ind['industry'])
                    for stk in stocks:
                        stk_dic[stk.ts_code] = stk.stock_name
                    stk_ind_dic[ind['industry']] = stk_dic
                    stk_dic = {}
        except Exception as err:
            logger.err(err)

        return render(request, self.template_name, {self.context_object_name: stk_ind_dic})

        
