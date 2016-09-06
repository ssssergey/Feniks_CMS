# -*- coding: utf-8 -*-
import locale

from django import template

register = template.Library()


@register.filter(name=u'currency')
def currency(value):
    try:
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    except:
        locale.setlocale(locale.LC_ALL, '')
    loc = locale.localeconv()
    return locale.currency(value, loc['currency_symbol'], grouping=False)


@register.filter
def month_name(month_number):
    calendar = {
        1: u'Январь',
        2: u'Февраль',
        3: u'Март',
        4: u'Апрель',
        5: u'Май',
        6: u'Июнь',
        7: u'Июль',
        8: u'Август',
        9: u'Сентябрь',
        10: u'Октябрь',
        11: u'Ноябрь',
        12: u'Декабрь',
    }
    return calendar[month_number]
