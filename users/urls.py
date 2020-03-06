from django.urls import re_path, path

from . import views

app_name = 'user'
urlpatterns = [
    path('profile/<user_name>',
         views.UserProfileView.as_view(), name='profile'),
    path('trade/<account>/<type>/<ts_code>/',
         views.UserStockTradeView.as_view(), name='stock_trade'),
    path('dashboard/',
         views.UserDashboardView.as_view(), name='dashboard'),
    path('tradelog/',
         views.UserTradelogView.as_view(), name='trade_log'),
    path('create-trade',
         views.create_trade, name='create_trade'),
    path('get-stock-for-trade/<account>/<stock_code>/',
         views.get_stock_for_trade),
    path('position/refresh',
         views.refresh_position, name='refresh_position'),
    path('position/account/<account_id>/<symbol>',
         views.get_position_by_symbol, name='get_position_by_symbol'),
]
