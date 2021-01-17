from stockmarket import views
from django.urls import path, re_path

app_name = 'stock_market'
urlpatterns = [
    path('realtime-quotes/<symbols>/',
         views.realtime_quotes),
    path('listed_companies/<name_or_code>/',
         views.listed_companies),
    path('company-basic/<ts_code>/',
         views.get_company_basic),
    path('company-daily-basic/<ts_code>/<start_date>/<end_date>/',
         views.get_daily_basic),
    path('company-single-daily-basic/<ts_code>/<start_date>/<end_date>/',
         views.get_single_daily_basic),
    path('stock-hist/<ts_code>/<freq>/<type>/<int:period>/',
         views.stock_close_hist),  # ??
]
