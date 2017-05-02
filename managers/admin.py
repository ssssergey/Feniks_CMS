from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from .models import Product, Order, OrderItem, Delivery, AdvanceMoney


# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'sale_date', 'saler', 'full_money_date',)
    inlines = [
        OrderItemInline,
    ]
    search_fields = ['order_num', 'customer_addres', 'customer_name']
    list_filter = (
        'saler',
        ('sale_date', DateFieldListFilter),
    )


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('__unicode__', 'slug')


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'order', 'present', 'delivery',)


class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'date', 'addres', 'lifters', 'driver', 'created', 'last_updated')
    search_fields = ['delivery_num', 'addres']
    list_filter = (
        'lifter',
        'driver',
        ('date', DateFieldListFilter),
    )

    def lifters(self, instance):
        return ", ".join([p.last_name for p in instance.lifter.all()])


class AdvanceMoneyAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'date', 'order')
    list_filter = (
        ('date', DateFieldListFilter),
    )


admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(AdvanceMoney, AdvanceMoneyAdmin)
