# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from Feniks_CMS import settings

############### Категории ###############
class ActiveCategoryManager(models.Manager):
    def get_query_set(self):
        return super(ActiveCategoryManager, self).get_query_set().filter(is_active=True)


class Category(models.Model):
    name = models.CharField(u'Название категории', max_length=50)
    slug = models.SlugField(max_length=50, unique=True,
                            help_text='Unique value for product page URL, created from name.')
    is_active = models.BooleanField(u'Активна', default=True)
    objects = models.Manager()
    active = ActiveCategoryManager()

    class Meta:
        db_table = 'categories'
        ordering = ['-name']
        verbose_name = u'Категория'
        verbose_name_plural = u'Категории'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', args=(self.slug,))
##############################################

################### Товары ####################
class ActiveProductManager(models.Manager):
    def get_query_set(self):
        return super(ActiveProductManager, self).get_query_set().filter(is_active=True)


class Product(models.Model):
    name = models.CharField(u'Название товара', max_length=255)
    slug = models.SlugField(max_length=255, unique=True,
                            help_text='Unique value for product page URL, created from name.')
    categories = models.ForeignKey(Category, verbose_name=u'Категория')
    min_price = models.IntegerField(u'Мин. цена', blank=True, null=True)
    max_price = models.IntegerField(u'Макс. цена', blank=True, null=True)
    is_active = models.BooleanField(u'Активно', default=True)
    description = models.TextField(u'Описание', blank=True, null=True, help_text=u'Введите любое произвольное описание, если необходимо.')
    created_at = models.DateTimeField(u'Создан', auto_now_add=True)
    updated_at = models.DateTimeField(u'Изменен', auto_now=True)
    objects = models.Manager()
    active = ActiveProductManager()

    class Meta:
        db_table = 'products'
        ordering = ['name']
        verbose_name = u'Товар'
        verbose_name_plural = u'Товары'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product', args=(self.slug,))
####################################################

################## Заказы ##################
class ActiveOrderManager(models.Manager):
    def get_query_set(self):
        return super(ActiveOrderManager, self).get_query_set().filter(is_active=True)

class Order(models.Model):
    # each individual status
    # ORDER_STATUSES = (
    #     ('not_paid', u'Неоплачен'), ('advance_money', u'Получен задаток'), ('full_paid', u'Оплачен полностью'),
    #     ('canceled', u'Отменен'), ('completed', u'Завершен'))
    created = models.DateTimeField(u'Создан', auto_now_add=True)
    last_updated = models.DateTimeField(u'Изменен', auto_now=True)
    sale_date = models.DateField(u'Дата продажи', null=True)
    advance_money_date = models.DateField(u'Дата получения задатка', blank=True, null=True)
    realization_date = models.DateField(u'Дата реализации', blank=True, null=True)
    advance_money = models.IntegerField(u'Сумма задатка', blank=True, null=True)
    # status = models.CharField(u'Статус', max_length=150, choices=ORDER_STATUSES)
    saler = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'Менеджер', blank=True, null=True)
    is_active = models.BooleanField(u'Активно', default=False)
    objects = models.Manager()
    active = ActiveOrderManager()

    class Meta:
        verbose_name = u'Заказ'
        verbose_name_plural = u'Заказы'

    def __unicode__(self):
        return u'Заказ #{}'.format(self.id)

    @property
    def quantity(self):
        order_items = OrderItem.objects.filter(order=self)
        return len(order_items)

    @property
    def total(self):
        total = 0
        order_items = OrderItem.objects.filter(order=self)
        for item in order_items:
            total += item.total
        return total

    def get_absolute_url(self):
        return reverse('order_details', args=(self.id,))
################################################

################## Позиция заказа ###################
class ActiveOrderItemManager(models.Manager):
    def get_query_set(self):
        return super(ActiveOrderItemManager, self).get_query_set().filter(is_active=True)

class OrderItem(models.Model):
    product = models.ForeignKey(Product, verbose_name=u'Товар')
    quantity = models.IntegerField(u'Количество', default=1)
    price = models.IntegerField(u'Цена продажи')
    order = models.ForeignKey(Order, verbose_name=u'Заказ')
    is_active = models.BooleanField(u'Активно', default=False)
    objects = models.Manager()
    active = ActiveOrderItemManager()

    class Meta:
        verbose_name = u'Позиция заказа'
        verbose_name_plural = u'Позиции заказа'

    @property
    def total(self):
        return self.quantity * self.price

    @property
    def name(self):
        return self.product.name


    def __unicode__(self):
        result = self.product.name
        return u'Товар заказа: {}'.format(result)

    def get_absolute_url(self):
        return self.product.get_absolute_url()
################################################################