from django.db import models
from django.contrib.auth.models import User




class Transaction(models.Model):
    STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ]
    slug = models.SlugField(max_length=50, unique=True, default='')
    phone_number = models.CharField(max_length=20, default = '')
    account_reference = models.CharField(max_length=50, blank=True)
    transaction_desc = models.CharField(max_length=255, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Transaction #{self.pk} - {self.user.username}"

