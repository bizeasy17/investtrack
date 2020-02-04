from django.urls import re_path, path

from . import views

app_name = 'siteadmin'
urlpatterns = [
    path('<module_name>/',
         views.SiteAdminGenericView.as_view(), name='generic'),
]
