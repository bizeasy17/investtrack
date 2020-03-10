from django.urls import re_path, path

from . import views

app_name = 'user'
urlpatterns = [
    path('profile/<user_name>',
         views.UserProfileView.as_view(), name='profile'),
    path('trade/<account>/<type>/<ts_code>/',
         views.UserStockTradeView.as_view(), name='stock_trade'),
    path('trade/account/<account>/',
         views.UserRecordTradeView.as_view(), name='record_trade'),
    path('dashboard/',
         views.UserDashboardView.as_view(), name='dashboard'),
    path('tradelog/',
         views.UserTradelogView.as_view(), name='trade_log'),
    path('create-trade',
         views.create_trade, name='create_trade'),
    path('account/create',
         views.UserTradeAccountCreateView.as_view(), name='create_account'),
    path('create-account',
         views.create_account, name='account_create'),
    path('get-stock-for-trade/<account>/<stock_code>/',
         views.get_stock_for_trade),
    path('position/refresh',
         views.refresh_position),
    path('position/account/<account_id>/<symbol>',
         views.get_position_by_symbol),
    path('position-vs-status/<account>/<symbol>/',
         views.get_position_status),
    path('profit-trend/period/<period>/',
         views.get_profit_trend_by_period),
    path('invest-attempt-trend/period/<period>/',
         views.get_invest_success_attempt_by_period),
]
