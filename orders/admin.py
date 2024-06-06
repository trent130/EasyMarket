from django.contrib import admin
from .models import Order
from django.contrib.admin.exceptions import NotRegistered

# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'status', 'timestamp', 'quantity', 'total_price', 'product')
    list_filter = ('buyer', 'status', 'timestamp')
    search_fields = ['user__username', 'product__title']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
try:
    admin.site.unregister(Order)
except NotRegistered:
    pass
admin.site.register(Order, OrderAdmin)

