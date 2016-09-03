# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import ListView, CreateView
from .models import Order, Product
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, "index.html", {})

def product_list(request):
    form = None
    context = {
        'product_list': Product.objects.all(),
        'product_form': form,
    }
    return render(request, "product_list.html", context)













# Create your views here.
class ProductList(ListView):
    model = Product
    context_object_name = 'product_list'
    template_name="product_list.html"

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
    template_name="index.html"

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


