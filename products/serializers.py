from rest_framework import serializers
from .models import Product, Category
from marketplace.models import Student
from django.db.models import Avg

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'product_count']

    def get_product_count(self, obj):
        return obj.product_set.count()

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    student_name = serializers.CharField(source='student.user.username', read_only=True)
    average_rating = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'price', 'category',
            'category_name', 'image', 'student', 'student_name',
            'average_rating', 'is_wishlisted', 'created_at'
        ]

    def get_average_rating(self, obj):
        return obj.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.wishlist.products.filter(id=obj.id).exists()
        return False

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    student = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'price',
            'category', 'image', 'student', 'reviews',
            'is_wishlisted', 'related_products', 'created_at',
            'updated_at'
        ]

    def get_student(self, obj):
        return {
            'id': obj.student.id,
            'username': obj.student.user.username,
            'rating': obj.student.reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
            'products_count': obj.student.products.count()
        }

    def get_reviews(self, obj):
        return {
            'average': obj.reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
            'count': obj.reviews.count(),
            'recent': [
                {
                    'id': review.id,
                    'rating': review.rating,
                    'comment': review.comment,
                    'reviewer': review.reviewer.username,
                    'created_at': review.created_at
                }
                for review in obj.reviews.order_by('-created_at')[:3]
            ]
        }

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.wishlist.products.filter(id=obj.id).exists()
        return False

    def get_related_products(self, obj):
        related = Product.objects.filter(
            category=obj.category
        ).exclude(
            id=obj.id
        ).order_by('-created_at')[:4]
        return ProductListSerializer(related, many=True).data

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'price', 'category',
            'image'
        ]

    def create(self, validated_data):
        student = Student.objects.get(user=self.context['request'].user)
        return Product.objects.create(student=student, **validated_data)

class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'price', 'category',
            'image'
        ]

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        if instance and instance.student.user != self.context['request'].user:
            raise serializers.ValidationError(
                "You don't have permission to update this product"
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
    sort_by = serializers.ChoiceField(
        required=False,
        choices=[
            'price_asc',
            'price_desc',
            'newest',
            'rating'
        ]
    )

class ProductBulkActionSerializer(serializers.Serializer):
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(
        choices=['delete', 'activate', 'deactivate']
    )
