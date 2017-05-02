from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..views import OrderCreate
from ..models import Order, OrderItem, AdvanceMoney, Delivery, Product

User = get_user_model()

class OrderTestCase(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.get_or_create(username='testuser')[0])

    def test_index(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_create_order_get(self):
        response = self.client.get(reverse('order_create'))
        self.assertEqual(response.status_code, 200)

    def test_create_order_post(self):
        response = self.client.post(reverse('order_create'), {'order_num': '1', 'sale_date': '29.10.2016'})
        self.assertEqual(response.status_code, 302)
        orders = Order.objects.all()
        self.assertEqual(len(orders), 1)