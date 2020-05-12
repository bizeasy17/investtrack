from django.urls import re_path, path

from . import views

app_name = 'analysis'
urlpatterns = [
    path('',
         views.AnalysisHomeView.as_view(), name='home'),#??
    path('strategy/test/result/<stock_symbol>/<strategy>/<test_period>/',
         views.strategy_on_days_test_result),  # ??
]
