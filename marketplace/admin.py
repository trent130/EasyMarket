from django.contrib import admin
from marketplace.models import  Cart, CartItem, Message, Reaction, Review, WishList
from django.contrib.admin.exceptions import NotRegistered
from django.utils.html import format_html

# Register your models here.

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'reviewer', 'rating', 'timestamp')
    list_filter = ['product', 'reviewer']
    search_fields = ['product', 'reviewer']
    ordering = ['-timestamp']


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'added_at')
    search_fields = ('cart__user__username', 'product__title')
    list_filter = ['added_at']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ['user__username']
    list_filter = ['created_at', 'updated_at']
    inlines = [CartItemInline]


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)


class ReactionAdmin(admin.ModelAdmin):
    list_display = ['reaction_type', 'user', 'message_sent', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__username', 'message__content']
    ordering = ['-created_at']


class ReactionInline(admin.TabularInline):
    model = Reaction
    fk_name = 'message_sent'
    extra = 1


class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'timestamp', 'read')
    search_fields = ['user__username', 'content']
    list_filter = ['user__username', 'timestamp', 'read']
    inlines = [ReactionInline]

admin.site.register(Message, MessageAdmin)
admin.site.register(Reaction, ReactionAdmin)
try:
    admin.site.unregister(Review)
except NotRegistered:
    pass
admin.site.register(Review, ReviewAdmin)

class WishListAdmin(admin.ModelAdmin):
    list_display = ('user_info', 'product_count', 'created_date')
    list_filter = ['created_at', 'user__user_type']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'product_list_display']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'created_at')
        }),
        ('Products in Wishlist', {
            'fields': ('products', 'product_list_display'),
            'description': 'Select products to add to this user\'s wishlist'
        }),
    )

    filter_horizontal = ['products']  # Makes the many-to-many field easier to manage

    def user_info(self, obj):
        """Display user information with username and email"""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.user.username,
            obj.user.email
        )
    user_info.short_description = 'User'
    user_info.admin_order_field = 'user__username'

    def product_count(self, obj):
        """Display the number of products in the wishlist"""
        count = obj.products.count()
        if count == 0:
            return format_html('<span style="color: #999;">0 products</span>')
        elif count <= 5:
            return format_html('<span style="color: #28a745;">{} products</span>', count)
        else:
            return format_html('<span style="color: #007bff;">{} products</span>', count)
    product_count.short_description = 'Products Count'

    def created_date(self, obj):
        """Display formatted creation date"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_date.short_description = 'Created'
    created_date.admin_order_field = 'created_at'

    def product_list_display(self, obj):
        """Display a formatted list of products in the wishlist"""
        products = obj.products.all()
        if not products:
            return format_html('<em style="color: #999;">No products in wishlist</em>')

        product_list = []
        for product in products[:10]:  # Limit to first 10 products for display
            product_list.append(
                format_html(
                    '<span style="background: #f8f9fa; padding: 2px 6px; margin: 2px; '
                    'border-radius: 3px; display: inline-block;">{}</span>',
                    product.title
                )
            )

        result = format_html('{}', format_html('<br>').join(product_list))

        if products.count() > 10:
            result += format_html(
                '<br><em style="color: #666;">... and {} more products</em>',
                products.count() - 10
            )

        return result
    product_list_display.short_description = 'Products in Wishlist'

    def get_queryset(self, request):
        """Optimize queryset to reduce database queries"""
        return super().get_queryset(request).select_related('user').prefetch_related('products')


admin.site.register(WishList, WishListAdmin)
