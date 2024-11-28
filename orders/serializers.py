from decimal import Decimal
from rest_framework import serializers
from .models import Order
from products.models import Product
from marketplace.serializers_marketplace import ProductSerializer
from django.core.validators import MinValueValidator, MaxValueValidator

class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        validators=[MinValueValidator(0.01), MaxValueValidator(Decimal('999999.99'))]
    )
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        validators=[MinValueValidator(0.01), MaxValueValidator(Decimal('999999.99'))]
    )
    product = ProductSerializer(read_only=True)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    shipping_address = serializers.CharField(required=True)

    class Meta:
        model = Order
        fields = [
            'items', 'shipping_address', 'payment_method',
            'special_instructions'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        total_amount = 0
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            price = product.price
            quantity = item_data['quantity']
            total = price * quantity
            total_amount += total
            
            order.items.create(
                product=product,
                quantity=quantity,
                price=price,
                total=total
            )
        
        order.total_amount = total_amount
        order.save()
        return order

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(
        source='get_payment_status_display',
        read_only=True
    )
    tracking_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'items', 'total_amount', 'status',
            'status_display', 'payment_status', 'payment_status_display',
            'shipping_address', 'tracking_number', 'tracking_url',
            'special_instructions', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'total_amount', 'payment_status',
            'tracking_number', 'created_at', 'updated_at'
        ]

    def get_tracking_url(self, obj):
        if obj.tracking_number:
            # Replace with actual tracking URL generation
            return f"https://tracking.example.com/{obj.tracking_number}"
        return None

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['shipping_address', 'special_instructions', 'status']
        read_only_fields = ['status']  # Status can only be updated by staff

class OrderCancellationSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)
    
    def validate(self, data):
        order = self.context['order']
        if order.status not in ['pending', 'paid']:
            raise serializers.ValidationError(
                "Order cannot be cancelled in its current status"
            )
        return data

class OrderTrackingSerializer(serializers.ModelSerializer):
    status_history = serializers.SerializerMethodField()
    estimated_delivery = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'status', 'status_display', 'tracking_number',
            'tracking_url', 'status_history', 'estimated_delivery'
        ]

    def get_status_history(self, obj):
        # This would be implemented based on your order tracking system
        return [
            {
                'status': status.status,
                'location': status.location,
                'timestamp': status.timestamp,
                'description': status.description
            }
            for status in obj.status_history.all()
        ]
