from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        # 'transaction_id', 
        'user_info', 
        'amount', 
        'status_badge',
        # 'payment_method', 
        'timestamp'
    ]
    
    list_filter = ['status', 'timestamp']  # Removed payment_method from list_filter
    
    search_fields = [
        'transaction_id', 
        'user__email', 
        'user__username',
        'phone_number',
        'account_reference'
    ]
    
    readonly_fields = [
        'user_details',
        'payment_details'
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
                'user_details',
                'phone_number',
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_details',
                'account_reference',
                'transaction_desc',
                'failure_reason'
            )
        }),
    )

    def user_info(self, obj):
        """Display user information with link."""
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}">{}</a><br><small>{}</small>',
            url,
            obj.user.get_full_name() or obj.user.username,
            obj.user.email
        )
    user_info.short_description = 'User'

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'pending': 'warning',
            'completed': 'success',
            'failed': 'danger'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def user_details(self, obj):
        """Display detailed user information."""
        return format_html(
            """
            <div class="user-details">
                <p><strong>Name:</strong> {}</p>
                <p><strong>Email:</strong> {}</p>
                <p><strong>Phone:</strong> {}</p>
                <p><strong>Member Since:</strong> {}</p>
            </div>
            """,
            obj.user.get_full_name(),
            obj.user.email,
            obj.phone_number,
            obj.user.date_joined.strftime('%B %d, %Y')
        )
    user_details.short_description = 'User Details'

    def payment_details(self, obj):
        """Display detailed payment information."""
        return format_html(
            """
            <div class="payment-details">
                <p><strong>Amount:</strong> Ksh {}</p>
                <p><strong>Method:</strong> {}</p>
                <p><strong>Reference:</strong> {}</p>
                <p><strong>Status:</strong> {}</p>
                {}
            </div>
            """,
            obj.amount,
            obj.get_payment_method_display(),
            obj.account_reference,
            obj.get_status_display(),
            f"<p><strong>Failure Reason:</strong> {obj.failure_reason}</p>" if obj.failure_reason else ""
        )
    payment_details.short_description = 'Payment Details'

    class Media:
        css = {
            'all': ('css/admin/transaction.css',)
        }