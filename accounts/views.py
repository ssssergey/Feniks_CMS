# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.views.generic.dates import MonthArchiveView, DayArchiveView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from managers.models import Order, OrderItem, Delivery

User = get_user_model()


class WorkerDayArchiveView(LoginRequiredMixin, DayArchiveView):
    """ Daily report for boss  """
    queryset = Order.objects.all()
    date_field = "sale_date"
    template_name = 'accounts/workers_archive_day.html'
    allow_empty = True
    ordering = 'sale_date'

    def get_queryset(self):
        qs = super(WorkerDayArchiveView, self).get_queryset()
        qs = qs.filter(Q(saler__id=self.kwargs['user_id']) | Q(saler2__id=self.kwargs['user_id'])).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super(WorkerDayArchiveView, self).get_context_data(**kwargs)

        qs = context['object_list']

        total_per_saler = 0
        for order in qs:
            total_per_saler += order.total_per_saler
        context['total'] = total_per_saler
        return context


class WorkerMonthArchiveView(LoginRequiredMixin, MonthArchiveView):
    queryset = Order.objects.all()
    date_field = "sale_date"
    template_name = 'accounts/workers_archive_month.html'
    allow_empty = True
    month_format = '%m'
    ordering = 'sale_date'

    def get_queryset(self):
        qs = super(WorkerMonthArchiveView, self).get_queryset()
        qs = qs.filter(Q(saler__id=self.kwargs['user_id']) | Q(saler2__id=self.kwargs['user_id'])).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super(WorkerMonthArchiveView, self).get_context_data(**kwargs)
        user = get_object_or_404(User, id=self.kwargs['user_id'])
        context['current_user'] = user

        qs = context['object_list']

        total_per_saler = 0
        for order in qs:
            total_per_saler += order.total_per_saler
        context['total'] = total_per_saler

        realiz_qs = qs.filter(full_money_date__isnull=False)

        realiz_total = 0
        for order in realiz_qs:
            realiz_total += order.total_per_saler
        context['realiz_total'] = realiz_total
        context['realiz_qs'] = realiz_qs

        all_qs = self.get_queryset()
        realiz_cashin_qs = all_qs.filter(full_money_date__month=self.get_month()).filter(
            full_money_date__year=self.get_year())

        realiz_cashin_total = 0
        for order in realiz_cashin_qs:
            realiz_cashin_total += order.total
        context['realiz_cashin_total'] = realiz_cashin_total
        context['realiz_cashin_qs'] = realiz_cashin_qs

        # Lifter
        lifts = Delivery.objects.filter(lifter__id=self.kwargs['user_id'],
                                        date__month=self.get_month()).filter(
            date__year=self.get_year()).prefetch_related('orderitem_set__order')
        total_per_lifter = 0
        for lift in lifts:
            total_per_lifter += lift.price_per_lifter
        context['lifts'] = lifts
        context['total_per_lifter'] = total_per_lifter

        # Driver
        drives = Delivery.objects.filter(driver__id=self.kwargs['user_id'], date__month=self.get_month()).filter(
            date__year=self.get_year())
        context['drives'] = drives

        # Admin
        admins = OrderItem.objects.filter(supplier_invoice_date__month=self.get_month(),
                                          admin_id=self.kwargs['user_id']).filter(
            supplier_invoice_date__year=self.get_year()).select_related('order', 'product')
        context['admins'] = admins

        return context
