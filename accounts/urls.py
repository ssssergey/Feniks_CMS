from django.conf.urls import url
from django.contrib.auth.views import logout, login

from .views import my_account

urlpatterns = [
    # url(r'^$', accounts,{'template_name': 'accounts/accounts.html'}, 'accounts'),
    url(r'^(?P<account_id>[0-9]+)/$', my_account, name='my_account'),
    url(r'^login/$', login, {'template_name': 'accounts/login.html' }, name='login'),
    url(r'^logout/$', logout, {'template_name': 'accounts/logged_out.html'}, name='logout'),
]