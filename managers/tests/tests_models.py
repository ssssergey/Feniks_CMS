# -*- coding: utf-8 -*-

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..views import OrderCreate
from ..models import Order, OrderItem, AdvanceMoney, Delivery, Product

class OrderTestCase(TestCase):
    def test_delivered(self):
        order = Order.objects.create()
        product = Product.objects.create(name='product')
        oi_1 = OrderItem.objects.create(order=order, price=1, product=product)
        oi_2 = OrderItem.objects.create(order=order, price=1, product=product)
        oi_not = OrderItem.notdelivered_items.count()
        oi_del = OrderItem.delivered_items.count()
        self.assertEqual(oi_not, 2)
        self.assertEqual(oi_del, 0)

class DeliveryTestCase(TestCase):
    def setUp(self):
        self.order = Order.objects.create(order_num=1)
        self.product = Product.objects.create(name=u'Стул')
        self.orderitem = OrderItem.objects.create(order=self.order, price=1, product=self.product)
        self.delivery = Delivery.objects.create(delivery_num=1)

    def test_delete(self):
        self.orderitem.delivery = self.delivery
        self.orderitem.save()

        self.orderitem.refresh_from_db()

        self.assertEqual(self.orderitem.delivery.delivery_num, 1)

        Delivery.objects.get(id=self.delivery.pk).delete()

        self.assertEqual(Delivery.objects.all().count(), 0)

        self.orderitem.refresh_from_db()
        self.assertIsNone(self.orderitem.delivery)