from django.urls import re_path, path

from . import views

app_name = 'paiming'
urlpatterns = [
    path('',
         views.HomeView.as_view(), name='home'),  # ??
]
