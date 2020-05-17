from django.urls import re_path, path

from . import views

app_name = 'analysis'
urlpatterns = [
    path('',
         views.AnalysisHomeView.as_view(), name='home'),  # ??
    path('strategies/category/<strategy_ctg>/',
         views.strategies_by_category),  # ??
    path('b-test/strategy/<strategy>/<stock_symbol>/<test_freq>/<test_period>/',
         views.bstrategy_test),  # ??
    path('b-test-result-incr-pct/strategy/<strategy>/<stock_symbol>/<test_period>/',
         views.bstrategy_test_result_incr_pct),  # ??
    path('b-test-result-incr/strategy/<strategy>/<stock_symbol>/<test_period>/',
         views.bstrategy_test_result_incr),  # ??
    path('b-test-result-drop/strategy/<strategy>/<stock_symbol>/<test_period>/',
         views.bstrategy_test_result_drop),  # ??
    path('s-test-result/strategy/<strategy>/<stock_symbol>/<test_period>/',
         views.sstrategy_test_result_incr),  # ??
    path('s-test-result/strategy/<strategy>/<stock_symbol>/<test_period>/',
         views.sstrategy_test_result_drop),  # ??
]
