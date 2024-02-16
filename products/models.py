from django.db import models
from django.contrib.auth.models import User
from marketplace.models import Student  

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, unique = True)
    description = models.TextField(blank = True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length = 100)
    description = models.TextField()
    price = models.DecimalField(max_digits = 5, decimal_places = 2)
    student = models.ForeignKey(Student, on_delete = models.CASCADE, related_name = 'products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name = 'products')
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return self.title

class Image(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name = "images")
    image = models.ImageField(upload_to = 'product_images/')
    description = models.TextField(blank =True)

    def __str__(self):
        return f'image for {self.product.title}'