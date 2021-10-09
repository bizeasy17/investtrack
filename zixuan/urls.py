from django.urls import re_path, path

from . import views

app_name = 'zixuan'
urlpatterns = [
    path('',
         views.HomeView.as_view(), name='home'),  # ??
    path('industries/<industry>/my-company-daily-basic/',
         views.MyCompanyDailyBasicList.as_view(), name='my_company_daily_basic'),  # ??
    path('selected-stk-price/',
         views.get_selected_latest_price),
    path('selected-stk-traffic/<ts_code>/',
         views.get_selected_traffic),
]
