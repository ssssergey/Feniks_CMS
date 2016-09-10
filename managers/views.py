# -*- coding: utf-8 -*-
import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import ListView, CreateView
from uuslug import slugify

from .forms import ProductForm, OrderForm, AdvanceMoneyForm, DeliveryForm
from .models import Order, Product, Category, OrderItem, AdvanceMoney, Delivery


@login_required
def index(request):
    return render(request, "index.html", locals())


@login_required
def order_create(request):
    form = OrderForm()
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.saler = request.user
            obj.save()
            order_id = obj.id
            order_num = request.POST.get('order_num')
            messages.warning(request, u'Договор №{} создан. Теперь добавьте укажите товары.'.format(order_num))
            return HttpResponseRedirect(reverse('order_fill', kwargs={'order_id': order_id}))
    return render(request, "order_create.html", locals())


@login_required
def order_edit(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.warning(request, u'Изменения приняты.')
            return HttpResponseRedirect(reverse('order_fill', kwargs={'order_id': order_id}))
    return render(request, "order_edit.html", locals())


@login_required
def order_list(request):
    orders = Order.active.all()
    page_title = u'Все договоры'
    return render(request, "order_list.html", locals())


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    page_title = u'Договор №{}'.format(order.order_num)
    return render(request, "order_detail.html", locals())


@login_required
def order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.user == order.saler or request.user.is_superuser:
        order.delete()
    else:
        messages.warning(request, u'У вас нет прав на удаление этого Договора.')
    del request.session['order_id']
    return HttpResponseRedirect(reverse('home'))


@login_required
def order_fill(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order__id=order_id)
    product_list = Product.objects.all()
    product_form = ProductForm()
    return render(request, "order_fill.html", locals())

@login_required
def product_create(request):
    form = ProductForm(request.POST)
    if form.is_valid():
        new_product = form.save(commit=False)
        # cat_id = request.POST.get('categories')
        # new_product.categories = Category.active.get(id=cat_id)
        new_product.slug = slugify(new_product.name)
        new_product.save()
        template = "snippets/product_table_row.html"
        html = render_to_string(template, {'product': new_product})
        response = json.dumps({'success': 'True', 'html': html})
    else:
        html = form.errors.as_ul()
        print(html)
        response = json.dumps({'success': 'False', 'html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@login_required
def product_to_order(request):
    order_id = request.GET.get('order_id')
    product_id = request.GET.get('product_id')
    price = request.GET.get('price')
    discount = request.GET.get('discount')
    quantity = request.GET.get('quantity')

    order = Order.objects.get(id=int(order_id))
    product = Product.objects.get(id=int(product_id))

    order_item = OrderItem()
    order_item.order = order
    order_item.product = product
    order_item.price = int(price)
    if discount:
        order_item.discount = int(discount)
    order_item.quantity = int(quantity)
    order_item.save()

    template = "snippets/order_item_table_row.html"
    html = render_to_string(template, {'orderitem': order_item})
    response = json.dumps({'success': 'True', 'html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')


######################### Advance Money ##########################
@login_required
def advance_money_create(request):
    form = AdvanceMoneyForm()
    if request.method == "POST":
        form = AdvanceMoneyForm(request.POST)
        if form.is_valid():
            order_num = request.POST.get('order_num')
            try:
                order = Order.objects.get(order_num=order_num)
                obj = form.save(commit=False)
                obj.order = order
                obj.save()
                messages.warning(request, u'Задаток для Договора №{} добавлен.'.format(order_num))
                return HttpResponseRedirect(reverse('home'))
            except:
                form.add_error('order_num', u'Договора №{} не существует.'.format(order_num))
                messages.warning(request, u'Договора №{} не существует.'.format(order_num))
    return render(request, "advance_money_create.html", locals())


@login_required
def advance_money_detail(request, id):
    am = get_object_or_404(AdvanceMoney, id=id)
    return render(request, "advance_money_detail.html", locals())


@login_required
def advance_money_edit(request, id):
    am = get_object_or_404(AdvanceMoney, id=id)
    form = AdvanceMoneyForm(instance=am)
    if request.method == 'POST':
        form = AdvanceMoneyForm(request.POST, instance=am)
        if form.is_valid():
            form.save()
            messages.warning(request, u'Изменения приняты.')
            return HttpResponseRedirect(reverse('advance_money_detail', kwargs={'id': id}))
    return render(request, "advance_money_edit.html", locals())


######################## Delivery #############################
@login_required
def delivery_create(request):
    form = DeliveryForm()
    if request.method == "POST":
        form = DeliveryForm(request.POST)
        if form.is_valid():
            obj = form.save()
            delivery_id = obj.id
            delivery_num = request.POST.get('delivery_num')
            messages.warning(request, u'Доставка №{} создана. Теперь добавьте укажите товары.'.format(delivery_num))
            # return render(request, "delivery_fill.html", locals())
            return HttpResponseRedirect(reverse('delivery_fill', kwargs={'id': delivery_id}))
    return render(request, "delivery_create.html", locals())


@login_required
def delivery_detail(request, id):
    delivery = get_object_or_404(Delivery, id=id)
    page_title = u'Доставка №{}'.format(delivery.delivery_num)
    return render(request, "delivery_detail.html", locals())


@login_required
def delivery_edit(request, id):
    delivery = get_object_or_404(Delivery, id=id)
    form = DeliveryForm(instance=delivery)
    if request.method == 'POST':
        form = DeliveryForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            messages.warning(request, u'Изменения приняты.')
            return HttpResponseRedirect(reverse('delivery_fill', kwargs={'id': id}))
    return render(request, "delivery_edit.html", locals())


@login_required
def delivery_fill(request, id):
    delivery = get_object_or_404(Delivery, id=id)
    order_items = OrderItem.objects.filter(delivery=delivery)
    return render(request, "delivery_fill.html", locals())

@login_required
def get_orderitems(request):
    order_num = request.GET.get('order_num')
    try:
        order = Order.objects.get(order_num=order_num)
        oi_list = OrderItem.objects.filter(order=order).filter(delivery__isnull=True)
        template = "snippets/orderitem_delivery_add.html"
        html = render_to_string(template, {'oi_list': oi_list})
        response = json.dumps({'success': 'True', 'html': html})
    except Exception as e:
        html = u'Такого договора не существует!'
        response = json.dumps({'success': 'False', 'html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@login_required
def orderitem_to_delivery(request):
    oi_id = request.GET.get('oi_id')
    delivery_num = request.GET.get('delivery_num')
    try:
        delivery = Delivery.objects.get(delivery_num=delivery_num)
    except:
        delivery = None
        html = u'Такой доставки не существует!'
        response = json.dumps({'success': 'False', 'html': html})
    if delivery:
        try:
            orderitem = OrderItem.objects.get(id=oi_id)
            orderitem.delivery = delivery
            orderitem.save()
            template = "snippets/order_item_table_row.html"
            html = render_to_string(template, {'orderitem': orderitem})
            response = json.dumps({'success': 'True', 'html': html})
        except:
            html = u'Такой позиции товара не существует!'
            response = json.dumps({'success': 'False', 'html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@login_required
def find_delivery(request):
    delivery_num = request.GET.get('delivery_num')
    try:
        delivery = Delivery.objects.get(delivery_num=delivery_num)
    except:
        messages.warning(request, u'Доставки №{} не существует.'.format(delivery_num))
        return render(request, "index.html", {})
    delivery_id = delivery.id
    return HttpResponseRedirect(reverse('delivery_detail', kwargs={'id': delivery_id}))

@login_required
def find_order(request):
    order_num = request.GET.get('order_num')
    try:
        order = Order.objects.get(order_num=order_num)
    except:
        messages.warning(request, u'Договора №{} не существует.'.format(order_num))
        return render(request, "index.html", {})
    order_id = order.id
    return HttpResponseRedirect(reverse('order_detail', kwargs={'order_id': order_id}))
