# -*- coding: utf-8 -*-

from datetime import datetime

from rest_framework import serializers, generics, permissions, viewsets
from django.db.models import Q
from django.db.models import Sum, Count

from managers.models import Product, OrderItem, Order
from accounts.models import UserProfile
from .filters import OrdersFilter, UsersFilter


class UserOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ This viewset automatically provides `list` and `detail` actions.
        http://127.0.0.1:8000/api/users/?role_saler=true
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserOrdersSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_class = UsersFilter

    def list(self, request, *args, **kwargs):
        response = super(UserViewSet, self).list(request, args, kwargs)
        for user in response.data:
            user['fullname'] = u'{} {} {}'.format(user['last_name'], user['first_name'],
                                                  user['patronymic'])
        return response


class SalerViewSet(UserViewSet):
    """ This viewset automatically provides `list` and `detail` actions.
        http://127.0.0.1:8000/api/salers/
        http://127.0.0.1:8000/api/salers/?date_to=2016-12-01
    """
    queryset = UserProfile.objects.filter(role_saler=True)

    def list(self, request, *args, **kwargs):
        response = super(SalerViewSet, self).list(request, args, kwargs)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        for user in response.data:
            user['fullname'] = u'{} {} {}'.format(user['last_name'], user['first_name'],
                                                  user['patronymic'])
        if date_from or date_to:
            for user in response.data:
                qs = Order.objects.all()
                # date filter
                if date_from is not None:
                    qs = qs.filter(sale_date__gte=date_from)
                if date_to is not None:
                    qs = qs.filter(sale_date__lte=date_to)
                # count orders
                qs = qs.filter(Q(saler__id=user['id']) | Q(saler2__id=user['id'])).distinct()
                user['count_orders'] = qs.count()
                # sum money
                sum_money = sum([order.total for order in qs])
                user['sum_money'] = sum_money
                orders = OrderSerializer(qs, many=True)
                user['orders'] = orders.data
        return response


class OrderSerializer(serializers.ModelSerializer):
    saler = serializers.ReadOnlyField(source='saler.fullname')
    saler2 = serializers.ReadOnlyField(source='saler2.fullname')

    class Meta:
        model = Order
        fields = [
            'id',
            'order_num',
            'saler',
            'saler2',
            'sale_date',
            'delivery_money',
            'delivery_discount',
            'lifting_money',
            'lifting_discount',
            'assembly_money',
            'assembly_discount',
            'kredit',
            'full_money_date',
            'admin_check',
            'admin_who_checked',
            'total',
            'total_subtotal',
            'total_per_saler',
            'total_advance_money',
            'quantity',
            'delivered',
        ]


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ This viewset automatically provides `list` and `detail` actions.
        http://127.0.0.1:8000/api/orders/?saler=12
        http://127.0.0.1:8000/api/orders/?date_to=2016-09-22
        http://127.0.0.1:8000/api/orders/?date_to=2016-09-22&saler=9
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_class = OrdersFilter

    def list(self, request, *args, **kwargs):
        response = super(OrderViewSet, self).list(request, args, kwargs)
        total_sum = 0
        total_sum_per_saler = 0
        for order in response.data:
            total_sum += order['total']
            total_sum_per_saler += order['total_per_saler']
        response.data = {
            'total_sum': total_sum,
            'total_sum_per_saler': total_sum_per_saler,
            'orders': response.data
        }
        return response

        # def get_queryset(self):
        #     queryset = Order.objects.all()
        #     saler_id = self.request.query_params.get('saler', None)
        #     if saler_id is not None:
        #         queryset = queryset.filter(Q(saler__id=saler_id) | Q(saler2__id=saler_id)).distinct()
        #     return queryset

        # class OrderList(generics.ListCreateAPIView):
        #     """ This viewset automatically provides `list` and `detail` actions. """
        #     queryset = Order.objects.all()
        #     serializer_class = OrderSerializer
        #     permission_classes = (permissions.IsAuthenticated,)
        #
        # class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
        #     """ This viewset automatically provides `list` and `detail` actions. """
        #     queryset = Order.objects.all()
        #     serializer_class = OrderSerializer
        #     permission_classes = (permissions.IsAuthenticated,)
        #
        # class UserList(generics.ListCreateAPIView):
        #     """ This viewset automatically provides `list` and `detail` actions. """
        #     queryset = UserProfile.objects.all()
        #     serializer_class = UserSerializer
        #     permission_classes = (permissions.IsAuthenticated,)
        #
        # class UserDetail(generics.RetrieveUpdateDestroyAPIView):
        #     """ This viewset automatically provides `list` and `detail` actions. """
        #     queryset = UserProfile.objects.all()
        #     serializer_class = UserSerializer
        #     permission_classes = (permissions.IsAuthenticated,)
