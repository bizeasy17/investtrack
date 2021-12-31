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
         views.CompanyList.as_view(), name='company_list'),#views.get_companies),
#     path('industries/<industry>/companies/',
#          views.IndustryCompanyList.as_view(), name='company_list_industry'),
    path('stock-close-history/<ts_code>/<freq>/<int:period>/',
         views.StockCloseHistoryList.as_view(), name='close_history'),  # ??
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
    path('command/',
         views.command_test),
    path('cmd/<cmd>/<params>/', views.analysis_command),
]
