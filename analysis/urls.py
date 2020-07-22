from django.urls import re_path, path

from . import views

app_name = 'analysis'
urlpatterns = [
    path('',
         views.AnalysisHomeView.as_view(), name='home'),  # ??
    path('strategies/by-category/<parent_strategy>/',
         views.strategies_by_category),  # ??
    #     path('b-test-result-inc  r-pct/strategy/<strategy>/<stock_symbol>/<test_period>/',
    #          views.bstrategy_test_result_incr_pct),  # ??
    path('expected-pct-data/strategy/<strategy>/<stock_symbol>/<freq>/<exp_pct>/',
         views.freq_expected_pct_data),  # ??
    path('high-pct-data/strategy/<strategy>/<stock_symbol>/<test_period>/',
         views.high_pct_data),  # ??
    path('low-pct-data/strategy/<strategy>/<stock_symbol>/<test_period>/',
         views.low_pct_data),  # ??
    path('mark-ma-cp/<stock_symbol>/<freq>/',
         views.ma_test),
    path('stock-hist/strategy/<strategy>/<stock_symbol>/<freq>/<type>/<int:period>/',
         views.stock_history),  # ??
    # 选股page
    path('xuangu/', views.XuanGuHomeView.as_view(), name="xuangu"),
    #     走势预测
    path('yuce/', views.YuCeHomeView.as_view(), name="yuce"),
    #     走势预测
    path('zhengu/', views.ZhenGuHomeView.as_view(), name="zhengu"),

    #     path('feed/pct-period-data/',
    #          views.feed_pct_data),  # ??
    #     path('feed/expected-pct-data/',
    #          views.feed_expected_pct_data),  # ??
    #     path('s-test-result/strategy/<strategy>/<stock_symbol>/<test_period>/',
    #          views.sstrategy_test_result_incr),  # ??
    #     path('s-test-result/strategy/<strategy>/<stock_symbol>/<test_period>/',
    #          views.sstrategy_test_result_drop),  # ??
]
