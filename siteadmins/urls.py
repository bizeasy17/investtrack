from django.urls import re_path, path

from . import views

app_name = 'siteadmin'
urlpatterns = [
    path('dashboard/',
         views.DashboardView.as_view(), name='dashboard'),  # ??
    path('settings/',
         views.SettingsView.as_view(), name='setting'),  # ??
    path('strategy-mgmt/',
         views.StrategyMgmtView.as_view(), name='strategy_mgmt'),  # ??
    path('companylisted/sync/', views.sync_company_list),
]
