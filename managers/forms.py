# -*- coding: utf-8 -*-
import re

from django import forms
from django.contrib.auth import get_user_model

from .models import Product, Order, OrderItem, Delivery, AdvanceMoney
from Feniks_CMS import settings

User = get_user_model()


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name']
        widgets = {
            'name': forms.Textarea(attrs={'rows': 2}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_num',
                  'sale_date',
                  'saler2',
                  'customer_name', 'customer_addres', 'customer_phone',
                  'delivery_money', 'delivery_discount',
                  'lifting_money', 'lifting_discount',
                  'assembly_money', 'assembly_discount',
                  'kredit',
                  'full_money_date']
        widgets = {
            'sale_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'full_money_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'customer_addres': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['saler2'].queryset = User.objects.filter(role_saler=True)

    def clean(self):
        cleaned_data = super(OrderForm, self).clean()

        if cleaned_data.get('kredit') and not cleaned_data.get('full_money_date'):
            raise forms.ValidationError(
                u"Кредит подразумевает, что оплачено полностью. Укажите дату полной оплаты.")

        order_num = cleaned_data.get('order_num')
        if not order_num:
            raise forms.ValidationError(u"Заполните номер договора.")
        if ' ' in order_num:
            raise forms.ValidationError(u"Не должно быть пустых ПРОБЕЛОВ в номере договора.")
        if any(c.isalpha() for c in order_num) and not order_num.isupper():
            raise forms.ValidationError(u"Все буквы должны быть ЗАГЛАВНЫМИ в номере договора.")

        return cleaned_data


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product',
                  'quantity',
                  'price',
                  'discount',
                  'present',
                  'supplier_invoice_date',
                  'admin',
                  'supplier_delivered_date']
        widgets = {
            'supplier_invoice_date': forms.DateInput(
                attrs={'class': 'datepicker'}),
            'supplier_delivered_date': forms.DateInput(
                attrs={'class': 'datepicker'}),
            # 'customer_addres': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        self.fields['admin'].queryset = User.objects.filter(role_admin=True)

    def clean(self):
        cleaned_data = super(OrderItemForm, self).clean()
        if cleaned_data.get('supplier_invoice_date') and not cleaned_data.get(
                'admin'):
            raise forms.ValidationError(
                u"Укажите администратора, который сделал заказ у поставщика.")
        if cleaned_data.get('admin') and not cleaned_data.get(
                'supplier_invoice_date'):
            raise forms.ValidationError(
                u"Укажите дату, когда был сделан заказ у поставщика.")
        return cleaned_data


class AdvanceMoneyForm(forms.ModelForm):
    order_num = forms.CharField(label=u'Номер договора', max_length=30,
                                required=False)

    class Meta:
        model = AdvanceMoney
        fields = ['order_num', 'date', 'advance_money']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'datepicker'}),
        }


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['delivery_num',
                  'date',
                  'selfdrive',
                  'driver',
                  'lifter',
                  'addres',
                  'price_delivery',
                  'price',
                  'price_assembly']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'datepicker'}),
            'lifter': forms.CheckboxSelectMultiple(),
            'addres': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(DeliveryForm, self).__init__(*args, **kwargs)
        self.fields['driver'].queryset = User.objects.filter(role_driver=True)
        self.fields['lifter'].queryset = User.objects.filter(role_lifter=True)
        self.fields['delivery_num'].initial = '(2017)'

    def clean(self):
        cleaned_data = super(DeliveryForm, self).clean()

        if not cleaned_data.get('date'):
            raise forms.ValidationError(u"Заполните дату.")

        delivery_num = cleaned_data.get('delivery_num')
        if not delivery_num:
            raise forms.ValidationError(u"Заполните номер доставки.")

        p = re.compile(r'[0-9]+\(20[0-9]+\)')
        if not re.search(p, delivery_num):
            raise forms.ValidationError(u"Неправильный формат Номера доставки. Образцы: 85(2017), 90(2017)")

        return cleaned_data