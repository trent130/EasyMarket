from rest_framework import serializers
from django.db.models import Avg
from .models import Cart, CartItem, WishList, Review
from products.models import Product, Category
from users.serializers import StudentProfileSerializer
from products.serializers import ProductSerializer

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = StudentProfileSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'product', 'reviewer', 'rating',
            'comment', 'timestamp'
        ]
        read_only_fields = ['reviewer', 'timestamp']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'product', 'product_id',
            'quantity', 'total_price', 'added_at'
        ]
        read_only_fields = ['cart', 'added_at', 'total_price']

    def validate_quantity(self, value):
        """
        Validate quantity is at least 1.
        """
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True, source='cartitem_set')
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'items', 'total_items',
            'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class WishListItemSerializer(serializers.ModelSerializer):
    """Enhanced product serializer for wishlist items with seller information"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    seller = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True)
    available_stock = serializers.IntegerField(read_only=True)
    image_url = serializers.SerializerMethodField()
    has_variants = serializers.BooleanField(source='variants.exists', read_only=True)
    total_sales = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'price', 'category',
            'category_name', 'image_url', 'seller',
            'average_rating', 'available_stock',
            'condition', 'created_at', 'total_sales', 'has_variants',
        ]

    def get_seller(self, obj):
        """Return detailed seller information"""
        student = obj.student
        return {
            'id': student.id,
            'username': student.user.username,
            'email': student.user.email,
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'date_joined': student.user.date_joined,
            'products_count': student.products.filter(is_active=True).count(),
            'average_rating': student.products.aggregate(
                avg_rating=Avg('reviews__rating')
            )['avg_rating'] or 0.0
        }

    def get_image_url(self, obj):
        """Return the absolute URL of the product image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None


class WishListSerializer(serializers.ModelSerializer):
    products = WishListItemSerializer(many=True, read_only=True)
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = WishList
        fields = ['id', 'user', 'products', 'product_ids', 'auto_now', 'total_items']
        read_only_fields = ['user', 'auto_now']

    def get_total_items(self, obj):
        """Return total number of items in wishlist"""
        return obj.products.count()

    def create(self, validated_data):
        """
        Create a new wishlist and add the given product IDs to it.
        Args:
            validated_data (dict): The validated data from the serializer.
        Returns:
            WishList: The newly created wishlist.
        """
        product_ids = validated_data.pop('product_ids', [])
        wishlist = WishList.objects.create(**validated_data)
        if product_ids:
            products = Product.objects.filter(id__in=product_ids)
            wishlist.products.set(products)
        return wishlist


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description',
            'image', 'product_count', 'is_active'
        ]
        read_only_fields = ['slug']


class SearchResultSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)
    total_results = serializers.IntegerField()
    categories = CategorySerializer(many=True)
    price_range = serializers.DictField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2)
    )
