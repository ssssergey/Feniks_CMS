# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date

from rest_framework import serializers, generics, permissions, viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from django.db.models import Q
from django.db.models import Sum, Count

from managers.models import Product, OrderItem, Order, Delivery
from accounts.models import UserProfile
from .filters import OrdersFilter, UsersFilter, DeliveryLifterFilter, DeliveryDriverFilter, DeliveryAssemblerFilter


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
    authentication_classes = (SessionAuthentication, BasicAuthentication)
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
    authentication_classes = (SessionAuthentication, BasicAuthentication)

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
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    filter_class = OrdersFilter

    def list(self, request, *args, **kwargs):
        response = super(OrderViewSet, self).list(request, args, kwargs)
        total_sum = 0
        total_sum_per_saler = 0
        for order in response.data:
            total_sum += order['total']
            total_sum_per_saler += order['total_per_saler']
        response.data = {
            'total_sum_for_salers': total_sum,
            'total_sum_per_saler': total_sum_per_saler,
            'orders': response.data
        }
        return response


class MoneyExtraViewSet(viewsets.ReadOnlyModelViewSet):
    """ This viewset automatically provides `list` and `detail` actions.
        http://127.0.0.1:8000/api/money-extra/
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        ids = [order.id for order in Order.objects.all() if order.delivered == False and order.kredit == False and (
            order.total_advance_money > 0 or order.full_money_date)]
        queryset = Order.objects.filter(id__in=ids)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(MoneyExtraViewSet, self).list(request, args, kwargs)
        total_sum = 0
        total_sum_paid_not_delivered = 0
        total_sum_partialy_paid = 0
        paid = [x for x in Order.objects.all() if
                x.delivered == False and x.full_money_date and x.kredit == False]
        for order in paid:
            total_sum_paid_not_delivered += order.total
        partialy_paid = [x for x in Order.objects.all() if
                         x.delivered == False and not x.full_money_date and x.kredit == False]
        for order in partialy_paid:
            total_sum_partialy_paid += order.total_advance_money
        total_sum = total_sum_paid_not_delivered + total_sum_partialy_paid
        response.data = {
            'total_sum': total_sum,
            'total_sum_paid_not_delivered': total_sum_paid_not_delivered,
            'total_sum_partialy_paid': total_sum_partialy_paid,
            'orders': response.data
        }
        return response


class DeliverySerializer(serializers.ModelSerializer):
    price_per_lifter = serializers.ReadOnlyField()

    class Meta:
        model = Delivery
        fields = '__all__'


class DeliveryLifterViewSet(viewsets.ReadOnlyModelViewSet):
    """ This viewset automatically provides `list` and `detail` actions.
        http://127.0.0.1:8000/api/delivery-lifter/?lifter=12
        http://127.0.0.1:8000/api/delivery-lifter/?date_to=2016-09-22
        http://127.0.0.1:8000/api/delivery-lifter/?date_to=2016-09-22&lifter=9
    """
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    filter_class = DeliveryLifterFilter

    def list(self, request, *args, **kwargs):
        lifter = self.request.query_params.get('lifter', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        if not date_from:
            content = {'error': u'Ошибка! Начальная дата не выбрана!'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        if not date_to:
            content = {'error': u'Ошибка! Конечная дата не выбрана!'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        response = super(DeliveryLifterViewSet, self).list(request, args, kwargs)
        total_sum = 0
        total_sum_per_lifter = 0
        for delivery in response.data:
            total_sum += delivery['price'] or 0
            total_sum_per_lifter += delivery['price_per_lifter']
        response.data = {
            'total_sum': total_sum,
            'total_sum_per_lifter': total_sum_per_lifter,
            'deliveries': response.data,
            'count': len(response.data),
        }
        return response


class DeliveryAssemblerSerializer(serializers.ModelSerializer):
    discount = serializers.SerializerMethodField()
    class Meta:
        model = Delivery
        fields = '__all__'

    def get_discount(self, delivery):
        item = delivery.orderitem_set.last()
        return item.order.assembly_discount if item else False


class DeliveryAssemblerViewSet(viewsets.ReadOnlyModelViewSet):
    """ This viewset automatically provides `list` and `detail` actions.
        http://127.0.0.1:8000/api/delivery-assembler
        http://127.0.0.1:8000/api/delivery-assembler/?date_to=2016-09-22
        http://127.0.0.1:8000/api/delivery-assembler/?date_from=2016-09-22
    """
    queryset = Delivery.objects.all()
    serializer_class = DeliveryAssemblerSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    filter_class = DeliveryAssemblerFilter

    def get_queryset(self):
        queryset = Delivery.objects.filter(price_assembly__gt = 0)
        return queryset

    def list(self, request, *args, **kwargs):
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        if not date_from:
            content = {'error': u'Ошибка! Начальная дата не выбрана!'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        if not date_to:
            content = {'error': u'Ошибка! Конечная дата не выбрана!'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        response = super(DeliveryAssemblerViewSet, self).list(request, args, kwargs)
        total_sum = 0
        total_sum_with_discount = 0
        for delivery in response.data:
            total_sum += delivery['price_assembly'] or 0
            if delivery['discount'] == True:
                total_sum_with_discount += delivery['price_assembly'] or 0
        response.data = {
            'total_sum': total_sum,
            'total_sum_with_discount': total_sum_with_discount,
            'deliveries': response.data,
            'count': len(response.data),
        }
        return response


class DeliveryDriverViewSet(viewsets.ReadOnlyModelViewSet):
    """ This viewset automatically provides `list` and `detail` actions.
        http://127.0.0.1:8000/api/delivery-driver/?date_from=2016-09-22&date_to=2016-09-22&driver=22
    """
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    filter_class = DeliveryDriverFilter

    def list(self, request, *args, **kwargs):
        driver = self.request.query_params.get('driver', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        if not date_from:
            content = {'error': u'Ошибка! Начальная дата не выбрана!'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        if not date_to:
            content = {'error': u'Ошибка! Конечная дата не выбрана!'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        response = super(DeliveryDriverViewSet, self).list(request, args, kwargs)

        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
        date_range = int((date_to_obj - date_from_obj).days) + 1
        dates = []
        extra_deliveries = 0
        full_days = 0
        not_full_days = 0
        for d in range(date_range):
            current_date = date_from_obj + timedelta(d)
            qs = Delivery.objects.filter(date=current_date)
            if driver:
                qs = qs.filter(driver=driver)
            if len(qs):
                date_dict = {}
                date_dict['num'] = d
                date_dict['date'] = current_date.strftime('%d.%m.%Y')
                deliveries = [{'id': deliv.id, 'delivery_num': deliv.delivery_num} for deliv in qs]
                date_dict['deliveries'] = deliveries
                date_dict['deliveries_count'] = len(deliveries)
                if len(deliveries) >= 4:
                    date_dict['full'] = True
                    full_days += 1
                else:
                    date_dict['full'] = False
                    not_full_days += 1
                date_dict['extra_count'] = (len(deliveries) - 4) if len(deliveries) >= 4 else 0
                extra_deliveries += date_dict['extra_count']
                dates.append(date_dict)

        response.data = {
            'dates': dates,
            'extra_deliveries': extra_deliveries,
            'full_days': full_days,
            'not_full_days': not_full_days,
        }
        return response

