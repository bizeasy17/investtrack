from django.urls import path, re_path

from . import views

app_name = 'user'
urlpatterns = [
    #     path('profile/<username>',
    #          views.UserProfileView.as_view(), name='profile'),
    path('profile/',
         views.UserProfileView.as_view(), name='get_profile'),
    path('profile/update',
         views.update_user_profile, name='update_profile'),
    #     path('trade/<account>/<type>/<ts_code>/',
    #          views.UserStockTradeView.as_view(), name='stock_trade'),
    path('account/<account>/trade/<symbol>/',
         views.UserRecordStockTradeView.as_view(), name='get_record_trade_view'),
    path('dashboard/',
         views.UserDashboardView.as_view(), name='dashboard'),
    path('tradelog/<symbol>',
         views.UserTradelogView.as_view(), name='trade_log'),
    path('create-trade',
         views.create_trade, name='post_trade_creation'),
    path('account/create',
         views.UserTradeAccountCreateView.as_view(), name='create_account'),
    path('create-account',
         views.create_account, name='account_create'),
    path('get-stock-for-trade/<account>/<stock_code>/',
         views.get_stock_for_trade),
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
]
