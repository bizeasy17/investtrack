from django.urls import re_path, path

from . import views

app_name = 'users'
urlpatterns = [
    re_path(r'^(?P<username>[\w.@+-]+)/$',
        views.UserDetailView.as_view(), name='detail'),
]