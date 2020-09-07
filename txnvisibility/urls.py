from . import views
from django.urls import path, re_path

app_name = 'txn_vis'
urlpatterns = [
    # # date format: 2020-01-30, period format: 15, 30, 60, D, W, M, index_name format: sh, sz, hs300 etc.
    # # http://127.0.0.1:8000/invest/stocks/get-index-price/sh/2019-12-01/2019-12-31/D
    # /txnvis/hist/6/000001/2020-02-25/2020-04-25/D/
    path('hist/<int:account_id>/<symbol>/<start_date>/<end_date>/<type>/',
         views.stock_transaction_history),
    path('stock-for-trade/<int:account_id>/<symbol>/',
         views.stock_for_trade),
]
