from stockmarket.models import StockNameCodeMap
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
from investors.models import StockFollowing
# Create your views here.

logger = logging.getLogger(__name__)


class SearchView(TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'public_pages/home.html'
    search_template = 'public_pages/stock_dashboard.html'
    # search_template_list = 'public_pages/search_result_list.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'search_single'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        # if req_user is not None:
        #     pass
        # else:
        #     pass
        try:
            if len(request.GET) > 0:
                selected = False

                if not req_user.is_anonymous:
                    sel_stocks = StockFollowing.objects.filter(
                        trader=req_user, ts_code=request.GET['q'])
                    if sel_stocks is not None and len(sel_stocks) > 0:
                        selected = True
                    # query_trace = UserQueryTrace(query_string=request.GET['q'], request_url=request.path, ip_addr=get_ip(request), uid=req_user)
                    # query_trace.save()
                company = StockNameCodeMap.objects.get(
                    ts_code=request.GET['q'])
                return render(request, self.search_template, {self.context_object_name: {'ts_code': request.GET['q'], 'stock_name': company.stock_name, 'industry': company.industry, 'selected': selected}})
            else:
                return render(request, self.template_name)
        except Exception as err:
            logger.error(err)
            return render(request, self.search_template, {self.context_object_name: {'err_message': _('抱歉，未查询到相关股票，请重试！'), 'd_none': 'd-none'}})
