from django.urls import re_path, path

from . import views

app_name = 'siteadmin'
urlpatterns = [
    path('dashboard/',
         views.DashboardView.as_view(), name='dashboard'),  # ??
    path('settings/',
         views.SettingsView.as_view(), name='setting'),  # ??
    path('query-analyzer/',
         views.QueryAnalyzerView.as_view(), name='query_analyzer'),  # ??
    path('strategy-mgmt/',
         views.StrategyMgmtView.as_view(), name='strategy_mgmt'),  # ??
    path('snapshot/manual/',
         views.take_snapshot_manual),
    path('trans/detail/position/<int:id>',
         views.get_transaction_detail),
    path('trans/detail/breakdown/<int:id>/<ref_num>',
         views.get_transaction_detail_breakdown),
    path('trans/detail/pkd/<int:ref_id>',
         views.get_transaction_detail_pkd),
    path('companylisted/sync/', views.sync_company_list),
    path('analysis/mark-jz-cp/<stock_symbol>/<start_date>/<freq>/',
         views.jiuzhuan_test),
    path('strategy-test-by-period/<strategy>/<stock_symbol>/<test_period>/',
         views.bstrategy_test_by_period),  # ??
    path('strategy-test-exp-pct/<strategy>/<stock_symbol>/<test_freq>/',
         views.bstrategy_exp_pct_test),  # ??
]
