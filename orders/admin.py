from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'total_amount')
    list_filter = ('status', 'created_at')
    search_fields = ['user__username', 'reference']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'address', 'city', 'postal_code')
    list_filter = ('user', 'city')
    search_fields = ['user__username', 'address']

admin.site.register(Order, OrderAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)