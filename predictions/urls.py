from django.urls import re_path, path

from . import views

app_name = 'predictions'
urlpatterns = [
    path('',
         views.PredictHomeView.as_view(), name='home'),  # ??
]
