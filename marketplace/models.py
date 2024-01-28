from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Student(models.Model):
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.EmailField(max_length = 50, unique = True)
    bio = models.TextField(blank = True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'



class Review(models.Model):
    product = models.ForeignKey('products.Product', on_delete = models.CASCADE, related_name = 'reviews')
    reviewer = models.ForeignKey(User, on_delete = models.CASCADE)
    rating = models.PositiveIntegerField(validators = [MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank = True)
    timestamp = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'Review for {self.product.title} by {self.reviewer.username}'

    class Meta:
        unique_together = (('product', 'reviewer'),)
        index_together = (('product', 'reviewer'),)