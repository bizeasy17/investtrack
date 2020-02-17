from django.urls import re_path, path

from . import views

app_name = 'user'
urlpatterns = [
    path('profile/<user_name>',
         views.UserProfileView.as_view(), name='profile'),
    path('stock-trade/',
         views.UserStockTradeView.as_view(), name='stock_trade'),
    path('dashboard/',
         views.UserDashboardView.as_view(), name='dashboard'),
    path('tradelog/',
         views.UserTradelogView.as_view(), name='trade_log'),
    path('create-trade',
         views.create_trade, name='create_trade'),
    path('position/refresh',
         views.refresh_position, name='refresh_position'),
    path('position/<code>',
         views.get_position_by_code, name='get_position_by_code'),
]
