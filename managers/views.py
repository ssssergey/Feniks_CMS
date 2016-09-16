# -*- coding: utf-8 -*-
import json
from datetime import datetime
from uuslug import slugify

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, TemplateView

from .forms import ProductForm, OrderForm, AdvanceMoneyForm, DeliveryForm, OrderItemForm
from .models import Order, Product, Category, OrderItem, AdvanceMoney, Delivery


@login_required
def index(request):
    now = datetime.now()
    limit_date = datetime(2016, 11, 1)
    if now > limit_date:
        raise Http404
    if request.user.role_admin:
        orders = Order.objects.filter(admin_check=False)
        oi_list = OrderItem.objects.filter(order__admin_check=False)
    return render(request, "index.html", locals())


class OrderCreate(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "order_create.html"

    def get_success_url(self):
        return reverse('order_fill', args=(self.get_object().id,))

    def form_valid(self, form):
        obj = form.save()
        obj.saler = self.request.user
        obj.save()
        order_num = obj.order_num
        messages.info(self.request, u'Договор №{} создан. Теперь добавьте укажите товары.'.format(order_num))
        return HttpResponseRedirect(self.get_success_url())


# @login_required
# def order_create(request):
#     form = OrderForm()
#     if request.method == "POST":
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             obj = form.save()
#             obj.saler = request.user
#             obj.save()
#             order_id = obj.id
#             order_num = request.POST.get('order_num')
#             messages.info(request, u'Договор №{} создан. Теперь добавьте укажите товары.'.format(order_num))
#             return HttpResponseRedirect(reverse('order_fill', kwargs={'order_id': order_id}))
#     return render(request, "order_create.html", locals())

class OrderEdit(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "order_edit.html"

    def get_success_url(self):
        return reverse('order_fill', args=(self.get_object().id,))

    def form_valid(self, form):
        order = self.get_object()
        if order.saler != self.request.user and not self.request.user.role_admin and not self.request.user.is_superuser:
            messages.warning(self.request, u'Вы не можете изменять этот договор, потому что не вы его заключали.')
            return HttpResponseRedirect(reverse('home'))
        form.save()
        return HttpResponseRedirect(self.get_success_url())


# @login_required
# def order_edit(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     if order.saler != request.user and not request.user.role_admin and not request.user.is_superuser:
#         messages.warning(request, u'Вы не можете изменять этот договор, потому что не вы его заключали.')
#         return HttpResponseRedirect(reverse('home'))
#     form = OrderForm(instance=order)
#     if request.method == 'POST':
#         form = OrderForm(request.POST, instance=order)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(reverse('order_fill', kwargs={'order_id': order_id}))
#     return render(request, "order_edit.html", locals())


@login_required
def order_list(request):
    orders = Order.active.all()
    page_title = u'Все договоры'
    return render(request, "order_list.html", locals())


class OrderDetail(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "order_detail.html"

    def get_context_data(self, **kwargs):
        context = super(OrderDetail, self).get_context_data(**kwargs)
        order = self.get_object()
        context['page_title'] = u'Договор №{}'.format(order.order_num)
        return context


# @login_required
# def order_detail(request, id):
#     order = get_object_or_404(Order, id=id)
#     page_title = u'Договор №{}'.format(order.order_num)
#     return render(request, "order_detail.html", locals())


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
def orderitem_delete(request):
    oi_id = request.GET.get('oi_id')
    try:
        oi = OrderItem.objects.get(id=oi_id)
        oi.delete()
        response = json.dumps({'success': 'True', 'html': u'Удалено'})
    except Exception as e:
        response = json.dumps({'success': 'False', 'html': str(e)})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')


class OrderItemEdit(LoginRequiredMixin, UpdateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = "orderitem_edit.html"

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        form.save()
        messages.info(self.request, u'Изменения приняты.')
        return HttpResponseRedirect(reverse('home'))


# @login_required
# def orderitem_edit(request, id):
#     orderitem = get_object_or_404(OrderItem, id=id)
#     form = OrderItemForm(instance=orderitem)
#     if request.method == 'POST':
#         form = OrderItemForm(request.POST, instance=orderitem)
#         if form.is_valid():
#             form.save()
#             messages.info(request, u'Изменения приняты.')
#             return HttpResponseRedirect(reverse('home'))
#     return render(request, "orderitem_edit.html", locals())

class AjaxableResponseMixin(object):
    def form_valid(self, form):
        # response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            new_product = form.save(commit=False)
            # cat_id = request.POST.get('categories')
            # new_product.categories = Category.active.get(id=cat_id)
            new_product.slug = slugify(new_product.name)
            new_product.save()
            template = "snippets/product_table_row.html"
            html = render_to_string(template, {'product': new_product})
            data = {
                'success': 'True', 'html': html
            }
            print ('ajax !!!')
            return JsonResponse(data)
        else:
            print ('not ajax')
            response = super(AjaxableResponseMixin, self).form_valid(form)
            return response

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            html = form.errors.as_ul()
            data = {
                'success': 'False', 'html': html
            }
            return JsonResponse(data)
        else:
            return response


class ProductCreate(LoginRequiredMixin, AjaxableResponseMixin, CreateView):
    model = Product
    form_class = ProductForm



# @login_required
# def product_create(request):
#     form = ProductForm(request.POST)
#     if form.is_valid():
#         new_product = form.save(commit=False)
#         # cat_id = request.POST.get('categories')
#         # new_product.categories = Category.active.get(id=cat_id)
#         new_product.slug = slugify(new_product.name)
#         new_product.save()
#         template = "snippets/product_table_row.html"
#         html = render_to_string(template, {'product': new_product})
#         response = json.dumps({'success': 'True', 'html': html})
#     else:
#         html = form.errors.as_ul()
#         print(html)
#         response = json.dumps({'success': 'False', 'html': html})
#     return HttpResponse(response, content_type='application/javascript; charset=utf-8')


@login_required
def product_to_order(request):
    order_id = request.GET.get('order_id')
    product_id = request.GET.get('product_id')
    price = request.GET.get('price')
    discount = request.GET.get('discount')
    quantity = request.GET.get('quantity')
    present = request.GET.get('present')
    if present == 'true':
        present = True
    elif present == 'false':
        present = False
    else:
        raise Http404

    order = Order.objects.get(id=int(order_id))
    product = Product.objects.get(id=int(product_id))

    order_item = OrderItem()
    order_item.order = order
    order_item.product = product
    order_item.price = int(price)
    if discount:
        order_item.discount = int(discount)
    order_item.quantity = int(quantity)
    order_item.present = present
    order_item.save()

    template = "snippets/order_item_table_row.html"
    html = render_to_string(template, {'orderitem': order_item})
    response = json.dumps({'success': 'True', 'html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')


######################### Advance Money ##########################
class AdvanceMoneyCreate(LoginRequiredMixin, CreateView):
    model = AdvanceMoney
    form_class = AdvanceMoneyForm
    template_name = "advance_money_create.html"

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        order_num = self.request.POST.get('order_num')
        try:
            order = Order.objects.get(order_num=order_num)
            obj = form.save(commit=False)
            obj.order = order
            obj.save()
            messages.info(self.request, u'Задаток для Договора №{} добавлен.'.format(order_num))
            return HttpResponseRedirect(reverse('home'))
        except:
            form.add_error('order_num', u'Договора №{} не существует.'.format(order_num))
            messages.warning(self.request, u'Договора №{} не существует.'.format(order_num))
            return render(self.request, "advance_money_create.html", locals())


# @login_required
# def advance_money_create(request):
#     form = AdvanceMoneyForm()
#     if request.method == "POST":
#         form = AdvanceMoneyForm(request.POST)
#         if form.is_valid():
#             order_num = request.POST.get('order_num')
#             try:
#                 order = Order.objects.get(order_num=order_num)
#                 obj = form.save(commit=False)
#                 obj.order = order
#                 obj.save()
#                 messages.info(request, u'Задаток для Договора №{} добавлен.'.format(order_num))
#                 return HttpResponseRedirect(reverse('home'))
#             except:
#                 form.add_error('order_num', u'Договора №{} не существует.'.format(order_num))
#                 messages.warning(request, u'Договора №{} не существует.'.format(order_num))
#     return render(request, "advance_money_create.html", locals())


class AdvanceMoneyDetail(LoginRequiredMixin, DetailView):
    model = AdvanceMoney
    template_name = "advance_money_detail.html"

    def get_context_data(self, **kwargs):
        context = super(AdvanceMoneyDetail, self).get_context_data(**kwargs)
        object = self.get_object()
        context['page_title'] = u'Задаток №{}'.format(object.id)
        return context


# @login_required
# def advance_money_detail(request, id):
#     am = get_object_or_404(AdvanceMoney, id=id)
#     return render(request, "advance_money_detail.html", locals())


class AdvanceMoneyEdit(LoginRequiredMixin, UpdateView):
    model = AdvanceMoney
    form_class = AdvanceMoneyForm
    template_name = "advance_money_edit.html"

    def get_success_url(self):
        return reverse('advance_money_detail', kwargs={'pk': self.get_object().id})

    def form_valid(self, form):
        form.save()
        messages.info(self.request, u'Изменения приняты.')
        return HttpResponseRedirect(self.get_success_url())


# @login_required
# def advance_money_edit(request, id):
#     am = get_object_or_404(AdvanceMoney, id=id)
#     form = AdvanceMoneyForm(instance=am)
#     if request.method == 'POST':
#         form = AdvanceMoneyForm(request.POST, instance=am)
#         if form.is_valid():
#             form.save()
#             messages.info(request, u'Изменения приняты.')
#             return HttpResponseRedirect(reverse('advance_money_detail', kwargs={'id': id}))
#     return render(request, "advance_money_edit.html", locals())


######################## Delivery #############################
class DeliveryCreate(LoginRequiredMixin, CreateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = "delivery_create.html"

    def get_success_url(self):
        return reverse('delivery_fill', args=(self.get_object().id,))

    def form_valid(self, form):
        obj = form.save()
        delivery_id = obj.id
        delivery_num = obj.delivery_num
        messages.info(self.request, u'Доставка №{} создана. Теперь добавьте укажите товары.'.format(delivery_num))
        return HttpResponseRedirect(reverse('delivery_fill', kwargs={'id': delivery_id}))


# @login_required
# def delivery_create(request):
#     form = DeliveryForm()
#     if request.method == "POST":
#         form = DeliveryForm(request.POST)
#         if form.is_valid():
#             obj = form.save()
#             delivery_id = obj.id
#             delivery_num = request.POST.get('delivery_num')
#             messages.info(request, u'Доставка №{} создана. Теперь добавьте укажите товары.'.format(delivery_num))
#             # return render(request, "delivery_fill.html", locals())
#             return HttpResponseRedirect(reverse('delivery_fill', kwargs={'id': delivery_id}))
#     return render(request, "delivery_create.html", locals())


class DeliveryDetail(LoginRequiredMixin, DetailView):
    model = Delivery
    template_name = "delivery_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DeliveryDetail, self).get_context_data(**kwargs)
        object = self.get_object()
        context['page_title'] = u'Доставка №{}'.format(object.delivery_num)
        return context


# @login_required
# def delivery_detail(request, id):
#     delivery = get_object_or_404(Delivery, id=id)
#     page_title = u'Доставка №{}'.format(delivery.delivery_num)
#     return render(request, "delivery_detail.html", locals())

class DeliveryEdit(LoginRequiredMixin, UpdateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = "delivery_edit.html"

    def get_success_url(self):
        return reverse('delivery_fill', kwargs={'id': self.get_object().id})

    def form_valid(self, form):
        form.save()
        messages.info(self.request, u'Изменения приняты.')
        return HttpResponseRedirect(self.get_success_url())


# @login_required
# def delivery_edit(request, id):
#     delivery = get_object_or_404(Delivery, id=id)
#     form = DeliveryForm(instance=delivery)
#     if request.method == 'POST':
#         form = DeliveryForm(request.POST, instance=delivery)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(reverse('delivery_fill', kwargs={'id': id}))
#     return render(request, "delivery_edit.html", locals())


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
    return HttpResponseRedirect(reverse('delivery_detail', kwargs={'pk': delivery_id}))


@login_required
def find_order(request):
    order_num = request.GET.get('order_num')
    try:
        order = Order.objects.get(order_num=order_num)
    except:
        messages.warning(request, u'Договора №{} не существует.'.format(order_num))
        return render(request, "index.html", {})
    order_id = order.id
    return HttpResponseRedirect(reverse('order_detail', kwargs={'pk': order_id}))


@login_required
def admin_check(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if not order.full_money_date:
        messages.warning(request,
                         u'Администратор, вы не можете пометить этот договор проверенным. Он не оплачен полостью.')
        return HttpResponseRedirect(reverse('home'))
    oi_list = OrderItem.objects.filter(order=order)
    for oi in oi_list:
        if not oi.delivery:
            messages.warning(request,
                             u'Администратор, вы не можете пометить этот договор проверенным. В этом договре остались не доставленные позиции.')
            return HttpResponseRedirect(reverse('home'))
    order.admin_check = True
    order.admin_who_checked = request.user
    order.save()
    messages.info(request, u'Подтверждение принято.')
    return HttpResponseRedirect(reverse('home'))
