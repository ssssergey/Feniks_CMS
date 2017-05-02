from django.conf.urls import url
from django.contrib.auth.views import logout, login

from .views import WorkerMonthArchiveView, WorkerDayArchiveView

urlpatterns = [
    url(r'^worker/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/(?P<user_id>[0-9]+)$',
        WorkerMonthArchiveView.as_view(),
        name='worker_account'),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]+)/(?P<day>[0-9]+)/(?P<user_id>[0-9]+)$',
        WorkerDayArchiveView.as_view(month_format='%m'),
        name="worker_day"),

    url(r'^login/$', login, {'template_name': 'accounts/login.html'},
        name='login'),
    url(r'^logout/$', logout, {'template_name': 'accounts/logged_out.html'},
        name='logout'),
]
