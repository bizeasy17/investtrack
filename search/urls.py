from django.urls import re_path, path

from . import views

app_name = 'search'
urlpatterns = [
    path('',
         views.SearchView.as_view(), name='home'),  # ??
    path('industry/<industry>/',
         views.IndustryHomeView.as_view(), name='industry_profile'),  # ??
]
