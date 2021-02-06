from django.urls import re_path, path

from . import views

app_name = 'paiming'
urlpatterns = [
    path('',
         views.SearchView.as_view(), name='home'),  # ??
]
