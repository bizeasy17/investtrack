from django.urls import re_path, path

from . import views

app_name = 'siteadmin'
urlpatterns = [
    path('<module_name>/',
         views.SiteAdminGenericView.as_view(), name='generic'),#??
    path('snapshot/manual/',
         views.take_snapshot_manual),
    path('trans/detail/position/<int:id>',
         views.get_transaction_detail),
    path('trans/detail/breakdown/<int:id>/<ref_num>',
         views.get_transaction_detail_breakdown),
    path('trans/detail/pkd/<int:ref_id>',
         views.get_transaction_detail_pkd),
    path('companylisted/sync/', views.sync_company_list),
    path('analysis/jiuzhuan/mark-test/<stock_symbol>/<start_date>/', views.jiuzhuan_test),

]
