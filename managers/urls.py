# -*- coding: utf-8 -*-

from django.conf.urls import url

from managers.views import *

urlpatterns = [
    url(r'^order_create$', order_create, name='order_create'),
    url(r'^order_edit/(?P<order_id>[0-9]+)$', order_edit, name='order_edit'),
    url(r'^order_delete/(?P<order_id>[0-9]+)$', order_delete, name='order_delete'),
    url(r'^order_list$', order_list, name='order_list'),
    url(r'^order_detail/(?P<order_id>[0-9]+)$', order_detail, name='order_detail'),
    url(r'^order_fill/(?P<order_id>[0-9]+)$', order_fill, name='order_fill'),
    url(r'^product_create$', product_create, name='product_create'),
    url(r'^product_to_order$', product_to_order, name='product_to_order'),
    url(r'^advance_money_create$', advance_money_create, name='advance_money_create'),
    url(r'^advance_money_detail/(?P<id>[0-9]+)$', advance_money_detail, name='advance_money_detail'),
    url(r'^advance_money_edit/(?P<id>[0-9]+)$', advance_money_edit, name='advance_money_edit'),
    url(r'^delivery_create$', delivery_create, name='delivery_create'),
    url(r'^delivery_detail/(?P<id>[0-9]+)$', delivery_detail, name='delivery_detail'),
    url(r'^delivery_edit/(?P<id>[0-9]+)$', delivery_edit, name='delivery_edit'),
    url(r'^delivery_fill/(?P<id>[0-9]+)$', delivery_fill, name='delivery_fill'),
    url(r'^get_orderitems$', get_orderitems, name='get_orderitems'),
    url(r'^orderitem_to_delivery$', orderitem_to_delivery, name='orderitem_to_delivery'),
    url(r'^delete_oi_from_order$', delete_oi_from_order, name='delete_oi_from_order'),
    url(r'^find_delivery$', find_delivery, name='find_delivery'),
    url(r'^find_order$', find_order, name='find_order'),
]

