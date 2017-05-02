# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.contrib import admin

from managers.views import index

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('accounts.urls')),
    url(r'^', include('managers.urls')),
    url(r'^', include('statistics.urls')),
    url(r'^$', index, name='home'),
    url(r'^api/', include('managers.api.urls', namespace="api")),
    url(r'^api/', include('statistics.api_accountant.urls', namespace="api")),
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

admin.site.site_header = u'"Феникс" - зарплаты'
