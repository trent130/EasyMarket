from django.db import models
# from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, Permission
from products.models import Product
# import string
# import random


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        """
        Returns a string representation of the student, which is
        the combination of their first and last names.

        Returns:
            str: The string representation of the student.
        """
        return f'{self.first_name} {self.last_name}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')

    def __str__(self):
        """
        Returns a string representation of the user profile, which is
        the username of the associated user.

        Returns:
            str: The string representation of the user profile.
        """
        return f'{self.user.username}'  # pylint: disable=no-member


@receiver(post_save, sender=User)
def create_user_related_profiles(sender, instance, created, **kwargs):
    
    """
    Signal receiver that creates user-related profiles upon User creation.

    This function is triggered when a User instance is saved. If a new User 
    is created, it automatically creates a UserProfile associated with that 
    User. Additionally, it attempts to create a Student profile only if the 
    email does not already exist in the Student model. If the email already 
    exists, it logs a message indicating that a Student with that email 
    already exists. For existing Users, it ensures that the UserProfile is 
    saved if it exists.
    """
    if created:
        # Create UserProfile
        UserProfile.objects.create(user=instance)

        # Create Student profile only if email doesn't exist
        if not Student.objects.filter(email=instance.email).exists():
            Student.objects.create(user=instance, email=instance.email)
        else:
            print(f"Student with email {instance.email} already exists.")
    else:
        # Ensure UserProfile exists and save it
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        """
        Returns a string representation of the message, which is
        the combination of the associated user's username and the
        timestamp of the message.

        Returns:
            str: The string representation of the message.
        """
        return f'{self.user.username} - {self.timestamp}'


class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('haha', 'Haha'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry')
    ]
    
    reaction_type = models.CharField(
        max_length=10, choices=REACTION_CHOICES)
    message = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='reactions', null=True, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the reaction, which includes
        the type of reaction and the username of the user who made it.

        Returns:
            str: The string representation of the reaction.
        """
        return f'{self.reaction_type} by {self.user.username}'


class Review(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the review, which includes
        the title of the product being reviewed and the username of the
        user who wrote the review.

        Returns:
            str: The string representation of the review.
        """
        return f'Review for {self.product.title} by {self.reviewer.username}'

    class Meta:
        unique_together = (('product', 'reviewer'),)
    #    index_together = (('product', 'reviewer'),)

# def unique_slug_field_cart():
#     length =10
#     characters = string.ascii_lowercase + string.digits

#     while slug:
#         if Cart.objects.filter(slug == slug).exists():
#             pass
#         slug = ''.join(random.choices(characters), k=length)   
#     return slug


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through='CartItem')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField()

    def __str__(self):
        """
        Returns a string representation of the cart, which is
        the username of the associated user.

        Returns:
            str: The string representation of the cart.
        """
    
        return f"Cart for {self.user.username}"

    def total_items(self):
        """
        Returns the total number of items in the cart.

        """
        return sum(item.quantity for item in self.cartitem_set.all())

    def total_price(self):
        """
        Returns the total price of all items in the cart.

        Returns:
            float: The total price of all items in the cart.
        """
        return sum(item.total_price() for item in self.cartitem_set.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """
        Returns a string representation of the cart item, which includes
        the quantity and title of the product in the cart.

        Returns:
            str: The string representation of the cart item.
        """
        return f"{self.quantity} x {self.product.title} in cart"

    def total_price(self):
        """
        Returns the total price of the cart item, which is the product price times the quantity.

        Returns:
            float: The total price of the cart item.
        """
        return self.product.price * self.quantity


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('basic', 'Basic'),
        ('legacy', 'Legacy'),
        ('admin', 'Admin'),
        ('premium', 'Premium'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='basic')
        
    # Define a unique related_name for the user_permissions relationship
    groups = models.ManyToManyField(Group, related_name='custom_users')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_users')

    class Meta:
        db_table = 'custom_user'


class WishList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name="wishlists")
    auto_now = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the wishlist, which is the username of the associated user concatenated with
        the string wishlist".
        
        Returns:
            str: The string representation of the wishlist.
        """
        return f"{self.user.username}'s wishlist"