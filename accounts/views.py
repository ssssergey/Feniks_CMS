# -*- coding: utf-8 -*-
import time

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.template import RequestContext
from django.http import Http404
from django.views.generic.dates import MonthArchiveView
from django.contrib.auth.mixins import LoginRequiredMixin

from forms import UserLoginForm
from managers.models import Order, OrderItem, AdvanceMoney, Delivery

User = get_user_model()


class WorkerMonthArchiveView(LoginRequiredMixin, MonthArchiveView):
    queryset = Order.objects.all()
    date_field = "sale_date"
    template_name = 'accounts/workers_archive_month.html'
    allow_empty = True
    month_format = '%m'
    ordering = 'sale_date'

    def get_queryset(self):
        qs = super(WorkerMonthArchiveView, self).get_queryset()
        qs = qs.filter(saler__id=self.kwargs['user_id'])
        return qs

    def get_context_data(self, **kwargs):
        context = super(WorkerMonthArchiveView, self).get_context_data(**kwargs)
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        context['current_user'] = user

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

        am_qs = AdvanceMoney.objects.filter(order__in=qs, order__saler__id=self.kwargs['user_id'],
                                            order__full_money_date__isnull=True)
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

        am_cashin_qs = AdvanceMoney.objects.filter(date__month=self.get_month(),
                                                   order__saler__id=self.kwargs['user_id'],
                                                   order__full_money_date__isnull=True)
        am_cashin_total = 0
        for am in am_cashin_qs:
            am_cashin_total += am.advance_money
        context['am_cashin_total'] = am_cashin_total
        context['am_cashin_qs'] = am_cashin_qs

        # Lifter
        lifts = Delivery.objects.filter(lifter__id=self.kwargs['user_id'], date__month=self.get_month())
        context['lifts'] = lifts

        # Driver
        drives = Delivery.objects.filter(driver__id=self.kwargs['user_id'], date__month=self.get_month())
        context['drives'] = drives

        # Admin
        admins = OrderItem.objects.filter(supplier_invoice_date__month=self.get_month(),
                                          admin_id=self.kwargs['user_id'])
        context['admins'] = admins

        return context


class SalerMonthArchiveView(LoginRequiredMixin, MonthArchiveView):
    queryset = Order.objects.all()
    date_field = "sale_date"
    template_name = 'accounts/salers_archive_month.html'
    allow_empty = True
    month_format = '%m'
    ordering = 'sale_date'

    def get_queryset(self):
        qs = super(SalerMonthArchiveView, self).get_queryset()
        qs = qs.filter(saler__id=self.kwargs['user_id'])
        return qs

    def get_context_data(self, **kwargs):
        context = super(SalerMonthArchiveView, self).get_context_data(**kwargs)
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        context['current_user'] = user

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


class LifterMonthArchiveView(LoginRequiredMixin, MonthArchiveView):
    queryset = Delivery.objects.all()
    date_field = "date"
    template_name = 'accounts/lifters_archive_month.html'
    allow_empty = True
    month_format = '%m'
    ordering = 'date'

    def get_queryset(self):
        qs = super(LifterMonthArchiveView, self).get_queryset()
        qs = qs.filter(lifter__id=self.kwargs['user_id'])
        return qs

    def get_context_data(self, **kwargs):
        context = super(LifterMonthArchiveView, self).get_context_data(**kwargs)
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        context['current_user'] = user

        return context


class DriverMonthArchiveView(LoginRequiredMixin, MonthArchiveView):
    queryset = Delivery.objects.all()
    date_field = "date"
    template_name = 'accounts/drivers_archive_month.html'
    allow_empty = True
    month_format = '%m'
    ordering = 'date'

    def get_queryset(self):
        qs = super(DriverMonthArchiveView, self).get_queryset()
        qs = qs.filter(driver__id=self.kwargs['user_id'])
        return qs

    def get_context_data(self, **kwargs):
        context = super(DriverMonthArchiveView, self).get_context_data(**kwargs)
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        context['current_user'] = user

        driver_lifts = Delivery.objects.filter(lifter__id=self.kwargs['user_id'])
        context['driver_lifts'] = driver_lifts
        return context


class AdminMonthArchiveView(LoginRequiredMixin, MonthArchiveView):
    queryset = OrderItem.objects.all()
    date_field = "supplier_invoice_date"
    template_name = 'accounts/admins_archive_month.html'
    allow_empty = True
    month_format = '%m'

    def get_context_data(self, **kwargs):
        context = super(AdminMonthArchiveView, self).get_context_data(**kwargs)
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        context['current_user'] = user

        return context


# def login_view(request):
#     print(request.user.is_authenticated())
#     page_title = u"Вход"
#     form = UserLoginForm(request.POST or None)
#     if form.is_valid():
#         username = form.cleaned_data.get('username')
#         password = form.cleaned_data.get('password')
#         user = authenticate(username=username, password=password)
#         login(request, user)
#         return redirect('/')
#     return render(request, "accounts/login.html", {"form": form, "page_title": page_title})
#
#
# def logout_view(request):
#     logout(request)
#     return render(request, "index.html", {})


@login_required
def saler(request, id):
    page_title = u'Личный кабинет'
    if request.user.id != int(id) and not request.user.is_superuser:
        raise Http404
    if request.method == 'POST':
        postdata = request.POST.copy()
        print (postdata)
        if postdata['submit'] == u'Удалить':
            order_id = postdata['order_id']
            order = get_object_or_404(Order, id=order_id)
            if order and not order.admin_check:
                order.delete()
                message = u'Заказ удален.'
                messages.success(request, message)
            else:
                message = u'Вы не можете удалить этот заказ.'
                messages.warning(request, message)

    account_user = get_object_or_404(User, id=id)
    orders = Order.objects.filter(saler=account_user)

    user_oi_qs = OrderItem.active.filter(order__saler=account_user)
    user_oi_qs_completed = user_oi_qs.filter(order__full_money_date__isnull=False)
    # user_oi_qs_processed = user_oi_qs.filter(order__status=1)
    # user_oi_qs_submitted = user_oi_qs.filter(order__status=2)
    # user_oi_qs_shipped = user_oi_qs.filter(order__status=3)
    # user_oi_qs_completed = user_oi_qs.filter(order__status=4)
    # user_oi_qs_canceled = user_oi_qs.filter(order__status=0)
    x = 12  # months
    now = time.localtime()
    last_months = [time.localtime(time.mktime((now.tm_year, now.tm_mon - n, 1, 0, 0, 0, 0, 0, 0)))[:2] for n in
                   range(x)]
    # [(2016, 8), (2016, 7), (2016, 6), (2016, 5), (2016, 4), (2016, 3), (2016, 2), (2016, 1), (2015, 12), (2015, 11)]
    data = []
    for couple in last_months:
        month_obj = {
            'month': couple,
            'product_items': [],
            'product_items_completed': [],
            'product_items_money_came': [],
            'month_total': 0,
            'month_total_completed': 0,
            'month_total_money_came': 0,
        }
        month_oi_qs = user_oi_qs.filter(order__sale_date__year=couple[0], order__sale_date__month=couple[1])
        month_oi_qs_completed = user_oi_qs_completed.filter(order__sale_date__year=couple[0],
                                                            order__sale_date__month=couple[1])
        month_oi_qs_money_came = user_oi_qs_completed.filter(order__full_money_date__year=couple[0],
                                                             order__full_money_date__month=couple[1])

        for p in month_oi_qs:
            month_obj['month_total'] += p.total_with_discount
            month_obj['product_items'].append(p)

        for p in month_oi_qs_completed:
            month_obj['month_total_completed'] += p.total_with_discount
            month_obj['product_items_completed'].append(p)
        month_obj['percent'] = 0
        if month_obj['month_total_completed'] < 500000:
            month_obj['percent'] = 1
        else:
            month_obj['percent'] = 1.5
        month_obj['profit'] = month_obj['month_total_completed'] / 100 * month_obj['percent']

        for p in month_oi_qs_money_came:
            month_obj['month_total_money_came'] += p.total_with_discount
            month_obj['product_items_money_came'].append(p)

        data.append(month_obj)

    return render_to_response("accounts/saler.html", locals(), context_instance=RequestContext(request))
