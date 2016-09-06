from django.conf.urls import url
from django.contrib.auth.views import logout, login

from .views import my_account

urlpatterns = [
    url(r'^my_account/$', my_account,{'template_name': 'accounts/my_account.html'}, 'my_account'),
    url(r'^login/$', login, {'template_name': 'accounts/login.html' }, 'login'),
    url(r'^logout/$', logout, {'template_name': 'accounts/logged_out.html'}, 'login'),
]