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
# Create your views here.

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'paiming/home.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'paiming'

    def get(self, request, *args, **kwargs):
        req_user = request.user
        # if req_user is not None:
        #     pass
        # else:
        #     pass
        try:
            if len(request.GET) > 0:
                # query_trace = UserQueryTrace(query_string=request.GET['q'], request_url=request.path, ip_addr=get_ip(request), uid=req_user)
                # query_trace.save()
                return render(request, self.search_template, {self.context_object_name: {'ts_code':request.GET['q']}})
            else:
                return render(request, self.template_name)
        except Exception as err:
            logger.error(err)
