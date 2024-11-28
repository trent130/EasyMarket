from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import Product, Category, ProductVariant
from marketplace.models import Student, Review

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
            'created_at'
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
        product = obj.products.first()
        if product:
            return float(product.price) + float(obj.price_adjustment)
        return float(obj.price_adjustment)

    def get_available_stock(self, obj):
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
            'condition', 'created_at'
        ]

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.wishlist.products.filter(id=obj.id).exists()
        return False

    def get_image_url(self, obj):
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
        return {
            'id': obj.student.id,
            'username': obj.student.user.username,
            'rating': obj.student.average_rating,
            'products_count': obj.student.products.count(),
            'joined_date': obj.student.user.date_joined
        }

    def get_reviews(self, obj):
        recent_reviews = obj.reviews.select_related('reviewer').order_by('-created_at')[:3]
        return {
            'average': obj.average_rating,
            'count': obj.review_count,
            'recent': ReviewSerializer(recent_reviews, many=True).data
        }

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.wishlist.products.filter(id=obj.id).exists()
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
        ).order_by('-created_at')[:4]
        return ProductListSerializer(
            related,
            many=True,
            context=self.context
        ).data

class ProductCreateSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'title', 'description', 'price', 'category',
            'image', 'condition', 'stock', 'variants'
        ]

    def validate_price(self, value):
        """Validate price is reasonable"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero")
        if value > 1000000:  # 1 million
            raise serializers.ValidationError("Price is unreasonably high")
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
        decimal_places=2
    )
    max_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2
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
