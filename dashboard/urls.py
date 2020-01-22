from . import views
from django.urls import path, re_path

app_name = 'dashboard'
urlpatterns = [
    # re_path(r'^$', views.NotificationUnreadListView.as_view(), name='unread'),
]