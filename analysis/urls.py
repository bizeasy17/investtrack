from django.urls import re_path, path

from . import views

app_name = 'analysis'
urlpatterns = [
    path('cmd/<cmd>/<params>/', views.analysis_command),
]
