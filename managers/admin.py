from django.contrib import admin

from .models import Category, Product, Order, OrderItem, Delivery, AdvanceMoney


# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'sale_date', 'saler', 'full_money_date',)
    inlines = [
        OrderItemInline,
    ]
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'order', 'present', 'delivery',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Delivery)
admin.site.register(AdvanceMoney)
