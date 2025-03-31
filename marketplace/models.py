from django.db import models
# from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, Permission
from products.models import Product


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
