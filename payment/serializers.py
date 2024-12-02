from decimal import Decimal
from rest_framework import serializers
from .models import Transaction
from orders.models import Order
from django.core.validators import MinValueValidator, MaxValueValidator

class PaymentMethodSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['mpesa', 'card', 'bank'])
    details = serializers.DictField(required=False)
    is_default = serializers.BooleanField(default=False)

class MpesaPaymentSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    order_id = serializers.IntegerField()

    def validate_phone_number(self, value):
        # Remove any spaces or special characters
        cleaned = ''.join(filter(str.isdigit, value))
        
        # Validate Kenyan phone number format
        if not cleaned.startswith('254') or len(cleaned) != 12:
            raise serializers.ValidationError(
                "Invalid phone number format. Use format: 254XXXXXXXXX"
            )
        return cleaned

    def validate_order_id(self, value):
        try:
            order = Order.objects.get(id=value)
            if order.is_paid:
                raise serializers.ValidationError("Order is already paid")
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")

class CardPaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    token = serializers.CharField()  # Card token from payment processor
    save_card = serializers.BooleanField(default=False)

class TransactionSerializer(serializers.ModelSerializer):
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('999999.99'))]
    )
    class Meta:
        model = Transaction
        fields = [
            'id', 'order', 'amount', 'currency', 'status',
            'status_display', 'payment_method', 'payment_method_display',
            'transaction_id', 'account_reference', 'created_at',
            'updated_at', 'description'
        ]
        read_only_fields = [
            'status', 'transaction_id', 'account_reference',
            'created_at', 'updated_at'
        ]

class PaymentVerificationSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()
    order_id = serializers.IntegerField()

class RefundSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('999999.99'))]
    )
    reason = serializers.CharField()

    def validate(self, data):
        try:
            transaction = Transaction.objects.get(
                transaction_id=data['transaction_id']
            )
            if transaction.status != 'completed':
                raise serializers.ValidationError(
                    "Can only refund completed transactions"
                )
            if data.get('amount'):
                if data['amount'] > transaction.amount:
                    raise serializers.ValidationError(
                        "Refund amount cannot exceed transaction amount"
                    )
            return data
        except Transaction.DoesNotExist:
            raise serializers.ValidationError("Transaction not found")

class PaymentReceiptSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    payment_method_details = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'amount', 'currency',
            'payment_method', 'customer_name', 'payment_method_details',
            'created_at', 'description'
        ]

    def get_customer_name(self, obj):
        return f"{obj.order.user.first_name} {obj.order.user.last_name}"

    def get_payment_method_details(self, obj):
        if obj.payment_method == 'mpesa':
            return {
                'type': 'M-Pesa',
                'phone': obj.payment_details.get('phone_number'),
                'confirmation_code': obj.payment_details.get('mpesa_receipt')
            }
        return None

class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'order', 'amount', 'currency', 'status',
            'payment_method', 'transaction_id', 'created_at'
        ]
