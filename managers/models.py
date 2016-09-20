# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save

from uuslug import slugify

from Feniks_CMS import settings


############### Категории ###############
class ActiveCategoryManager(models.Manager):
    def get_query_set(self):
        return super(ActiveCategoryManager, self).get_query_set().filter(is_active=True)


class Category(models.Model):
    name = models.CharField(u'Название категории', max_length=150)
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
    name = models.TextField(u'Название товара', unique=True)
    slug = models.SlugField(max_length=255, unique=True,
                            help_text='Unique value for product page URL, created from name.')
    # categories = models.ForeignKey(Category, verbose_name=u'Категория')
    min_price = models.IntegerField(u'Мин. цена', blank=True, null=True)
    max_price = models.IntegerField(u'Макс. цена', blank=True, null=True)
    is_active = models.BooleanField(u'Активно', default=True)
    description = models.TextField(u'Описание', blank=True, null=True)
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


def pre_save_product_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)

pre_save.connect(pre_save_product_receiver, sender=Product)

####################################################



################## Заказы ##################
class ActiveOrderManager(models.Manager):
    def get_query_set(self):
        return super(ActiveOrderManager, self).get_query_set().filter(is_active=True)


class Order(models.Model):
    created = models.DateTimeField(u'Создан', auto_now_add=True)
    last_updated = models.DateTimeField(u'Изменен', auto_now=True)
    # Продажа
    order_num = models.CharField(u'Номер договора', max_length=250, null=True)
    saler = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'Менеджер', null=True, related_name='saler')
    sale_date = models.DateField(u'Дата продажи', null=True)
    customer_name = models.CharField(u'ФИО покупателя', max_length=150, blank=True, null=True)
    customer_addres = models.TextField(u'Адрес доставки', blank=True, null=True)
    customer_phone = models.CharField(u'Номер телефона', max_length=250, blank=True, null=True)
    # Полная сумма
    kredit = models.BooleanField(u'Кредит', default=False)
    delivery_money = models.IntegerField(u'Стоимость доставки', blank=True, null=True)
    full_money_date = models.DateField(u'Дата получения всей суммы', blank=True, null=True)
    # Администратор
    admin_check = models.BooleanField(u'Проверено админом', default=False)
    admin_who_checked = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'Проверивший админ', null=True, related_name='admin')
    is_active = models.BooleanField(u'Активно', default=True)
    # Бухгалтер
    accountant_check = models.BooleanField(u'Проверено бухгалтером', default=False)
    objects = models.Manager()
    active = ActiveOrderManager()

    class Meta:
        ordering = ['sale_date']
        verbose_name = u'Договор'
        verbose_name_plural = u'Договоры'

    def __unicode__(self):
        return u'Договор №{}'.format(self.order_num)

    @property
    def quantity(self):
        order_items = OrderItem.objects.filter(order=self)
        return len(order_items)

    @property
    def total(self):
        total = 0
        order_items = OrderItem.objects.filter(order=self)
        for item in order_items:
            total += item.total_with_discount
        return total

    @property
    def total_advance_money(self):
        total = 0
        amoney = AdvanceMoney.objects.filter(order=self)
        for item in amoney:
            total += item.advance_money
        return total

    @property
    def fullpayed(self):
        if self.full_money_date:
            return True
        else:
            return False

    def get_absolute_url(self):
        return reverse('order_details', args=(self.id,))


################################################

################ Задаток #################
class ActiveAdvanceMoneyManager(models.Manager):
    def get_query_set(self):
        return super(ActiveAdvanceMoneyManager, self).get_query_set().filter(is_active=True)


class AdvanceMoney(models.Model):
    order = models.ForeignKey(Order, verbose_name=u'Договор')
    date = models.DateField(u'Дата получения задатка', null=True)
    advance_money = models.IntegerField(u'Сумма задатка')
    is_active = models.BooleanField(u'Активно', default=True)
    objects = models.Manager()
    active = ActiveAdvanceMoneyManager()

    class Meta:
        ordering = ['date']
        verbose_name = u'Задаток'
        verbose_name_plural = u'Задатки'

    def __unicode__(self):
        return u'Задаток #{}'.format(self.id)


##################################


################ Доставка #################
class ActiveDeliveryManager(models.Manager):
    def get_query_set(self):
        return super(ActiveDeliveryManager, self).get_query_set().filter(is_active=True)


class Delivery(models.Model):
    delivery_num = models.IntegerField(u'Номер доставки (реализации)', null=True, blank=True)
    date = models.DateField(u'Дата доставки/самовывоза', null=True)
    selfdrive = models.BooleanField(u'Самовывоз', default=False)
    lifter = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=u'Грузчик', related_name='lifter_user',
                                    blank=True, null=True)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'Водитель', related_name='driver_user',
                               blank=True, null=True)
    addres = models.TextField(u'Адрес доставки', blank=True, null=True)
    price = models.IntegerField(u'Стоимость заноса', blank=True, null=True)
    is_active = models.BooleanField(u'Активно', default=True)
    objects = models.Manager()
    active = ActiveDeliveryManager()

    class Meta:
        ordering = ['date']
        verbose_name = u'Доставка'
        verbose_name_plural = u'Доставки'

    def __unicode__(self):
        return u'Доставка №{}'.format(self.delivery_num)


##################################

################## Позиция договора ###################
class ActiveOrderItemManager(models.Manager):
    def get_query_set(self):
        return super(ActiveOrderItemManager, self).get_query_set().filter(is_active=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name=u'Договор')
    product = models.ForeignKey(Product, verbose_name=u'Товар')
    quantity = models.IntegerField(u'Количество', default=1)
    price = models.IntegerField(u'Цена продажи')
    discount = models.IntegerField(u'Скидка', default=0)
    present = models.BooleanField(u'Наличие', default=False)
    # Заказ у поставщика
    supplier_invoice_date = models.DateField(u'Дата заказа у поставщика', blank=True, null=True)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'Администратор', related_name='admin_user',
                              null=True, blank=True)
    supplier_delivered_date = models.DateField(u'Дата получения от поставщика', blank=True, null=True)
    # Отгрузка
    delivery = models.ForeignKey(Delivery, verbose_name=u'Доставка', blank=True, null=True)

    is_active = models.BooleanField(u'Активно', default=True)
    objects = models.Manager()
    active = ActiveOrderItemManager()

    class Meta:
        verbose_name = u'Позиция договора'
        verbose_name_plural = u'Позиции договора'

    @property
    def total(self):
        return self.quantity * self.price

    @property
    def total_with_discount(self):
        return self.quantity * self.price - self.discount

    @property
    def name(self):
        return self.product.name

    @property
    def ordered_from_supplier(self):
        if self.supplier_invoice_date:
            return True
        else:
            return False

    @property
    def received_from_supplier(self):
        if self.supplier_delivered_date:
            return True
        else:
            return False

    @property
    def delivered(self):
        if self.delivery:
            return True
        else:
            return False

    def __unicode__(self):
        return u'Позиция договора: {}'.format(self.product.name)

    def get_absolute_url(self):
        return self.product.get_absolute_url()

################################################################
