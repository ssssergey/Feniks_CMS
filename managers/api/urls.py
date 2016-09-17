from django.conf.urls import url
from views import ProductListAPIView, ProductCreateAPIView

urlpatterns = [
    url(r'^products/$', ProductListAPIView.as_view(), name='products'),
    url(r'^products/create/$', ProductCreateAPIView.as_view(), name='create'),
]