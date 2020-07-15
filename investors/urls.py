from . import views
from django.urls import path, re_path

app_name = 'investors'
urlpatterns = [
    path('follow-stock/<symbol>/',
         views.follow_stock),
    path('stocks-following/',
         views.stocks_following),
]
