from rest_framework import serializers
# from django.core.exceptions import ValidationError
# from django.utils.text import slugify
from .models import Product, Category, ProductVariant
from marketplace.models import Review
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from users.models import Student
from django.db.models import Avg
from django.db.models import Count


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source='active_products_count', read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description',
            'image', 'product_count', 'is_active'
        ]
        read_only_fields = ['slug']


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'rating', 'comment', 'reviewer_name',
            'timestamp'
        ]


class ProductVariantSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    available_stock = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'name', 'sku', 'price_adjustment',
            'stock', 'reserved_stock', 'is_active',
            'final_price', 'available_stock'
        ]

    def get_final_price(self, obj):
        """
        Return the final price of the product variant, which is the product price + the price adjustment.

        If the product variant is not associated with a product, return the price adjustment only.
        """
        product = obj.products.first()
        if product:
            return float(product.price) + float(obj.price_adjustment)
        return float(obj.price_adjustment)

    def get_available_stock(self, obj):
        """
        Return the available stock of the product variant, which is the total stock minus the reserved stock.

        If the result is negative, return 0.
        """
        return max(0, obj.stock - obj.reserved_stock)


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    student_name = serializers.CharField(source='student.user.username', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    is_wishlisted = serializers.SerializerMethodField()
    available_stock = serializers.IntegerField(read_only=True)
    image_url = serializers.SerializerMethodField()
    has_variants = serializers.BooleanField(source='variants.exists', read_only=True)
    total_sales = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'price', 'category',
            'category_name', 'image_url', 'student', 'student_name',
            'average_rating', 'is_wishlisted', 'available_stock',
            'condition', 'created_at', 'total_sales', 'has_variants',
        ]

    def get_is_wishlisted(self, obj):
        """
        Return True if the product is in the current user's wishlist, False otherwise.

        This method requires the request object to be passed in the serializer context.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                return request.user.wishlist.products.filter(id=obj.id).exists()
            except request.user.wishlist.RelatedObjectDoesNotExist:
                return False
        return False

    def get_image_url(self, obj):
        """
        Return the absolute URL of the product image, if any.

        This method requires the request object to be passed in the serializer context.
        """
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    student = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()
    available_stock = serializers.IntegerField(read_only=True)
    image_url = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(many=True, read_only=True)
    statistics = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'price',
            'category', 'image_url', 'student', 'reviews',
            'is_wishlisted', 'available_stock', 'condition',
            'created_at', 'updated_at', 'related_products',
            'views_count', 'variants', 'statistics',
            'total_sales', 'total_revenue', 'last_sale_date'
        ]

    def get_statistics(self, obj):
        return {
            'total_sales': obj.total_sales,
            'total_revenue': float(obj.total_revenue),
            'last_sale_date': obj.last_sale_date,
            'average_rating': float(obj.average_rating),
            'review_count': obj.review_count,
            'views_count': obj.views_count
        }

    def get_student(self, obj):
        """
        Return a dictionary with the student's id, username, average rating, products count and join date.
        """
        student = obj.student
        average_rating = student.products.aggregate(Avg('reviews__rating'))['reviews__rating__avg'] or 0
        return {
            'id': student.id,
            'username': student.user.username,
            'rating': average_rating,
            'products_count': student.products.count(),
            'joined_date': student.user.date_joined
        }

    def get_reviews(self, obj):
        recent_reviews = obj.reviews.select_related('reviewer').order_by('-timestamp')[:3]
        return {
            'average': obj.average_rating,
            'count': obj.review_count,
            'recent': ReviewSerializer(recent_reviews, many=True).data
        }

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                return request.user.wishlist.products.filter(id=obj.id).exists()
            except request.user.wishlist.RelatedObjectDoesNotExist:
                return False
        return False

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None

    def get_related_products(self, obj):
        related = Product.objects.filter(
            category=obj.category,
            is_active=True
        ).exclude(
            id=obj.id
        ).annotate(
            similarity_score=Count('reviews')
        ).order_by('-created_at')[:4]
        return ProductListSerializer(
            related,
            many=True,
            context=self.context
        ).data


class ProductCreateSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, required=False)
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('999999.99'))
        ]
    )

    class Meta:
        model = Product
        fields = [
            'title', 'description', 'price', 'category',
            'image', 'condition', 'stock', 'variants'
        ]

    def validate_price(self, value):
        """Validate price is reasonable"""
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        min_value = Decimal('0.01')
        max_value = Decimal('999999.99')
        if value < min_value:
            raise serializers.ValidationError(f"Price must be at least {min_value}")
        if value > max_value:
            raise serializers.ValidationError(f"Price cannot exceed {max_value}")
        return value

    def validate_stock(self, value):
        """Validate stock quantity"""
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        if value > 10000:  # Reasonable maximum
            raise serializers.ValidationError("Stock quantity is unreasonably high")
        return value

    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        student = Student.objects.get(user=self.context['request'].user)
        product = Product.objects.create(student=student, **validated_data)

        # Create variants if provided
        for variant_data in variants_data:
            variant = ProductVariant.objects.create(**variant_data)
            product.variants.add(variant)

        return product


class ProductUpdateSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, required=False)
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('999999.99'))
        ]
    )

    class Meta:
        model = Product
        fields = [
            'title', 'description', 'price', 'category',
            'image', 'condition', 'stock', 'is_active',
            'variants'
        ]

    def update(self, instance, validated_data):
        variants_data = validated_data.pop('variants', None)
        product = super().update(instance, validated_data)

        if variants_data is not None:
            # Remove existing variants
            product.variants.clear()
            # Add new variants
            for variant_data in variants_data:
                variant = ProductVariant.objects.create(**variant_data)
                product.variants.add(variant)

        return product

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        if instance and instance.student.user != self.context['request'].user:
            raise serializers.ValidationError(
                "You don't have permission to update this product"
            )

        # Validate stock changes
        if 'stock' in attrs:
            new_stock = attrs['stock']
            if instance and new_stock < instance.reserved_stock:
                raise serializers.ValidationError(
                    "New stock level cannot be less than reserved stock"
                )

        return attrs


class ProductSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True)
    category = serializers.IntegerField(required=False)
    min_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('999999.99'))
        ]
    )
    max_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('999999.99'))
        ]
    )
    condition = serializers.ChoiceField(
        required=False,
        choices=Product.CONDITION_CHOICES
    )
    sort_by = serializers.ChoiceField(
        required=False,
        choices=[
            'price_asc',
            'price_desc',
            'newest',
            'rating',
            'popularity'
        ]
    )
    in_stock = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if (min_price := attrs.get('min_price')) and (max_price := attrs.get('max_price')):
            if min_price > max_price:
                raise serializers.ValidationError(
                    "Minimum price cannot be greater than maximum price"
                )
        return attrs


class ProductBulkActionSerializer(serializers.Serializer):
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=100  # Reasonable limit
    )
    action = serializers.ChoiceField(
        choices=['delete', 'activate', 'deactivate']
    )

    def validate_product_ids(self, value):
        """Validate product IDs exist and belong to user"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")

        existing_ids = set(Product.objects.filter(
            id__in=value,
            student__user=request.user
        ).values_list('id', flat=True))

        invalid_ids = set(value) - existing_ids
        if invalid_ids:
            raise serializers.ValidationError(
                f"Invalid product IDs: {', '.join(map(str, invalid_ids))}"
            )

        return value


