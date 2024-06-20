from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser,Permission
from products.models import Product

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        if not Student.objects.filter(email=instance.email).exists():
            Student.objects.create(user=instance, email=instance.email)
        else:
            print(f"Student with email {instance.email} already exists.")
           
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.EmailField(max_length = 50, unique = True)
    bio = models.TextField(blank = True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')

    def __str__(self):
        return f'{self.user.username}'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    reactions = models.ManyToManyField('Reaction', blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.timestamp}'

class Reaction(models.Model):
    emoji = models.CharField(max_length=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.emoji} by {self.user.username}'

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

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through='CartItem')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def total_items(self):
        return sum(item.quantity for item in self.cartitem_set.all())

    def total_price(self):
        return sum(item.total_price() for item in self.cartitem_set.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.title} in cart"

    def total_price(self):
        return self.product.price * self.quantity

class CustomUser(AbstractUser):
    is_basic = models.BooleanField(default=True)
    is_legacy = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_students = models.BooleanField(default=False)
    
    class Meta:
        # Define a unique related_name for the groups relationship
        db_table = 'custom_user'

    # Define a unique related_name for the user_permissions relationship
    groups = models.ManyToManyField(Group, related_name='custom_users')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_users')

class WishList(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    auto_now = models.DateTimeField(auto_now_add=True)
    