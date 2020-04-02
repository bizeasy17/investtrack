from django.urls import re_path, path

from . import views

app_name = 'siteadmin'
urlpatterns = [
    path('<module_name>/',
         views.SiteAdminGenericView.as_view(), name='generic'),
    path('snapshot/manual/',
         views.take_snapshot_manual),
    path('trans/detail/position/<int:id>',
         views.get_transaction_detail),
    path('trans/detail/breakdown/<ref_num>',
         views.get_transaction_detail_breakdown),
]
