from . import views
from django.urls import path, re_path

app_name = 'notifications'
urlpatterns = [
    # re_path(r'^$', views.NotificationUnreadListView.as_view(), name='unread'),
    # re_path(r'^mark-as-read/(?P<slug>[-\w]+)/$', views.mark_as_read, name='mark_as_read'),
    # re_path(r'^mark-all-as-read/$', views.mark_all_as_read, name='mark_all_read'),
    # re_path(r'^latest-notifications/$', views.get_latest_notifications, name='latest_notifications'),
]