from django.urls import path

from . import views

app_name = 'stock_market'
urlpatterns = [
    path('industries/<industry>/',
         views.IndustryList.as_view(), name='industry_list'),  # ??
    path('province/<province>/cities/<int:top>/',
         views.CityList.as_view(), name='city_list'),  # ??
    path('country/<country>/provinces/',
         views.ProvinceList.as_view(), name='province_list'),  # ??
    path('industry-basic/<industry>/<basic_type>/<quantile>/<start_date>/<end_date>/',
         views.IndustryBasicList.as_view(), name='industry_list'),  # ??
    path('companies/<input_text>/',
         views.CompanyList.as_view(), name='company_list'),  # views.get_companies),
    #     path('industries/<industry>/companies/',
    #          views.IndustryCompanyList.as_view(), name='company_list_industry'),
    path('stock-close-history/<ts_code>/<freq>/<int:period>/',
         views.StockCloseHistoryList.as_view(), name='close_history'),  # ??
#     path('ohlc/<ts_code>/<freq>/<int:period>/',
#          views.OHLCList.as_view(), name='ohlc'),  # ??
    path('ohlc-indic/<ts_code>/<freq>/<int:period>/<adj>/',
         views.get_ohlc, name='ohlc_indic'),  # ??
    path('ma/<ts_code>/<freq>/<int:period>/',
         views.get_ma),  # ??
    path('sma/<ts_code>/<freq>/<int:period>/',
         views.get_sma),  # ??
    path('rsi/<ts_code>/<freq>/<int:period>/',
         views.get_rsi),  # ??
    path('kdj/<ts_code>/<freq>/<int:period>/',
         views.get_kdj),  # ??
    path('bbi/<ts_code>/<freq>/<int:period>/',
         views.get_bbi),  # ??
    path('macd/<ts_code>/<freq>/<int:period>/',
         views.get_macd),  # ??
    path('boll/<ts_code>/<freq>/<int:period>/',
         views.get_boll),  # ??
    path('ema/<ts_code>/<freq>/<int:period>/',
         views.get_ema),  # ??
    path('stock-indic/<ts_code>/<freq>/<int:period>/',
         views.StockRSVPlusList.as_view(), name='stock_indicator'),  # ??
    path('daily-basic-history/<ts_code>/<start_date>/<end_date>/',
         views.StockDailyBasicHistoryList.as_view(), name='daily_basic_history'),
    path('top10-holders-stat/<ts_code>/<int:period>/',
         views.StockTop10HoldersStatList.as_view(), name='top10_holders_stat'),
    path('company-basic/<ts_code>/',
         views.get_company_basic),
    path('latest-daily-basic/<ts_code>/',
         views.get_latest_daily_basic),
    path('industry-latest-daily-basic/<industry>/<type>/',
         views.get_industry_basic),
    path('bt/', views.BTView.as_view(), name='huice'),
    path('bt-crossover/<ts_code>/<tech_indicator>/<indicator_param>/<strategy_category>/<cash>/<commission>/<leverage>/<freq>/',
         views.CrossoverBacktestingList.as_view(), name='backtesting_list'),
#     path('bt-system/<ts_code>/<strategy_category>/<ta_indicator_dict>/<buy_cond_dict>/<sell_cond_dict>/<stoploss>/<cash>/<commission>/<leverage>/<trade_on_close>/<freq>/',
#          views.SystemBacktestingList.as_view(), name='backtesting_list'),
    path('bt-system/<ts_code>/<strategy_category>/<ta_indicator_dict>/<buy_cond_dict>/<sell_cond_dict>/<stoploss>/<cash>/<commission>/<leverage>/<trade_on_close>/<adj>/<freq>/',
         views.get_bt_result),
    path('command/',
         views.command_test),
    path('cmd/<cmd>/<params>/', views.analysis_command),
]
