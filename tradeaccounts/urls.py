from . import views
from django.urls import path, re_path

app_name = 'trade_account'
urlpatterns = [
    path('',
         views.TradeAccountsHomeView.as_view(), name='index'),
    path('create/',
         views.create_tradeaccount, name='create'),
     path('comments/<ts_code>/<position_id>/',
         views.position_comments, name='comments'),
    # path('/positions/',
    #      views.positions, name='all_positions'),
    # path('/<account_id>/position/',
    #      views.position, name='position_by_account'),
]
