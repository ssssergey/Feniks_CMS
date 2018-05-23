from django.conf.urls import url
from .views import ProductListAPIView, ProductCreateAPIView, OrderItemListAPIView, OrderItemUpdateAPIView

urlpatterns = [
    url(r'^products/$', ProductListAPIView.as_view(), name='products'),
    url(r'^orderitems/order/(?P<order_num>[0-9]+)/$', OrderItemListAPIView.as_view(), name='orderitems'),
    url(r'^orderitems/(?P<id>[0-9]+)/edit/$', OrderItemUpdateAPIView.as_view(), name='orderitem_update'),
    url(r'^products/create/$', ProductCreateAPIView.as_view(), name='product_create'),
]
