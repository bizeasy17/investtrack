from django.urls import path, re_path

from users import views

app_name = 'user'
urlpatterns = [
    path('profile/',
         views.UserProfileView.as_view(), name='get_profile'),
    path('profile/update',
         views.update_user_profile, name='update_profile'),

]
