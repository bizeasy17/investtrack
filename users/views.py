from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView, DetailView, FormView
from django.utils.translation import ugettext_lazy as _

from .models import User
from .forms import UserTradeForm, UserForm
from investmgr.models import TradeRec, Positions, TradeStrategy


# Create your views here.
class UserDashboardView(LoginRequiredMixin, ListView):
    # form_class = UserTradeForm
    # model = TradeRec

    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'users/user_dashboard.html'
    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'trade_info'  

    def get_queryset(self):
        tradedetails = TradeRec.objects.filter(trader=self.request.user.id, )[:10]
        trade_positions = Positions.objects.filter(trader=self.request.user.id).exclude(lots=0)
        # fav_stocks = StockFavorates.objects.filter(trader=self.request.user.id,)
        queryset = {
            'tradedetails': tradedetails,
            'positions': trade_positions,
            # 'fav_stocks': fav_stocks
        }
        return queryset


class TradeRecCreateView(LoginRequiredMixin, FormView):
    # model = TradeRec
    """Basic CreateView implementation to create new articles."""
    model = TradeRec
    message = _('新的交易记录创建成功.')

    def form_valid(self, form):
        user = self.request.user
        # form.instance.user = user
        traderec = form.save(False)
        traderec.trader = user
        traderec.save(True)
        return super().form_valid(form)

# class UserDetailView(LoginRequiredMixin, DetailView):
#     model = User

