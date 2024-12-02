from rest_framework import serializers
from .models import Student, Cart, CartItem, WishList, Review
from products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 'category',
            'image', 'student', 'created_at', 'updated_at', 'slug'
        ]

class StudentProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField()
    avatar = serializers.ImageField(source='userprofile.avatar')

    class Meta:
        model = Student
        fields = [
            'id', 'user_id', 'username', 'first_name', 'last_name',
            'email', 'bio', 'avatar', 'two_factor_enabled'
        ]

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

class WishListSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = WishList
        fields = ['id', 'user', 'products', 'product_ids', 'auto_now']
        read_only_fields = ['user', 'auto_now']

    def create(self, validated_data):
        product_ids = validated_data.pop('product_ids', [])
        wishlist = WishList.objects.create(**validated_data)
        if product_ids:
            products = Product.objects.filter(id__in=product_ids)
            wishlist.products.set(products)
        return wishlist

class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    slug = serializers.SlugField(read_only=True)
    description = serializers.CharField(required=False)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=False
    )
    image = serializers.ImageField(required=False)
    product_count = serializers.IntegerField(read_only=True)

class SearchResultSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)
    total_results = serializers.IntegerField()
    categories = CategorySerializer(many=True)
    price_range = serializers.DictField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2)
    )
