# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.contrib import admin

from managers.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('accounts.urls')),
    url(r'^', include('managers.urls')),
    url(r'^', include('statistics.urls')),
    url(r'^$', index, name='home'),
]

admin.site.site_header = u'"Феникс" - зарплаты'
