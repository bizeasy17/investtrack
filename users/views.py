# from calendar import monthrange
import calendar
import decimal
import locale
import logging
import os
from datetime import date, datetime, timedelta

import datedelta
import tushare as ts
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, View
from django.contrib.auth.password_validation import validate_password

from investors.models import StockFollowing, TradeStrategy
from stockmarket.models import StockNameCodeMap
from stocktrade.models import Transactions
from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot
from tradeaccounts.utils import calibrate_realtime_position

from .forms import UserTradeForm
from .models import User

locale.setlocale(locale.LC_ALL, '')

logger = logging.getLogger(__name__)

# Create your views here.
class UserProfileView(LoginRequiredMixin, View):
    # form_class = UserTradeForm
    # model = Transactions

    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'users/user_profile.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'user_profile'

    def get(self, request, *args, **kwargs):
        # username = self.kwargs['username']
        req_user = request.user
        if req_user is not None:
            user = User.objects.filter(
                id=req_user.id,)  # 前台需要添加view more...
            queryset = {
                'user': user,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})

class UserTradelogView(LoginRequiredMixin, View):
    # form_class = UserTradeForm
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'users/trade_log.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'trade_log'

    def get(self, request, *args, **kwargs):
        # username = self.kwargs['username']
        req_user = request.user
        stock_symbol = self.kwargs['symbol']
        if req_user is not None:
            tradedetails = Transactions.objects.filter(
                trader=req_user.id, stock_code=stock_symbol, created_or_mod_by='human')  # 前台需要添加view more...
            trade_positions = Positions.objects.filter(
                trader=req_user.id, is_liquidated=False).exclude(lots=0)
            strategies = TradeStrategy.objects.filter(creator=req_user.id)
            stocks_following = StockFollowing.objects.filter(
                trader=req_user.id,)
            stock_info = StockNameCodeMap.objects.get(stock_code=stock_symbol)
            queryset = {
                'symbol': stock_info.stock_code,
                'stock_name': stock_info.stock_name,
                'show_symbol': stock_info.ts_code,
                'market': stock_info.market,
                'det': tradedetails,
                'pos': trade_positions,
                'str': strategies,
                'fol': stocks_following,
            }
            return render(request, self.template_name, {self.context_object_name: queryset})
        else:
            return HttpResponseRedirect(reverse('404'))

# Create your function views here.
def file_upload(request):
    img_id = request.user.id
    if len(request.FILES) > 0:
        file = request.FILES['filePortrait']
        ext = file.name.split('.')[1] if file is not None else ''
        save_path = os.path.join(
            settings.MEDIA_ROOT, 'portraits', str(img_id) + '.' + ext)
        default_storage.save(save_path, file)
        return 'portraits/' + str(img_id) + '.' + ext


@login_required
def update_user_profile(request):
    if request.method == 'POST':
        trader = request.user
        picture_url= ''
        try:
            picture_url = file_upload(request)
            data = request.POST.copy()
            username = data.get("username")
            email = data.get('email')
            password = data.get('pass')
            # lastname = data.get('lastName')
            name = data.get('name')
            location = data.get('location')
            job_title = data.get('jobTitle')
            # bio = data.get('bio')
            short_bio = data.get('shortBio')
            # 更新相关用户字段
            # trader.email = email
            # trader.firstname = firstname
            # trader.lastname = lastname
            trader.email = email
            trader.name = name
            trader.location = location
            trader.job_title = job_title
            trader.set_password(password)
            # trader.bio = bio
            trader.short_bio = short_bio
            if picture_url is not None and picture_url != '': # 如果上传头像不为空，就更新
                trader.picture = picture_url
            # if direction == 'b':
            is_ok = trader.save()
            return JsonResponse({'code': 'success', 'message': _('更新成功')}, safe=False)
        except Exception as e:
            logger.error(e)

        # else:
        #     return JsonResponse({'code': 'error', 'message': _('更新失败')}, safe=False)
    return JsonResponse({'code': 'error', 'message': _('更新失败')}, safe=False)

def get_week_of_month(year, month, day):
    """
    获取指定的某天是某个月中的第几周
    周一作为一周的开始
    """
    end = int(datetime.datetime(year, month, day).strftime("%W"))
    begin = int(datetime.datetime(year, month, 1).strftime("%W"))
    return end - begin + 1


# class UserDetailView(LoginRequiredMixin, DetailView):
#     model = User

# custom 404, 403, 500 pages


def page_not_found_view(request, exception):
     # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'pages/404.html'
    return render(request, template_name)
