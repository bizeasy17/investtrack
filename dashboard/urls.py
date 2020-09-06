from django.urls import path, re_path

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('',
         views.DashboardHomeView.as_view(), name='index'),
    path('positions/refresh/',
         views.refresh_my_position),
    path('position/account/<account_id>/<symbol>',
         views.get_position_by_symbol),
    path('position-vs-status/<account>/<symbol>/',
         views.get_position_status),
    path('profit-trend/period/<period>/',
         views.get_profit_trend_by_period),
    path('invest-attempt-trend/period/<period>/',
         views.get_trans_success_rate_by_period),
    path('stock-profit-chg/<int:pid>/<symbol>/',
         views.get_stock_chg_seq),
]
