# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save, pre_delete
from uuslug import slugify

from Feniks_CMS import settings


################ Доставка #################
class ActiveDeliveryManager(models.Manager):
    def get_query_set(self):
        return super(ActiveDeliveryManager, self).get_query_set().filter(
            is_active=True)


class Delivery(models.Model):
    created = models.DateTimeField(u'Создан', auto_now_add=True)
    last_updated = models.DateTimeField(u'Изменен', auto_now=True)
    delivery_num = models.CharField(u'Номер доставки (реализации)', max_length=50)
    date = models.DateField(u'Дата доставки/самовывоза', null=True)
    selfdrive = models.BooleanField(u'Самовывоз', default=False)
    lifter = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                    verbose_name=u'Грузчик',
                                    related_name='lifter_user',
                                    blank=True)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL,
                               verbose_name=u'Водитель',
                               related_name='driver_user',
                               blank=True, null=True)
    addres = models.TextField(u'Адрес доставки', blank=True, null=True,
                              help_text=u'Если оставите адрес пустым, он будет скопирован из договора.')
    price_delivery = models.IntegerField(u'Стоимость доставки', default=0)
    price = models.IntegerField(u'Стоимость заноса', default=0)
    price_assembly = models.IntegerField(u'Стоимость сборки', default=0)
    is_active = models.BooleanField(u'Активно', default=True)
    objects = models.Manager()
    active = ActiveDeliveryManager()

    @property
    def price_per_lifter(self):
        if self.price is not None and self.lifter.count() > 0:
            return self.price / self.lifter.count()
        else:
            return 0

    @property
    def count_lifters(self):
        return self.lifter.count()

    class Meta:
        ordering = ['date']
        verbose_name = u'Доставка'
        verbose_name_plural = u'Доставки'

    def __unicode__(self):
        return u'Доставка № {}'.format(self.delivery_num)

    def validate_unique(self, exclude=None):
        if self.date and Delivery.objects.filter(delivery_num=self.delivery_num, date__year=self.date.year).exclude(
                id=self.pk).exists():
            raise ValidationError(u'Доставка с таким номером уже существует.')

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(Delivery, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('delivery_detail', args=(self.id,))


def pre_delete_delivery_receiver(sender, instance, *args, **kwargs):
    qs = OrderItem.objects.filter(delivery=instance)
    for orderitem in qs:
        orderitem.delivery = None
        orderitem.save()


pre_delete.connect(pre_delete_delivery_receiver, sender=Delivery)


##################################

################### Товары ####################

class Product(models.Model):
    name = models.TextField(u'Название товара', unique=True)
    slug = models.SlugField(max_length=255, unique=True,
                            help_text='Unique value for product page URL, created from name.')
    min_price = models.IntegerField(u'Мин. цена', blank=True, null=True)
    max_price = models.IntegerField(u'Макс. цена', blank=True, null=True)
    description = models.TextField(u'Описание', blank=True, null=True)
    created_at = models.DateTimeField(u'Создан', auto_now_add=True)
    updated_at = models.DateTimeField(u'Изменен', auto_now=True)

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
        new_slug = slugify(instance.name)
        if Product.objects.filter(slug=new_slug).exclude(id=instance.id).exists():
            raise ValidationError(u'Вообще-то такой товар уже существует.')
        instance.slug = new_slug


pre_save.connect(pre_save_product_receiver, sender=Product)


####################################################

################## Заказы ##################
class Order(models.Model):
    created = models.DateTimeField(u'Создан', auto_now_add=True)
    last_updated = models.DateTimeField(u'Изменен', auto_now=True)
    # Продажа
    order_num = models.CharField(u'Номер договора', max_length=250, help_text=u'Примеры: 90, 90/1, ДК90, ДК/ТЧ90')
    saler = models.ForeignKey(settings.AUTH_USER_MODEL,
                              verbose_name=u'Менеджер', null=True,
                              related_name='saler')
    saler2 = models.ForeignKey(settings.AUTH_USER_MODEL,
                               verbose_name=u'Второй менеджер', null=True,
                               blank=True,
                               related_name='saler2',
                               help_text=u'Указывать только если договор делится на двух менеджеров')
    sale_date = models.DateField(u'Дата продажи', null=True)
    customer_name = models.CharField(u'ФИО покупателя', max_length=150, blank=True, null=True)
    customer_addres = models.TextField(u'Адрес доставки', blank=True, null=True)
    customer_phone = models.CharField(u'Номер телефона', max_length=250, blank=True, null=True)
    # Услуги и скидки
    delivery_money = models.IntegerField(u'Стоимость доставки', default=0)
    delivery_discount = models.BooleanField(u'Скидка на доставку', default=False)
    lifting_money = models.IntegerField(u'Стоимость заноса', default=0)
    lifting_discount = models.BooleanField(u'Скидка на занос', default=False)
    assembly_money = models.IntegerField(u'Стоимость сборки', default=0)
    assembly_discount = models.BooleanField(u'Скидка на сборку', default=False)
    # Оплата
    kredit = models.BooleanField(u'Кредит', default=False)
    full_money_date = models.DateField(u'Дата получения всей суммы', blank=True, null=True)
    # Администратор
    admin_check = models.BooleanField(u'Проверено админом', default=False)
    admin_who_checked = models.ForeignKey(settings.AUTH_USER_MODEL,
                                          verbose_name=u'Проверивший админ',
                                          null=True, blank=True,
                                          related_name='admin')
    is_active = models.BooleanField(u'Активно', default=True)

    class Meta:
        ordering = ['sale_date']
        verbose_name = u'Договор'
        verbose_name_plural = u'Договоры'

    def __unicode__(self):
        return u'Договор № {}'.format(self.order_num)

    @property
    def quantity(self):
        order_items = OrderItem.objects.filter(order=self)
        return len(order_items)

    @property
    def total_subtotal(self):
        ''' Total with only product discounts '''
        total_subtotal = 0
        order_items = OrderItem.objects.filter(order=self)
        for item in order_items:
            total_subtotal += item.total_with_discount
        return total_subtotal

    @property
    def total(self):
        ''' Total with all discounts '''
        total = 0
        order_items = OrderItem.objects.filter(order=self)
        for item in order_items:
            total += item.total_with_discount
        if self.delivery_discount:
            total = total - self.delivery_money
        if self.lifting_discount:
            total = total - self.lifting_money
        if self.assembly_discount:
            total = total - self.assembly_money
        return total

    @property
    def total_per_saler(self):
        ''' Total per saler with all discounts '''
        if self.saler2:
            tps = int(self.total / 2)
        else:
            tps = self.total
        return tps

    @property
    def total_advance_money(self):
        total = 0
        amoney = AdvanceMoney.objects.filter(order=self)
        for item in amoney:
            total += item.advance_money
        return total

    @property
    def fulfilled(self):
        not_delivered_items = OrderItem.notdelivered_items.filter(order=self)
        if not not_delivered_items and self.full_money_date:
            return True
        else:
            return False

    @property
    def delivered(self):
        not_delivered_items = OrderItem.notdelivered_items.filter(order=self)
        if not not_delivered_items:
            return True
        else:
            return False

    def get_absolute_url(self):
        return reverse('order_detail', args=(self.id,))

    def validate_unique(self, exclude=None):
        if self.sale_date and Order.objects.filter(order_num=self.order_num,
                                                   sale_date__year=self.sale_date.year).exclude(
                id=self.pk).exists():
            raise ValidationError(u'Договор с таким номером уже существует.')

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(Order, self).save(*args, **kwargs)


################################################


################## Позиция договора ###################
from django.db.models import Q


class DeliveredOrderItemManager(models.Manager):
    def get_queryset(self):
        return super(DeliveredOrderItemManager, self).get_queryset().filter(delivery__isnull=False)


class NotDeliveredOrderItemManager(models.Manager):
    def get_queryset(self):
        return super(NotDeliveredOrderItemManager, self).get_queryset().filter(delivery__isnull=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name=u'Договор')
    product = models.ForeignKey(Product, verbose_name=u'Товар')
    quantity = models.IntegerField(u'Количество', default=1)
    price = models.IntegerField(u'Цена товара')
    discount = models.IntegerField(u'Скидка с товара', default=0)
    present = models.BooleanField(u'Наличие', default=False)
    # Заказ у поставщика
    supplier_invoice_date = models.DateField(u'Дата заказа у поставщика',
                                             blank=True, null=True)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL,
                              verbose_name=u'Администратор',
                              related_name='admin_user',
                              null=True, blank=True)
    supplier_delivered_date = models.DateField(u'Дата получения от поставщика',
                                               blank=True, null=True)
    # Отгрузка
    delivery = models.ForeignKey(Delivery, verbose_name=u'Доставка',
                                 blank=True, null=True)

    is_active = models.BooleanField(u'Активно', default=True)
    objects = models.Manager()
    delivered_items = DeliveredOrderItemManager()
    notdelivered_items = NotDeliveredOrderItemManager()

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


################ Предоплата #################
class AdvanceMoney(models.Model):
    created = models.DateTimeField(u'Создан', auto_now_add=True)
    last_updated = models.DateTimeField(u'Изменен', auto_now=True)
    order = models.ForeignKey(Order, verbose_name=u'Договор')
    date = models.DateField(u'Дата получения предоплаты', null=True)
    advance_money = models.IntegerField(u'Сумма предоплаты')
    is_active = models.BooleanField(u'Активно', default=True)

    class Meta:
        ordering = ['date']
        verbose_name = u'Предоплата'
        verbose_name_plural = u'Предоплата'

    def __unicode__(self):
        return u'Предоплата #{}'.format(self.id)

##################################
