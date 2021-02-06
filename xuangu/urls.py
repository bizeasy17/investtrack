from django.urls import re_path, path

from . import views

app_name = 'xuangu'
urlpatterns = [
    path('',
         views.SearchView.as_view(), name='home'),  # ??
]
