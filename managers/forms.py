# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model

from .models import Product, Order, OrderItem, Delivery, AdvanceMoney
from Feniks_CMS import settings

User = get_user_model()


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description']
        widgets = {
            'name': forms.Textarea(attrs={'rows': 2}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_num', 'sale_date', 'customer_name', 'customer_addres', 'customer_phone', 'kredit', 'full_money_date']
        widgets = {
            'sale_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'full_money_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'customer_addres': forms.Textarea(attrs={'rows': 3}),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', 'discount', 'present', 'supplier_invoice_date', 'admin',
                  'supplier_delivered_date', 'delivery']
        widgets = {
            'supplier_invoice_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'supplier_delivered_date': forms.DateInput(attrs={'class': 'datepicker'}),
            # 'customer_addres': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        self.fields['admin'].queryset = User.objects.filter(role_admin=True)

    def clean(self):
        cleaned_data = super(OrderItemForm, self).clean()
        if cleaned_data.get('supplier_invoice_date') and not cleaned_data.get('admin'):
            raise forms.ValidationError(u"Укажите администратора, который сделал заказ у поставщика.")
        if cleaned_data.get('admin') and not cleaned_data.get('supplier_invoice_date'):
            raise forms.ValidationError(u"Укажите дату, когда был сделан заказ у поставщика.")
        return cleaned_data


class AdvanceMoneyForm(forms.ModelForm):
    order_num = forms.IntegerField(label=u'Номер договора', required=False)

    class Meta:
        model = AdvanceMoney
        fields = ['order_num', 'date', 'advance_money']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'datepicker'}),
        }


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['delivery_num', 'date', 'selfdrive', 'driver', 'lifter', 'addres', 'zone', 'stores', 'assembly']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'datepicker'}),
            'lifter': forms.CheckboxSelectMultiple(),
            'addres': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(DeliveryForm, self).__init__(*args, **kwargs)
        self.fields['driver'].queryset = User.objects.filter(role_driver=True)
        self.fields['lifter'].queryset = User.objects.filter(role_lifter=True)

        # def clean(self):
        #     cleaned_data = super(OrderForm, self).clean()
        #     advance_money = cleaned_data.get('advance_money')
        #     advance_money_date = cleaned_data.get('advance_money_date')
        #
        #     if advance_money and (not advance_money_date):
        #         raise forms.ValidationError(u'Ошибка! Если вы получили задаток, то укажите дату получения.')
        #
        #     if advance_money_date and (not advance_money):
        #         raise forms.ValidationError(u'Ошибка! Если вы получили задаток, то укажите его сумму.')
