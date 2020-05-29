from django.urls import re_path, path

from . import views

app_name = 'analysis'
urlpatterns = [
    path('',
         views.AnalysisHomeView.as_view(), name='home'),  # ??
    path('strategies/category/<strategy_ctg>/',
         views.strategies_by_category),  # ??
#     path('b-test-result-incr-pct/strategy/<strategy>/<stock_symbol>/<test_period>/',
#          views.bstrategy_test_result_incr_pct),  # ??
    path('expected-pct-data/strategy/<strategy>/<stock_symbol>/<freq>/<exp_pct>/',
         views.freq_expected_pct_data),  # ??
    path('high-pct-data/strategy/<strategy>/<stock_symbol>/<test_period>/',
         views.high_pct_data),  # ??
    path('low-pct-data/strategy/<strategy>/<stock_symbol>/<test_period>/',
         views.low_pct_data),  # ??
#     path('s-test-result/strategy/<strategy>/<stock_symbol>/<test_period>/',
#          views.sstrategy_test_result_incr),  # ??
#     path('s-test-result/strategy/<strategy>/<stock_symbol>/<test_period>/',
#          views.sstrategy_test_result_drop),  # ??
]
