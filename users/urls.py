from django.urls import re_path, path

from . import views

app_name = 'users'
urlpatterns = [
    path('<pk>/dashboard/',
         views.UserDashboardView.as_view(), name='dashboard'),
    path('invest/create',
         views.create_trade, name='create_trade'),
]
