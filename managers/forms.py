# -*- coding: utf-8 -*-
from django import forms

from .models import Product, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'categories', 'description']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['sale_date', 'advance_money', 'advance_money_date', 'realization_date',]
        widgets = {
            'sale_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'advance_money_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'realization_date': forms.DateInput(attrs={'class': 'datepicker'}),
        }
    def clean(self):
        cleaned_data = super(OrderForm, self).clean()
        advance_money = cleaned_data.get('advance_money')
        advance_money_date = cleaned_data.get('advance_money_date')

        if advance_money and (not advance_money_date):
            raise forms.ValidationError(u'Ошибка! Если вы получили задаток, то укажите дату получения.')

        if advance_money_date and (not advance_money):
            raise forms.ValidationError(u'Ошибка! Если вы получили задаток, то укажите его сумму.')