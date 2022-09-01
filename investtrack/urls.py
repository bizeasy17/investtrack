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
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView

from stockmarket.models import StockNameCodeMap
from rest_framework import routers, serializers, viewsets

urlpatterns = [

    # admin url
    path('admin/', admin.site.urls),
    # App urls
    path('user/', include('users.urls')),
    # path('invest/', include('investmgr.urls')),
    path('account/', include('accounts.urls')),
    # retro1
    # path('auth/', include('authentication.urls')),
    path('investors/', include('investors.urls')),
    # path('notifications/', include('notifications.urls')),
    # path('stocktrade/', include('stocktrade.urls')),
    path('siteadmin/', include('siteadmins.urls')),
    path('stockmarket/', include('stockmarket.urls')),
    # path('tradeaccounts/', include('tradeaccounts.urls')),
    # path('txnvis/', include('txnvisibility.urls')),
    # path('dashboard/', include('dashboard.urls')),
    path('analysis/', include('analysis.urls')),
    # path('hongguan/', include('hongguan.urls')),
    path('zixuan/', include('zixuan.urls')),
    # path('xuangu/', include('xuangu.urls')),
    # path('paiming/', include('paiming.urls')),
    re_path(r'^', include('search.urls')),

    # home pages
    # re_path(r'^$',
    #         TemplateView.as_view(template_name='public_pages/home.html'), name='home'),
    # simple pages
    re_path(r'^about/$',
            TemplateView.as_view(template_name='pages/about.html'), name='about'),
    # test pages
    re_path(r'^404/$',
            TemplateView.as_view(template_name='pages/404.html'), name='404'),
    # 3rd Party Apps
    path('api-auth/', include('rest_framework.urls'))
]
handler404 = 'users.views.page_not_found_view'
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
