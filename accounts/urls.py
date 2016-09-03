from django.conf.urls import url
from views import *
from django.contrib.auth.views import login

urlpatterns = [
    url(r'^my_account/$', my_account,{'template_name': 'accounts/my_account.html'}, 'my_account'),
    url(r'^order_details/(?P<order_id>[-\w]+)/$', order_details,{'template_name': 'accounts/order_details.html'}, 'order_details'),
    url(r'^login/$', login, {'template_name': 'accounts/login.html' }, 'login'),
]