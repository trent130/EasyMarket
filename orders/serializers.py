from decimal import Decimal
from rest_framework import serializers
from .models import Order, OrderItem, ShippingAddress, Refund
from products.models import Product
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class OrderUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'postal_code', 'is_default',
        ]
        read_only_fields = ['id']


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    product_name = serializers.CharField(source='product.title', read_only=True)
    product_image = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'product_image', 'quantity', 'price', 'total']
        read_only_fields = ['id', 'price', 'total']

    def get_product_image(self, obj):
        if obj.product and hasattr(obj.product, 'images'):
            first = obj.product.images.first()
            if first:
                return first.image.url
        return None

    def get_total(self, obj):
        return str(Decimal(str(obj.price)) * obj.quantity)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError('Product not found.')
        return value


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    shipping_address = ShippingAddressSerializer(required=False)

    class Meta:
        model = Order
        fields = ['items', 'shipping_address', 'payment_method', 'notes']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        shipping_data = validated_data.pop('shipping_address', None)

        shipping_address = None
        if shipping_data:
            shipping_address = ShippingAddress.objects.create(
                user=validated_data['user'],
                **shipping_data,
            )

        order = Order.objects.create(
            **validated_data,
            shipping_address=shipping_address,
            total_amount=Decimal('0.00'),
        )

        total = Decimal('0.00')
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            price = product.price
            qty = item_data['quantity']
            total += Decimal(str(price)) * qty
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=price)

        order.total_amount = total
        order.save(update_fields=['total_amount'])
        return order


class OrderDetailSerializer(serializers.ModelSerializer):
    user = OrderUserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    can_request_refund = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'reference', 'user', 'items', 'total_amount', 'status',
            'status_display', 'cancellation_reason', 'payment_method',
            'payment_status', 'payment_date', 'is_paid', 'can_request_refund',
            'shipping_address', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'reference', 'user', 'total_amount', 'payment_status',
            'payment_date', 'created_at', 'updated_at',
        ]


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['notes']


class OrderAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'payment_status', 'payment_date', 'notes']


class OrderCancellationSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, min_length=5)

    def validate(self, data):
        order = self.context['order']
        if order.status not in ('pending', 'processing'):
            raise serializers.ValidationError(
                'Only pending or processing orders can be canceled.'
            )
        return data


class OrderTrackingSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'reference', 'status', 'status_display', 'payment_status', 'created_at', 'updated_at']


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['id', 'order', 'reason', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']
