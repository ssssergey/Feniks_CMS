# -*- coding: utf-8 -*-
import json
from uuslug import slugify

from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import ListView, CreateView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import Order, Product, Category, OrderItem
from .forms import ProductForm, OrderForm


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
                    return HttpResponseRedirect(reverse('home'))

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
    print (form)
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
    quantity = request.GET.get('quantity')

    order = Order.objects.get(id=int(order_id))
    product = Product.objects.get(id=int(product_id))

    order_item = OrderItem()
    order_item.order = order
    order_item.product = product
    order_item.price = int(price)
    order_item.quantity = int(quantity)
    order_item.save()

    template = "snippets/order_item_table_row.html"
    html = render_to_string(template, {'orderitem': order_item})
    response = json.dumps({'success': 'True', 'html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')
















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
