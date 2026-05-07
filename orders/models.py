from decimal import Decimal
from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = (
        ('processing', 'PROCESSING'),
        ('shipped', 'SHIPPED'),
        ('delivered', 'DELIVERED'),
        ('canceled', 'CANCELED'),
        ('refunded', 'REFUNDED'),
        ('returned', 'RETURNED'),
        ('pending', 'PENDING'),
    )
    PAYMENT_CHOICES = [
        ('MPESA', 'M-Pesa'),
        ('CASH', 'Cash on Delivery'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    reference = models.CharField(max_length=20, unique=True)
    shipping_address = models.ForeignKey('orders.ShippingAddress', on_delete=models.PROTECT, null=True)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('999999.99'))
        ]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    payment_status = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order #{self.id} - {self.user.username}'

    @property
    def is_paid(self):
        return self.payment_status

    @property
    def can_request_refund(self):
        return self.status == 'delivered' and self.is_paid

    def send_cancellation_notification(self):
        pass  # Implement email notification

    def send_delivery_confirmation(self):
        pass  # Implement email notification

    def generate_invoice(self):
        return b'PDF content'  # Implement PDF generation

    def create_refund_request(self, reason):
        from .models import Refund
        return Refund.objects.create(order=self, reason=reason)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Shipping addresses'


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
