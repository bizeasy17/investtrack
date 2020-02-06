from django.urls import re_path, path

from . import views

app_name = 'user'
urlpatterns = [
    path('dashboard/',
         views.UserDashboardView.as_view(), name='dashboard'),
    path('tradelog/',
         views.UserTradelogView.as_view(), name='trade_log'),
    path('create-trade/',
         views.create_trade, name='create_trade'),
]
