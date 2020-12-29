from django.urls import re_path, path

from . import views

app_name = 'analysis'
urlpatterns = [
    path('',
         views.AnalysisHomeView.as_view(), name='home'),  # ??
    path('<ts_code>/',
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
    path('stock-hist/strategy/<strategy>/<stock_symbol>/<freq>/<type>/<int:period>/',
         views.stock_history),  # ??
    # paiming page
    path('paiming/', views.PaimingHomeView.as_view(), name="paiming"),
    # 选股page
    path('xuangu/', views.XuanguHomeView.as_view(), name="xuangu"),
    path('xuangu/<int:year>/<int:mon>/<int:day>/<strategy_code>/<int:period>/<exp_pct>/<int:start_idx>/<int:end_idx>/',
         views.get_picked_stocks_bundle),
#     path('xuangu/picked_stocks/<year>/<month>/<day>/<strategy_code>/<int:start_idx>/<int:end_idx>/',
#          views.get_picked_stocks),
#     path('qt-uppct/<ts_codes>/<strategy_code>/',
#          views.get_qt_uppct),
#     path('qt-downpct/<ts_codes>/<strategy_code>/',
#          views.get_qt_downpct),
#     path('qt-targetpct-period/<ts_codes>/<strategy_code>/',
#          views.get_qt_targetpct),
    # ranking
    path('ranking/<strategy_code>/<test_type>/<qt_pct>/<input_param>/<int:start_idx>/<int:end_idx>/',
         views.strategy_test_ranking),
    # target pct rankings
    path('target-pct-ranking-by-stock/<stock_symbol>/<target_pct>/',
         views.stock_ranking_target_pct),
    path('updown-pct-ranking-by-stock/<stock_symbol>/<test_period>/<strategy_ctg>/<test_type>/',
         views.stock_ranking_updown_pct),

    #     走势预测
    path('yuce/', views.YuceHomeView.as_view(), name="yuce"),
    #     走势预测
    path('zhengu/', views.ZhenguHomeView.as_view(), name="zhengu"),

    path('cmd/<cmd>/<params>/', views.analysis_command),


    #     path('feed/pct-period-data/',
    #          views.feed_pct_data),  # ??
    #     path('feed/expected-pct-data/',
    #          views.feed_expected_pct_data),  # ??
    #     path('s-test-result/strategy/<strategy>/<stock_symbol>/<test_period>/',
    #          views.sstrategy_test_result_incr),  # ??
    #     path('s-test-result/strategy/<strategy>/<stock_symbol>/<test_period>/',
    #          views.sstrategy_test_result_drop),  # ??
]
