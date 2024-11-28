from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    PAYMENT_METHODS = [
        ('MPESA', 'M-Pesa'),
        ('CASH', 'Cash on Delivery'),
    ]
    # Add missing fields that caused the errors
    transaction_id = models.CharField(max_length=100, unique=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHODS,
        default='mpesa'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01')), 
            MaxValueValidator(Decimal('999999.99'))
        ]
    )
    phone_number = models.CharField(max_length=15)
    reference = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=100)
    checkout_request_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)  # Renamed from created_at
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.reference} - {self.amount}"
