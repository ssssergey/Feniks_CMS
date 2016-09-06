# -*- coding: utf-8 -*-
import json

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import ListView, CreateView
from uuslug import slugify

from .forms import ProductForm, OrderForm
from .models import Order, Product, Category, OrderItem


@login_required
def index(request):
    return render(request, "index.html", {})


@login_required
def create_order(request):
    new_order = Order()
    new_order.saler = request.user
    new_order.save()
    request.session['order_id'] = new_order.id
    return HttpResponseRedirect(reverse('product_list'))


@login_required
def product_list(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id', '')
        if order_id:
            order_instance = Order.objects.get(id=int(order_id))
            if 'yes' in request.POST:
                order_instance.is_active = True
                o_form = OrderForm(request.POST, instance=order_instance)
                if o_form.is_valid():
                    o_form.save()
                    oi_set = order_instance.orderitem_set.all()
                    for oi in oi_set:
                        oi.is_active = True
                        oi.save()
                    del request.session['order_id']
                    return HttpResponseRedirect(reverse('order_detail', args=[order_id, ]))

            elif 'no' in request.POST:
                order_instance.delete()
                del request.session['order_id']
                return HttpResponseRedirect(reverse('home'))
    order_id = request.session.get('order_id', '')
    if order_id:
        p_form = ProductForm()
        order_instance = Order.objects.get(id=int(order_id))
        o_form = OrderForm(request.POST or None, instance=order_instance)
        order_items = OrderItem.objects.filter(order__id=order_id)
        context = {
            'order_id': order_id,
            'order_items': order_items,
            'product_list': Product.objects.all(),
            'product_form': p_form,
            'order_form': o_form,
        }
        return render(request, "product_list.html", context)
    else:
        return HttpResponseRedirect(reverse('home'))


def product_add(request):
    form = ProductForm(request.POST)
    print (u'Создание товара!!!!!!!!!!!!!!!!', form)
    if form.is_valid():
        new_product = form.save(commit=False)
        cat_id = request.POST.get('categories')
        new_product.categories = Category.active.get(id=cat_id)
        new_product.slug = slugify(new_product.name)
        new_product.save()
        template = "snippets/product_table_row.html"
        html = render_to_string(template, {'product': new_product})
        response = json.dumps({'success': 'True', 'html': html})
    else:
        html = form.errors.as_ul()
        response = json.dumps({'success': 'False', 'html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')


def add_to_order(request):
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


@login_required
def orders(request):
    orders = Order.active.all()
    page_title = u'Все договоры'
    return render(request, "orders.html", locals())


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    page_title = u'Договор №{}'.format(order.order_num)
    return render(request, "order_detail.html", locals())










# Create your views here.
class ProductList(ListView):
    model = Product
    context_object_name = 'product_list'
    template_name = "product_list.html"

    # def get(self, request, *args, **kwargs):
    #     return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProductList, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['product_list'] = Product.objects.all()
        return context


class OrderList(ListView):
    model = Order
    context_object_name = 'order_list'
    template_name = "index.html"

    # def get(self, request, *args, **kwargs):
    #     return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(OrderList, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['product_list'] = Product.objects.all()
        return context


class CreateOrder(CreateView):
    model = Order
