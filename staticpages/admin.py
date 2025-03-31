from django.contrib import admin
from .models import StaticPage, Footer, Testimonial, ContactMessage, FAQ, Footer

# Register your models here.
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'email',
        'message',
        # 'created_at',
    ]
    list_filter = ['name', 'email']
    search_fields = [
        'name',
        'email',
    ]
    readonly_fields = [
        'created_at',
    ]

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = [
        'question',
        'answer',
        'created_at',
        'updated_at',
        'is_published'
    ]
    list_filter = ['created_at', 'is_published']
    search_fields = [
        'question',
        'answer',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'is_published'
    ]

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = [
        'author',
        'content',
        'created_at',
        'is_featured',
    ]
    list_filter = ['created_at', 'author', 'is_featured']
    search_fields = [
        'author',
        'created_at',
    ]
    readonly_fields = [
        'created_at',
        'is_featured'
    ]

@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'content',
        'created_at',
        'is_published',
        'slug',
        'updated_at'
    ]
    list_filter = ['created_at', 'title', 'is_published']
    search_fields = [
        'title',
        'created_at',
    ]
    readonly_fields = [
        'created_at',
        'is_published',
        'updated_at'
    ]

# @admin.register(Footer)
# class FooterAdmin(admin.ModelAdmin):
#     list_display = [
#         'title',
#         'content',
#         'created_at',
#         'is_published',
#         'slug',
#         'updated_at'
#     ]
#     list_filter = ['created_at', 'title', 'is_published']
#     search_fields = [
#         'title',
#         'created_at',
#     ]
#     readonly_fields = [
#         'created_at',
#         'is_published',
#         'updated_at'
#     ]