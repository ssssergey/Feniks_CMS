from django.shortcuts import render
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic.dates import MonthArchiveView, WeekArchiveView, DayArchiveView

from managers.models import Order, AdvanceMoney


@user_passes_test(lambda u: u.is_superuser)
def statistics(request):
    now = datetime.now()
    return render(request, "statistics/statistics.html", locals())


class OrderMonthArchiveView(MonthArchiveView):
    queryset = Order.objects.all()
    date_field = "sale_date"
    template_name = 'statistics/order_archive_month.html'
    allow_empty = True

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
        realiz_qs = qs.filter(full_money_date__isnull=False)

        realiz_total = 0
        for order in realiz_qs:
            realiz_total += order.total
        context['realiz_total'] = realiz_total
        context['realiz_qs'] = realiz_qs

        am_qs = AdvanceMoney.objects.filter(order__in=qs)
        am_total = 0
        for am in am_qs:
            am_total += am.advance_money
        context['am_total'] = am_total
        context['am_qs'] = am_qs

        all_qs = self.get_queryset()
        realiz_cashin_qs = all_qs.filter(full_money_date__month=self.get_month())

        realiz_cashin_total = 0
        for order in realiz_cashin_qs:
            realiz_cashin_total += order.total
        context['realiz_cashin_total'] = realiz_cashin_total
        context['realiz_cashin_qs'] = realiz_cashin_qs


        am_cashin_qs = AdvanceMoney.objects.filter(date__month=self.get_month())
        am_cashin_total = 0
        for am in am_cashin_qs:
            am_cashin_total += am.advance_money
        context['am_cashin_total'] = am_cashin_total
        context['am_cashin_qs'] = am_cashin_qs

        return context

class OrderWeekArchiveView(WeekArchiveView):
    queryset = Order.objects.all()
    date_field = "sale_date"
    week_format = "%W"
    template_name = 'statistics/order_archive_week.html'
    allow_empty = True

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(OrderWeekArchiveView, self).dispatch(*args, **kwargs)


class OrderDayArchiveView(DayArchiveView):
    queryset = Order.objects.all()
    date_field = "sale_date"
    template_name = 'statistics/order_archive_day.html'
    allow_empty = True

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(OrderDayArchiveView, self).dispatch(*args, **kwargs)
