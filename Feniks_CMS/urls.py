# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.contrib import admin

from managers.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^$', index, name='home'),
    url(r'^create_order$', create_order, name='create_order'),
    url(r'^product_list$', product_list, name='product_list'),
    url(r'^product_add$', product_add, name='product_add'),
    url(r'^add_to_order$', add_to_order, name='add_to_order'),
    url(r'^orders$', orders, name='orders'),
    url(r'^order/(?P<order_id>[0-9]+)$', order_detail, name='order_detail'),
    # url(r'^order/(?P<order_id>[0-9]+)/advance_money$', advance_money, name='advance_money'),
    # url(r'^order/(?P<order_id>[0-9]+)/order_items$', order_items, name='order_items'),
    # url(r'^order/(?P<order_id>[0-9]+)/order_items/(?P<oi_id>[0-9]+)$', order_item_detail, name='order_item_detail'),
]

admin.site.site_header = u'"Феникс" - зарплаты'
