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
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('999999.99'))]
    )
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('999999.99'))]
    )
    product = ProductSerializer(read_only=True)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            return product
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['items', 'shipping_address', 'payment_method', 'notes']

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
            order.items.create(product=product, quantity=quantity, price=price)
        order.total_amount = total_amount
        order.save()
        return order


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'items', 'total_amount', 'status',
            'status_display', 'payment_status', 'payment_method',
            'shipping_address', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'total_amount', 'payment_status', 'created_at', 'updated_at']


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['shipping_address', 'notes', 'status']
        read_only_fields = ['status']


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
    class Meta:
        model = Order
        fields = ['status', 'status_display', 'created_at', 'updated_at']

    status_display = serializers.CharField(source='get_status_display', read_only=True)
