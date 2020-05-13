from django.urls import re_path, path

from . import views

app_name = 'analysis'
urlpatterns = [
    path('',
         views.AnalysisHomeView.as_view(), name='home'),  # ??
    path('strategies/category/<strategy_ctg>/',
         views.strategies_by_category),  # ??
    path('strategy/b-test-result-incr/<strategy>/<stock_symbol>/<test_period>/',
         views.bstrategy_test_result_incr),  # ??
    path('strategy/b-test-result-drop/<strategy>/<stock_symbol>/<test_period>/',
         views.bstrategy_test_result_drop),  # ??
    path('strategy/s-test-result/<strategy>/<stock_symbol>/<test_period>/',
         views.sstrategy_test_result_incr),  # ??
    path('strategy/s-test-result/<strategy>/<stock_symbol>/<test_period>/',
         views.sstrategy_test_result_drop),  # ??
]
