from django.urls import re_path, path

from . import views

app_name = 'zixuan'
urlpatterns = [
    path('',
         views.HomeView.as_view(), name='home'),  # ??
]
