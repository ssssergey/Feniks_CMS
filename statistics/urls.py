# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^statistics$', statistics, name='statistics'),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]+)/$',
        OrderMonthArchiveView.as_view(month_format='%m'),
        name="archive_month_numeric"),
    url(r'^(?P<year>[0-9]{4})/week/(?P<week>[0-9]+)/$',
        OrderWeekArchiveView.as_view(),
        name="archive_week"),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]+)/(?P<day>[0-9]+)/$',
        OrderDayArchiveView.as_view(month_format='%m'),
        name="archive_day"),
]
