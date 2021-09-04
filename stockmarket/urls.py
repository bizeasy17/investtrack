from stockmarket import views
from django.urls import path, re_path

app_name = 'stock_market'
urlpatterns = [
    path('companies/<input_text>/',
         views.get_companies),
    path('company-basic/<ts_code>/',
         views.get_company_basic),
    path('daily-basic/companies/<ts_code>/<start_date>/<end_date>/',
         views.get_daily_basic),
    path('daily-basic/company/<ts_code>/<start_date>/<end_date>/',
         views.get_single_daily_basic),
    path('close/<ts_code>/<freq>/<int:period>/',
         views.stock_close_hist),  # ??
]
