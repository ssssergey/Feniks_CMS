from django_filters import rest_framework as filters
from django.db.models import Q

from managers.models import Order
from accounts.models import UserProfile


class OrdersFilter(filters.FilterSet):
    saler = filters.NumberFilter(name='saler', method='saler_custom_filter')
    date_from = filters.DateFilter(name='sale_date', lookup_type='gte')
    date_to = filters.DateFilter(name='sale_date', lookup_type='lte')

    class Meta:
        model = Order

    def saler_custom_filter(self, queryset, name, value):
        queryset = queryset.filter(Q(saler__id=value) | Q(saler2__id=value)).distinct()
        return queryset

class UsersFilter(filters.FilterSet):

    class Meta:
        model = UserProfile

