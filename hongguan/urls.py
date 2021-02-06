from django.urls import re_path, path

from . import views

app_name = 'hongguan'
urlpatterns = [
    path('',
         views.SearchView.as_view(), name='home'),  # ??
]
