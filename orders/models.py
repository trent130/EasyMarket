from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Order(models.Model):
    product = models.ForeignKey('products.Product', on_delete = models.CASCADE, related_name = 'orders')
    buyer = models.ForeignKey(User, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits = 5, decimal_places = 2)
    timestamp = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'order #{self.id}- {self.product.title}'
