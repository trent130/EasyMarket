from django.contrib import admin
from marketplace.models import  Cart, CartItem, Message, Reaction, Review, WishList
from django.contrib.admin.exceptions import NotRegistered

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
    list_display = ['reaction_type', 'user', 'message', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__username', 'message__content']
    ordering = ['-created_at']


class ReactionInline(admin.TabularInline):
    model = Reaction
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

admin.site.register(WishList)
