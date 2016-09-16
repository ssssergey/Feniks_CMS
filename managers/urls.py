# -*- coding: utf-8 -*-

from django.conf.urls import url

from managers.views import *

urlpatterns = [
    url(r'^order_create$', OrderCreate.as_view(), name='order_create'),
    url(r'^order_edit/(?P<pk>[0-9]+)$', OrderEdit.as_view(), name='order_edit'),
    url(r'^order_delete/(?P<order_id>[0-9]+)$', order_delete, name='order_delete'),
    url(r'^order_list$', order_list, name='order_list'),
    url(r'^order_detail/(?P<pk>[0-9]+)$', OrderDetail.as_view(), name='order_detail'),
    url(r'^order_fill/(?P<order_id>[0-9]+)$', order_fill, name='order_fill'),
    url(r'^product_create$', ProductCreate.as_view(), name='product_create'),
    url(r'^product_to_order$', product_to_order, name='product_to_order'),
    url(r'^advance_money_create$', AdvanceMoneyCreate.as_view(), name='advance_money_create'),
    url(r'^advance_money_detail/(?P<pk>[0-9]+)$', AdvanceMoneyDetail.as_view(), name='advance_money_detail'),
    url(r'^advance_money_edit/(?P<pk>[0-9]+)$', AdvanceMoneyEdit.as_view(), name='advance_money_edit'),
    url(r'^delivery_create$', DeliveryCreate.as_view(), name='delivery_create'),
    url(r'^delivery_detail/(?P<pk>[0-9]+)$', DeliveryDetail.as_view(), name='delivery_detail'),
    url(r'^delivery_edit/(?P<pk>[0-9]+)$', DeliveryEdit.as_view(), name='delivery_edit'),
    url(r'^delivery_fill/(?P<id>[0-9]+)$', delivery_fill, name='delivery_fill'),
    url(r'^get_orderitems$', get_orderitems, name='get_orderitems'),
    url(r'^orderitem_to_delivery$', orderitem_to_delivery, name='orderitem_to_delivery'),
    url(r'^orderitem_delete$', orderitem_delete, name='orderitem_delete'),
    url(r'^orderitem_edit/(?P<pk>[0-9]+)$', OrderItemEdit.as_view(), name='orderitem_edit'),
    url(r'^find_delivery$', find_delivery, name='find_delivery'),
    url(r'^find_order$', find_order, name='find_order'),
    url(r'^admin_check/(?P<order_id>[0-9]+)$', admin_check, name='admin_check'),
]

