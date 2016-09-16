from django.conf.urls import url
from views import ProductListAPIView

urlpatterns = [
    url(r'^products/$', ProductListAPIView.as_view(), name='products'),
]