"""investtrack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # App urls
    path('siteadmin/', include('siteadmins.urls')),
    path('user/', include('users.urls')),
    path('notifications/', include('notifications.urls')),
    path('invest/', include('investmgr.urls')),
    
    # home pages
    re_path(r'^$',
            TemplateView.as_view(template_name='pages/home.html'), name='home'),
    # simple pages
    re_path(r'^about/$',
        TemplateView.as_view(template_name='pages/about.html'), name='about'),
    
    # test pages
    re_path(r'^404/$',
            TemplateView.as_view(template_name='pages/404.html'), name='404'),

    # 3rd Party Apps
    re_path(r'^accounts/', include('allauth.urls')),
]

handler404 = 'users.views.my_custom_page_not_found_view'

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
