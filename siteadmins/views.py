import tushare as ts
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, View


# Create your views here.
class SiteAdminGenericView(LoginRequiredMixin, View):
    # form_class = UserTradeForm
    # model = TradeRec

    # template_name属性用于指定使用哪个模板进行渲染
    default_template_name = 'siteadmin/dashboard.html'
    site_settings_template_name = 'siteadmin/settings.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'admin_dashboard'

    def get(self, request, *args, **kwargs):
        module_name = self.kwargs['module_name']
        req_user = request.user
        if req_user is not None and req_user.is_superuser:
            if module_name is not None:
                if module_name == 'dashboard':
                    return render(request, self.default_template_name)
                elif module_name == 'settings':
                    return render(request, self.site_settings_template_name)
                else:
                    return render(request, self.default_template_name)
        else:
            return HttpResponseRedirect(reverse('404'))   
