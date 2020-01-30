from . import views
from django.urls import path, re_path

app_name = 'investment_manager'
urlpatterns = [
    path('stocks/get-realtime-price/<stock_name_or_code>/',
         views.get_realtime_price),
    # date format: 2020-01-30, period format: 15, 30, 60, D, W, M, index_name format: sh, sz, hs300 etc.
    # http://127.0.0.1:8000/invest/stocks/get-index-price/sh/2019-12-01/2019-12-31/D
    path('stocks/get-index-price/<index_name>/<start_date>/<end_date>/<period>/',
         views.get_index_price_by),
]
