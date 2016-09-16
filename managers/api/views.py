from rest_framework.serializers import ModelSerializer
from rest_framework.generics import ListAPIView

from managers.models import Product

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug'
        ]

class ProductListAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer