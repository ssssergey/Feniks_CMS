# -*- coding: utf-8 -*-
import time

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.template import RequestContext

from forms import UserLoginForm
from managers.models import Order, OrderItem


# CUSTOM LOGIN
def login_view(request):
    print(request.user.is_authenticated())
    page_title = u"Вход"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('/')
    return render(request, "accounts/login.html", {"form": form, "page_title": page_title})


# CUSTOM LOGOUT
def logout_view(request):
    logout(request)
    return render(request, "index.html", {})


@login_required
def my_account(request, template_name="accounts/my_account.html"):
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
    name = request.user.get_full_name()
    page_title = u'Личный кабинет'
    orders = Order.objects.filter(saler=request.user)
    user = request.user

    user_oi_qs = OrderItem.active.filter(order__saler=user)
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
            month_obj['month_total'] += p.total
            month_obj['product_items'].append(p)

        for p in month_oi_qs_completed:
            month_obj['month_total_completed'] += p.total
            month_obj['product_items_completed'].append(p)
        month_obj['percent'] = 0
        if month_obj['month_total_completed'] < 500000:
            month_obj['percent'] = 1
        else:
            month_obj['percent'] = 1.5
        month_obj['profit'] = month_obj['month_total_completed'] / 100 * month_obj['percent']

        for p in month_oi_qs_money_came:
            month_obj['month_total_money_came'] += p.total
            month_obj['product_items_money_came'].append(p)

        data.append(month_obj)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