class ProductDraftSerializer(serializers.ModelSerializer):
    """Serializer for product drafts"""
    variants = ProductVariantSerializer(many=True, required=False)
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('999999.99'))
        ],
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 'category',
            'image', 'condition', 'stock', 'variants', 'is_draft',
            'created_at', 'updated_at', 'slug'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def validate(self, attrs):
        """Validate draft data - less strict than published products"""
        # For drafts, we allow partial data
        return attrs

    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        validated_data['is_draft'] = True
        student = Student.objects.get(user=self.context['request'].user)
        product = Product.objects.create(student=student, **validated_data)

        # Create variants if provided
        for variant_data in variants_data:
            variant = ProductVariant.objects.create(**variant_data)
            product.variants.add(variant)

        return product

    def update(self, instance, validated_data):
        variants_data = validated_data.pop('variants', None)
        product = super().update(instance, validated_data)

        if variants_data is not None:
            # Remove existing variants
            product.variants.clear()
            # Add new variants
            for variant_data in variants_data:
                variant = ProductVariant.objects.create(**variant_data)
                product.variants.add(variant)

        return product


class ProductValidationSerializer(serializers.Serializer):
    """Serializer for validating product data before saving"""
    title = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(required=False)
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('999999.99'))
        ],
        required=False
    )
    category = serializers.IntegerField(required=False)
    condition = serializers.ChoiceField(
        choices=Product.CONDITION_CHOICES,
        required=False
    )
    stock = serializers.IntegerField(min_value=0, required=False)

    def validate_category(self, value):
        """Validate category exists"""
        if value and not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid category")
        return value

    def validate(self, attrs):
        """Validate the product data and return validation results"""
        errors = {}
        warnings = []

        # Check required fields for publishing
        if not attrs.get('title'):
            errors['title'] = 'Title is required'
        elif len(attrs['title']) < 3:
            warnings.append('Title should be at least 3 characters long')

        if not attrs.get('description'):
            errors['description'] = 'Description is required'
        elif len(attrs['description']) < 10:
            warnings.append('Description should be at least 10 characters long')

        if not attrs.get('price'):
            errors['price'] = 'Price is required'

        if not attrs.get('category'):
            errors['category'] = 'Category is required'

        # Additional validations
        if attrs.get('price') and attrs['price'] < Decimal('1.00'):
            warnings.append('Very low price - consider if this is correct')

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'data': attrs
        }


class ImageUploadSerializer(serializers.Serializer):
    """Serializer for image upload"""
    image = serializers.ImageField()

    def validate_image(self, value):
        """Validate image file"""
        # Check file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image file too large. Maximum size is 5MB.")

        # Check file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Invalid image format. Only JPEG, PNG, and WebP are allowed.")

        return value


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 'category',
            'image', 'student', 'created_at', 'updated_at', 'slug'
        ]
