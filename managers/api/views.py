from rest_framework.serializers import ModelSerializer
from rest_framework.generics import ListAPIView, CreateAPIView

from managers.models import Product


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug'
        ]


class ProductCreateSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = [
            # 'id',
            'name',
            # 'slug'
        ]


class ProductListAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductCreateAPIView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
