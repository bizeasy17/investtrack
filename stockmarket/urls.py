from stockmarket import views
from django.urls import path, re_path

app_name = 'stock_market'
urlpatterns = [
    path('companies/<input_text>/',
         views.get_companies),
    path('realtime-quotes/<symbols>/',
         views.realtime_quotes),
    path('company-basic/<ts_code>/',
         views.get_company_basic),
    path('daily-basic/companies/<ts_code>/<start_date>/<end_date>/',
         views.get_daily_basic),
    path('daily-basic/company/<ts_code>/<start_date>/<end_date>/',
         views.get_single_daily_basic),
    path('stock-hist/<ts_code>/<freq>/<type>/<int:period>/',
         views.stock_close_hist),  # ??
    path('updown-pct/<ts_code>/<strategy>/<test_period>/<freq>/<filters>/',
         views.get_updown_pct),
    path('daily-basic-latest/companies/<ts_code>/',
         views.get_latest_daily_basic),
    path('btest-ranking/<btest_type>/<btest_value>/<strategy>/<sorted_by>/<filters>/<freq>/<int:start_idx>/<int:end_idx>/',
         views.get_btest_ranking),
    #     path('updown-index-vol/<test_period>/<freq>/',
    #          views.get_index_vol_range),
    #     path('updown-stock-vol/<ts_code>/<strategy>/<exp_pct>/<freq>/',
    #          views.get_stock_vol_range),
    path('exp-pct/<ts_code>/<strategy>/<exp_pct>/<freq>/',
         views.get_expected_pct),
]
