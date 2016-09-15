from django.conf.urls import url
from django.contrib.auth.views import logout, login

from .views import saler, SalerMonthArchiveView, LifterMonthArchiveView, DriverMonthArchiveView, AdminMonthArchiveView, \
    WorkerMonthArchiveView

urlpatterns = [
    # url(r'^saler/(?P<id>[0-9]+)/$', saler, name='saler_account'),
    url(r'^worker/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/(?P<user_id>[0-9]+)$',
        WorkerMonthArchiveView.as_view(),
        name='worker_account'),
    url(r'^salers/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/(?P<user_id>[0-9]+)$',
        SalerMonthArchiveView.as_view(),
        name='saler_account'),
    url(r'^lifters/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/(?P<user_id>[0-9]+)$',
        LifterMonthArchiveView.as_view(),
        name='lifter_account'),
    url(r'^drivers/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/(?P<user_id>[0-9]+)$',
        DriverMonthArchiveView.as_view(),
        name='driver_account'),
    url(r'^admins/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/(?P<user_id>[0-9]+)$',
        AdminMonthArchiveView.as_view(),
        name='admin_account'),
    url(r'^login/$', login, {'template_name': 'accounts/login.html'}, name='login'),
    url(r'^logout/$', logout, {'template_name': 'accounts/logged_out.html'}, name='logout'),
]
