from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models import F
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def validate_image_size(value):
    """Validate image size (max 5MB)"""
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("Maximum file size is 5MB")

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='category_images/',
        null=True,
        default='category/default.jpg',
        validators=[validate_image_size]
    )
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def active_products_count(self):
        return self.products.filter(is_active=True).count()

def default_category():
    """Get or create default category"""
    category, created = Category.objects.get_or_create(
        name='Uncategorized',
        defaults={'description': 'Default category for uncategorized products'}
    )
    return category.id

class ProductVariant(models.Model):
    """Model for product variants (e.g., different sizes, colors)"""
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    price_adjustment = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        help_text="Price adjustment relative to base product price"
    )
    stock = models.PositiveIntegerField(default=0)
    reserved_stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.sku}"

    class Meta:
        ordering = ['name']

class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
    ]

    title = models.CharField(max_length=100)
    variants = models.ManyToManyField(
        ProductVariant,
        related_name='products',
        blank=True
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('999999.99'))]
    )
    student = models.ForeignKey(
        'marketplace.Student',
        on_delete=models.CASCADE,
        related_name='products'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_DEFAULT,
        default=default_category,
        related_name='products'
    )
    condition = models.CharField(
        max_length=10,
        choices=CONDITION_CHOICES,
        default='new'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(
        upload_to='product_images/',
        blank=True,
        validators=[validate_image_size]
    )
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    stock = models.PositiveIntegerField(default=1)
    reserved_stock = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)
    last_stock_update = models.DateTimeField(auto_now=True)
    
    # Statistics fields
    total_sales = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    last_sale_date = models.DateTimeField(null=True, blank=True)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    review_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
            models.Index(fields=['price']),
            models.Index(fields=['stock']),
        ]

    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug

        # Validate stock levels
        if self.reserved_stock > self.stock:
            raise ValidationError("Reserved stock cannot exceed total stock")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def available_stock(self):
        """Get available stock (total - reserved)"""
        return max(0, self.stock - self.reserved_stock)

    def is_in_stock(self):
        """Check if product is in stock"""
        return self.available_stock > 0

    def reserve_stock(self, quantity=1):
        """Reserve product stock"""
        if quantity > self.available_stock:
            raise ValidationError("Not enough stock available")
        
        success = Product.objects.filter(
            id=self.id,
            stock__gte=F('reserved_stock') + quantity
        ).update(
            reserved_stock=F('reserved_stock') + quantity,
            last_stock_update=timezone.now()
        )
        
        if success:
            self.refresh_from_db()
            logger.info(f"Reserved {quantity} units of product {self.id}")
            return True
        return False

    def release_stock(self, quantity=1):
        """Release reserved stock"""
        if quantity > self.reserved_stock:
            raise ValidationError("Cannot release more stock than reserved")
        
        success = Product.objects.filter(
            id=self.id,
            reserved_stock__gte=quantity
        ).update(
            reserved_stock=F('reserved_stock') - quantity,
            last_stock_update=timezone.now()
        )
        
        if success:
            self.refresh_from_db()
            logger.info(f"Released {quantity} units of product {self.id}")
            return True
        return False

    def update_stock(self, quantity):
        """Update total stock with validation"""
        if quantity < self.reserved_stock:
            raise ValidationError("New stock level cannot be less than reserved stock")
        
        self.stock = quantity
        self.last_stock_update = timezone.now()
        self.save()
        logger.info(f"Updated stock to {quantity} for product {self.id}")

    def increment_views(self):
        """Increment product view count"""
        Product.objects.filter(id=self.id).update(
            views_count=F('views_count') + 1
        )

    @property
    def average_rating(self):
        """Get average product rating"""
        return self.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0

    @property
    def review_count(self):
        """Get total number of reviews"""
        return self.reviews.count()

    def clean(self):
        """Additional model validation"""
        if self.price <= 0:
            raise ValidationError({'price': 'Price must be greater than zero'})
        if self.stock < 0:
            raise ValidationError({'stock': 'Stock cannot be negative'})
        if self.reserved_stock > self.stock:
            raise ValidationError({'reserved_stock': 'Reserved stock cannot exceed total stock'})
