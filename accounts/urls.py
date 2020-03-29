from django.urls import path, re_path
from django.views.generic import TemplateView

from . import views

app_name = 'account'
urlpatterns = [
    path('login/',
         TemplateView.as_view(template_name='account/login.html'), name='login'),
    path('signup/',
         TemplateView.as_view(template_name='account/signup.html'), name='signup'),
    path('reset-password/',
         TemplateView.as_view(template_name='account/password_reset.html'), name='reset_password'),
    path('authenticate/',
         views.authenticate_view),
    path('logout/',
         views.logout_view, name="logout"),
    path('register/',
         views.register_view),
    path('password/reset',
         views.reset_password_view),
]
