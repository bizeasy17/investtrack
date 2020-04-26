from . import views
from django.urls import path, re_path

app_name = 'stocktrade'
urlpatterns = [
    path('<symbol>/account/<account_id>/',
         views.TransactionHomeView.as_view(), name='home'),
#     path('<symbol>/',
#          views.TransactionHomeView.as_view(), name='home_symbol'),
    path('create/',
         views.make_transaction, name='create'),
]
