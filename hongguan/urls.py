from django.urls import re_path, path

from . import views

app_name = 'hongguan'
urlpatterns = [
    path('',
         views.HomeView.as_view(), name='home'),  # ??
    path('money-supply/<start_m>/<end_m>/',
         views.get_money_supply),
    path('cpi/<start_m>/<end_m>/',
         views.get_cpi),
    path('ppi/<start_m>/<end_m>/',
         views.get_ppi),
    path('gdp/<start_q>/<end_q>/',
         views.get_gdp),
    path('shibor/<start_date>/<end_date>/',
         views.get_shibor),
    path('libor/<start_date>/<end_date>/',
         views.get_libor),
    path('hibor/<start_date>/<end_date>/',
         views.get_hibor),
    path('shibor-lpr/<start_date>/<end_date>/',
         views.get_lpr),
]
