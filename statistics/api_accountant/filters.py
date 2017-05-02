from django_filters import rest_framework as filters
from django.db.models import Q

from managers.models import Order, Delivery
from accounts.models import UserProfile


class OrdersFilter(filters.FilterSet):
    saler = filters.NumberFilter(name='saler', method='saler_custom_filter')
    date_from = filters.DateFilter(name='sale_date', lookup_type='gte')
    date_to = filters.DateFilter(name='sale_date', lookup_type='lte')

    class Meta:
        model = Order
        fields = ['date_from', 'date_to', 'saler']

    def saler_custom_filter(self, queryset, name, value):
        queryset = queryset.filter(Q(saler__id=value) | Q(saler2__id=value)).distinct()
        return queryset


class DeliveryLifterFilter(filters.FilterSet):
    date_from = filters.DateFilter(name='date', lookup_type='gte')
    date_to = filters.DateFilter(name='date', lookup_type='lte')

    class Meta:
        model = Delivery
        fields = ['date_from', 'date_to', 'lifter']


class DeliveryAssemblerFilter(filters.FilterSet):
    date_from = filters.DateFilter(name='date', lookup_type='gte')
    date_to = filters.DateFilter(name='date', lookup_type='lte')

    class Meta:
        model = Delivery
        fields = ['date_from', 'date_to']


class DeliveryDriverFilter(filters.FilterSet):
    date_from = filters.DateFilter(name='date', lookup_type='gte')
    date_to = filters.DateFilter(name='date', lookup_type='lte')

    class Meta:
        model = Delivery
        fields = ['date_from', 'date_to', 'driver']


class UsersFilter(filters.FilterSet):

    class Meta:
        model = UserProfile

