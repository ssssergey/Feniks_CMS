from django.shortcuts import render
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic.dates import MonthArchiveView, WeekArchiveView, DayArchiveView
from django.contrib.auth import get_user_model

from managers.models import Order, AdvanceMoney


User = get_user_model()

@login_required
def accountant(request):
    return render(request, "accountant/index.html", {})


@user_passes_test(lambda u: u.is_superuser)
def statistics(request):
    now = datetime.now()
    salers = User.objects.filter(role_saler=True)
    lifters = User.objects.filter(role_lifter=True)
    drivers = User.objects.filter(role_driver=True)
    admins = User.objects.filter(role_admin=True)
    am_qs_all = [obj for obj in AdvanceMoney.objects.select_related('order').all() if obj.order.fulfilled==False]
    am_total = 0
    for am in am_qs_all:
        if am.order.full_money_date:
            am_total += am.order.total
        else:
            am_total += am.advance_money
    return render(request, "statistics/statistics.html", locals())


class OrderMonthArchiveView(MonthArchiveView):
    queryset = Order.objects.all()
    date_field = "sale_date"
    template_name = 'statistics/order_archive_month.html'
    allow_empty = True
    ordering = 'sale_date'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(OrderMonthArchiveView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(OrderMonthArchiveView, self).get_context_data(*args, **kwargs)
        qs = context['object_list']

        total = 0
        for order in qs:
            total += order.total
        context['total'] = total

        all_qs = self.get_queryset()
        realiz_cashin_qs = all_qs.filter(full_money_date__month=self.get_month()).filter(
            full_money_date__year=self.get_year())

        realiz_cashin_total = 0
        for order in realiz_cashin_qs:
            realiz_cashin_total += order.total

        context['realiz_cashin_total'] = realiz_cashin_total
        context['realiz_cashin_qs'] = realiz_cashin_qs

        realiz_qs = [obj for obj in qs if obj.fulfilled==False]

        realiz_total = 0
        for order in realiz_qs:
            realiz_total += order.total
        context['realiz_total'] = realiz_total
        context['realiz_qs'] = realiz_qs

        return context


class OrderWeekArchiveView(WeekArchiveView):
    queryset = Order.objects.all()
    date_field = "sale_date"
    week_format = "%W"
    template_name = 'statistics/order_archive_week.html'
    allow_empty = True
    ordering = 'sale_date'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(OrderWeekArchiveView, self).dispatch(*args, **kwargs)


class OrderDayArchiveView(DayArchiveView):
    queryset = Order.objects.all()
    date_field = "sale_date"
    template_name = 'statistics/order_archive_day.html'
    allow_empty = True
    ordering = 'sale_date'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(OrderDayArchiveView, self).dispatch(*args, **kwargs)

