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
    template_name = 'hongguan/home.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'hongguan'

    def get(self, request, *args, **kwargs):
        try:
            return render(request, self.template_name)
        except Exception as err:
            logger.error(err)
