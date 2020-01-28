from django.urls import re_path, path

from . import views

app_name = 'users'
urlpatterns = [
    path('<pk>/dashboard/',
         views.UserDashboardView.as_view(), name='dashboard'),
    path('trade/create',
         views.TradeRecCreateView.as_view(), name='create_trade'),
]
