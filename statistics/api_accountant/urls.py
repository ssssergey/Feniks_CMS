from django.conf.urls import url
# from views import OrderList, OrderDetail, UserDetail, UserList
from .views import (OrderViewSet, UserViewSet, SalerViewSet, DeliveryLifterViewSet, MoneyExtraViewSet,
                    DeliveryDriverViewSet, DeliveryAssemblerViewSet)
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

# urlpatterns = format_suffix_patterns([
#     url(r'^users/$',
#         UserList.as_view(),
#         name='users-list'),
#     url(r'^users/(?P<pk>[0-9]+)/$',
#         UserDetail.as_view(),
#         name='users-detail'),
#     url(r'^orders/$',
#         OrderList.as_view(),
#         name='order-list'),
#     url(r'^orders/(?P<pk>[0-9]+)/$',
#         OrderDetail.as_view(),
#         name='order-detail')
# ])

router = routers.SimpleRouter()
router.register(r'orders-for-salers', OrderViewSet)
router.register(r'delivery-lifter', DeliveryLifterViewSet)
router.register(r'delivery-assembler', DeliveryAssemblerViewSet)
router.register(r'delivery-driver', DeliveryDriverViewSet)
router.register(r'users', UserViewSet)
router.register(r'salers', SalerViewSet)
router.register(r'money-extra', MoneyExtraViewSet)

urlpatterns = router.urls
