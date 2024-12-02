from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 
        'user_info', 
        'amount', 
        'status_badge',
        'timestamp'
    ]
    
    list_filter = ['status', 'timestamp']
    
    search_fields = [
        'transaction_id', 
        'user__email', 
        'user__username',
        'phone_number',
        'reference'
    ]
    
    readonly_fields = [
        'user_details',
        'payment_details',
        'timestamp',
        'updated_at'
    ]
    
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'transaction_id',
                'merchant_request_id',
                'timestamp',
                'status',
                'amount',
                'payment_method'
            )
        }),
        ('User Information', {
            'fields': (
                'user',
                'phone_number',
            )
        }),
        ('Payment Details', {
            'fields': (
                'reference',
                'description',
                'checkout_request_id',
                'updated_at'
            )
        })
    )

    def user_info(self, obj):
        return f"{obj.user.username} ({obj.user.email})"
    user_info.short_description = "User"

    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'completed': '#28a745',
            'failed': '#dc3545'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status.lower(), '#000'),
            obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def user_details(self, obj):
        return format_html(
            "<strong>Username:</strong> {}<br>"
            "<strong>Email:</strong> {}<br>"
            "<strong>Phone:</strong> {}",
            obj.user.username,
            obj.user.email,
            obj.phone_number
        )
    user_details.short_description = "User Details"

    def payment_details(self, obj):
        return format_html(
            "<strong>Method:</strong> {}<br>"
            "<strong>Reference:</strong> {}<br>"
            "<strong>Amount:</strong> {}",
            obj.get_payment_method_display(),
            obj.reference,
            obj.amount
        )
    payment_details.short_description = "Payment Details"