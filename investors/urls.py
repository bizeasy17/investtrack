from . import views
from django.urls import path, re_path
from django.views.generic import TemplateView


app_name = 'investors'
urlpatterns = [
    path('follow-stock/<symbol>/',
         views.follow_stock),
    path('unfollow-stock/<symbol>/',
         views.unfollow_stock),
    path('stocks-following/',
         views.stocks_following),
    path('xuangu/',
         views.XuanguView.as_view(), name='xuangu'),  # ??
    path('xuangu/filters/<filters>/<int:start_idx>/<int:end_idx>/',
         views.CompanyHistoryDailyBasicList.as_view(), name='xuangu_filter'),  # ??
#     path('candlesticks/',
#          views.KanpanView.as_view(), name='kanpan'),  # ??
    # simple pages
#     re_path('candlesticks/',
#             TemplateView.as_view(template_name='investors/candlesticks.html'), name='candlesticks'),
#     re_path('linechart/',
#             views.LinechartView.as_view(), name='linechart'),
]
