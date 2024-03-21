from django.contrib import admin
from marketplace.models import Student
from products.models import Product, Category, Image
from orders.models import Order

# Register your models here.
admin.site.register(Student)
admin.site.register(Product)
admin.site.register(Image)
admin.site.register(Order)
admin.site.register(Category)
