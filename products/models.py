from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 
from django.utils.text import slugify
from django.apps import apps
# import requests


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(null=True, default='category/default.jpg', upload_to='category_images/')

    def __str__(self):
        return self.name

def default_category():
    category, created = Category.objects.get_or_create(name='Default')
    return category.id

class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    student = models.ForeignKey('marketplace.Student', on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey('products.Category', on_delete=models.CASCADE, default=default_category, related_name='products')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to = 'product_images/', blank = True)
    slug = models.SlugField(max_length=200, unique=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.title
    
    def is_in_stock(self):
        return self.stock > 0
    
    def __image_for__(self):
        return f'image for {self.product.title}'

