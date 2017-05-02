# -*- coding: utf-8 -*-
import json
from datetime import datetime, date
from uuslug import slugify

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import DetailView, ListView, UpdateView, DeleteView, TemplateView, View
from django.views.generic.edit import CreateView

from .forms import ProductForm, OrderForm, AdvanceMoneyForm, DeliveryForm, OrderItemForm
from .models import Order, Product, OrderItem, AdvanceMoney, Delivery


@login_required
def index(request):
    if request.user.role_accountant:
        return HttpResponseRedirect(reverse('accountant'))
    else:
        return HttpResponseRedirect(reverse('manager_home'))


@login_required
def manager_home(request):
    if request.user.is_active:
        if request.user.role_admin or request.user.role_accountant or request.user.is_superuser:
            orders = Order.objects.filter(admin_check=False)
            oi_list = OrderItem.objects.filter(delivery=None).select_related('order')
        return render(request, "index.html", locals())
    else:
        raise Http404


class OrderCreate(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "order_create.html"

    def get_success_url(self):
        return reverse('order_fill', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super(OrderCreate, self).form_valid(form)
        obj = form.save()
        obj.saler = self.request.user
        obj.save()
        messages.info(self.request,
                      u'Договор №{} создан. Теперь добавьте укажите товары.'.format(obj.order_num))
        return response


class OrderEdit(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "order_edit.html"

    def get_success_url(self):
        return reverse('order_fill', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        order = self.get_object()
        if order.saler != self.request.user and not self.request.user.role_admin and not self.request.user.role_accountant and not self.request.user.is_superuser:
            messages.warning(self.request,
                             u'Вы не можете изменять этот договор, потому что не вы его заключали.')
            return HttpResponseRedirect(reverse('home'))
        # if not self.request.user.role_admin and not self.request.user.is_superuser:
        #     if order.sale_date != datetime.today():
        #         messages.warning(self.request,
        #                          u'Вы не можете изменить этот договор, потому что уже поздно пить Боржоми. Обратитесь к администратору.')
        #         return HttpResponseRedirect(reverse('home'))
        if self.request.user == order.saler and order.admin_check:
            messages.warning(self.request,
                             u'Вы не можете изменять этот договор, потому он уже проверен администратором.')
            return HttpResponseRedirect(reverse('home'))
        return super(OrderEdit, self).form_valid(form)


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


@login_required
def order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.user == order.saler or request.user.is_superuser or request.user.role_accountant:
        order.delete()
    else:
        messages.warning(request, u'У вас нет прав на удаление этого Договора.')
    return HttpResponseRedirect(reverse('home'))


@login_required
def order_fill(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order_items = OrderItem.objects.filter(order__pk=pk).select_related('order', 'product')
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


# class AjaxableResponseMixin(object):
#     def form_valid(self, form):
#         if self.request.is_ajax():
#             new_product = form.save(commit=False)
#             new_product.slug = slugify(new_product.name)
#             new_product.save()
#             template = "snippets/product_table_row.html"
#             html = render_to_string(template, {'product': new_product})
#             data = {'success': 'True', 'html': html}
#             print ('ajax !!!')
#             return JsonResponse(data)
#         else:
#             print ('not ajax')
#             response = super(AjaxableResponseMixin, self).form_valid(form)
#             return response
#
#     def form_invalid(self, form):
#         response = super(AjaxableResponseMixin, self).form_invalid(form)
#         if self.request.is_ajax():
#             html = form.errors.as_ul()
#             data = {'success': 'False', 'html': html}
#             return JsonResponse(data)
#         else:
#             return response
#
#
# class ProductCreate(LoginRequiredMixin, AjaxableResponseMixin, CreateView):
#     model = Product
#     form_class = ProductForm


@login_required
def product_to_order(request):
    order_id = request.GET.get('order_id')
    product_id = request.GET.get('product_id')
    price = request.GET.get('price')
    discount = request.GET.get('discount') or 0
    quantity = request.GET.get('quantity')
    present = True if request.GET.get('present') == 'true' else False

    order = Order.objects.filter(id=int(order_id)).last()
    if order:
        product = Product.objects.get(id=int(product_id))

        order_item = OrderItem(order=order, product=product, price=price, quantity=quantity, discount=discount,
                               present=present)
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
        order = Order.objects.filter(order_num=order_num).last()
        if order:
            obj = form.save(commit=False)
            obj.order = order
            obj.save()
            messages.info(self.request, u'Предоплата для Договора №{} добавлен.'.format(order_num))
            return HttpResponseRedirect(reverse('home'))
        else:
            form.add_error('order_num', u'Договора №{} не существует.'.format(order_num))
            messages.warning(self.request, u'Договора №{} не существует.'.format(order_num))
            return render(self.request, "advance_money_create.html", locals())


class AdvanceMoneyDetail(LoginRequiredMixin, DetailView):
    model = AdvanceMoney
    template_name = "advance_money_detail.html"

    def get_context_data(self, **kwargs):
        context = super(AdvanceMoneyDetail, self).get_context_data(**kwargs)
        object = self.get_object()
        context['page_title'] = u'Предоплата №{}'.format(object.id)
        return context


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


######################## Delivery #############################
class DeliveryCreate(LoginRequiredMixin, CreateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = "delivery_create.html"

    def get_success_url(self):
        return reverse('delivery_fill', args=(self.get_object().id,))

    def form_valid(self, form):
        obj = form.save()
        messages.info(self.request,
                      u'Доставка №{} создана. Теперь добавьте товары.'.format(obj.delivery_num))
        return HttpResponseRedirect(reverse('delivery_fill', kwargs={'id': obj.id}))


class DeliveryDetail(LoginRequiredMixin, DetailView):
    model = Delivery
    template_name = "delivery_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DeliveryDetail, self).get_context_data(**kwargs)
        object = self.get_object()
        context['page_title'] = u'Доставка №{}'.format(object.delivery_num)
        return context


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


@login_required
def delivery_fill(request, id):
    delivery = get_object_or_404(Delivery, id=id)
    order_items = OrderItem.objects.filter(delivery=delivery).select_related('order', 'product')
    return render(request, "delivery_fill.html", locals())


@login_required
def get_orderitems(request):
    order_num = request.GET.get('order_num')
    order = Order.objects.filter(order_num=order_num).last()
    if order:
        oi_list = OrderItem.objects.filter(order=order).filter(delivery__isnull=True).select_related('order', 'product')
        if oi_list:
            template = "snippets/orderitem_delivery_add.html"
            html = render_to_string(template, {'oi_list': oi_list})
        else:
            html = u'<p>Все позиции договора № {} уже доставлены.</p>'.format(order.order_num)
        response = json.dumps({'success': 'True', 'html': html})
    else:
        html = u'<p>Такого договора не существует!</p>'
        response = json.dumps({'success': 'False', 'html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')


@login_required
def orderitem_to_delivery(request):
    oi_id = request.GET.get('oi_id')
    delivery_num = request.GET.get('delivery_num')
    delivery = Delivery.objects.filter(delivery_num=delivery_num).last()
    if not delivery:
        html = u'Такой доставки не существует!'
        response = json.dumps({'success': 'False', 'html': html})
    else:
        try:
            orderitem = OrderItem.objects.get(id=oi_id)
            orderitem.delivery = delivery
            orderitem.save()
            if not delivery.addres:
                delivery.addres = orderitem.order.customer_addres
                delivery.save()
            template = "snippets/order_item_table_row.html"
            html = render_to_string(template, {'orderitem': orderitem})
            response = json.dumps({'success': 'True', 'html': html})
        except:
            html = u'Такой позиции товара не существует!'
            response = json.dumps({'success': 'False', 'html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')


@login_required
def orderitem_delete_from_delivery(request):
    oi_id = request.GET.get('oi_id')
    try:
        oi = OrderItem.objects.get(id=oi_id)
        oi.delivery = None
        oi.save()
        response = json.dumps({'success': 'True', 'html': u'Удалено'})
    except Exception as e:
        response = json.dumps({'success': 'False', 'html': str(e)})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')


@login_required
def find_delivery(request):
    delivery_num = request.GET.get('delivery_num')
    delivery = Delivery.objects.filter(delivery_num=delivery_num).last()
    if not delivery:
        messages.warning(request, u'Доставки №{} не существует.'.format(delivery_num))
        return render(request, "index.html", {})
    return HttpResponseRedirect(reverse('delivery_detail', kwargs={'pk': delivery.id}))


@login_required
def find_order(request):
    order_num = request.GET.get('order_num')
    order = Order.objects.filter(order_num=order_num).last()
    if not order:
        messages.warning(request, u'Договора №{} не существует.'.format(order_num))
        return render(request, "index.html", {})
    return HttpResponseRedirect(reverse('order_detail', kwargs={'pk': order.id}))


@login_required
def admin_check(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if not order.full_money_date:
        messages.warning(request,
                         u'Администратор, вы не можете пометить этот договор проверенным. Он не оплачен полностью.')
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
