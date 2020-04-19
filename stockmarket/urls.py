from stockmarket import views
from django.urls import path, re_path

app_name = 'stock_market'
urlpatterns = [
    path('realtime-quotes/<symbols>/',
         views.realtime_quotes),
    path('listed_companies/<name_or_code>/',
         views.listed_companies),
]
