from . import views
from django.urls import path, re_path

app_name = 'investors'
urlpatterns = [
    path('follow-stock/<symbol>/',
         views.follow_stock),
    path('unfollow-stock/<symbol>/',
         views.unfollow_stock),
    path('stocks-following/',
         views.stocks_following),
    path('kanpan/',
         views.KanpanView.as_view(), name='kanpan'),  # ??
]
