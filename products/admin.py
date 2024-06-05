from django.contrib import admin
from django.contrib.admin.exceptions import NotRegistered
from .models import Product, Category, Image
from orders.models import Order
from marketplace.models import Student
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.models import Group
from marketplace.models import Review

class ImageInline(admin.TabularInline):
    model = Image
    extra = 3

class ProductAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    list_display = ('title', 'price', 'student', 'stock')
    list_filter = ['student']
    search_fields = ['title', 'description']

class ProductInline(admin.TabularInline):
    model = Product
    extra = 3

class CategoryAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
    list_display = ('name', 'description')
    search_fields = ['name']

class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ['first_name', 'last_name', 'email']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'reviewer', 'rating', 'timestamp')
    list_filter = ['product', 'reviewer']
    search_fields = ['product', 'reviewer']

try:
    admin.site.unregister(Product)
except NotRegistered:
    pass
admin.site.register(Product, ProductAdmin)

try:
    admin.site.unregister(Category)
except NotRegistered:
    pass
admin.site.register(Category, CategoryAdmin)

try:
    admin.site.unregister(Student)
except NotRegistered:
    pass
admin.site.register(Student, StudentAdmin)

try:
    admin.site.unregister(Review)
except NotRegistered:
    pass
admin.site.register(Review, ReviewAdmin)

try:
    admin.site.unregister(Order)
except NotRegistered:
    pass
admin.site.register(Order)

try:
    admin.site.unregister(Image)
except NotRegistered:
    pass
admin.site.register(Image)