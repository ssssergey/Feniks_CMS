from rest_framework.serializers import ModelSerializer, ReadOnlyField, HyperlinkedModelSerializer
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from managers.models import Product, OrderItem, Order


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
        ]

class OrderSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'order_num',
            '__unicode__',
        ]


class OrderItemSerializer(ModelSerializer):
    order = OrderSerializer()
    product = ProductSerializer()
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order',
            'product',
            'quantity',
            'price',
            'discount',
            'present',
            'supplier_invoice_date',
            'admin',
            'supplier_delivered_date',
            'delivery',
            'total',
            'total_with_discount',
            'name',
            'ordered_from_supplier',
            'received_from_supplier',
            'delivered',
        ]

class ProductCreateSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            # 'slug'
        ]


class ProductListAPIView(ListAPIView):
    """
    http://127.0.0.1:8000/api/products/
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.values('id', 'name').all()


class OrderItemListAPIView(ListAPIView):
    """
    http://127.0.0.1:8000/api/orderitems/order/1/
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        order = Order.objects.filter(order_num=self.kwargs['order_num']).last()
        return OrderItem.objects.filter(order=order).select_related('product', 'order')


class ProductCreateAPIView(CreateAPIView):
    """
    http://127.0.0.1:8000/api/products/create/
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer


class OrderItemUpdateAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    lookup_field = 'id'
