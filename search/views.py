import pandas as pd
import pytz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

# Create your views here.


class SearchView(TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'public_pages/home.html'
    search_template = 'public_pages/search_result_single.html'
    search_template_list = 'public_pages/search_result_list.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'search'

    def get(self, request, *args, **kwargs):
        # req_user = request.user
        # if req_user is not None:
        #     pass
        # else:
        #     pass
        if len(request.GET) > 0:
            return render(request, self.search_template)
        else:
            return render(request, self.template_name)

