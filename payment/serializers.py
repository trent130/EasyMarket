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
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Order not found")

        order = Order.objects.filter(
            id=value,
            user=user,
            payment_status=False,
        ).first()
        if order is None:
            raise serializers.ValidationError("Order not found or already paid")
        return value


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
        read_only=True,
        required=False,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('999999.99'))]
    )

    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'merchant_request_id', 'amount', 'status',
            'status_display', 'payment_method', 'payment_method_display',
            'phone_number', 'reference', 'checkout_request_id',
            'timestamp', 'updated_at', 'description'
        ]
        read_only_fields = [
            'status', 'transaction_id', 'merchant_request_id', 'amount',
            'payment_method', 'phone_number', 'reference',
            'checkout_request_id', 'description', 'timestamp', 'updated_at'
        ]


class PaymentVerificationSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()
    order_id = serializers.IntegerField()


class RefundSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(required=False, write_only=True)
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('99999.99'))]
    )
    reason = serializers.CharField()

    def validate(self, data):
        transaction = self.context.get('transaction')
        if transaction is None:
            raise serializers.ValidationError("Transaction not found")

        submitted_id = data.get('transaction_id')
        if submitted_id and submitted_id != transaction.transaction_id:
            raise serializers.ValidationError("Transaction does not match the URL")
        if transaction.status != 'completed':
            raise serializers.ValidationError(
                "Can only refund completed transactions"
            )
        if data.get('amount') and data['amount'] > transaction.amount:
            raise serializers.ValidationError(
                "Refund amount cannot exceed transaction amount"
            )
        return data


class PaymentReceiptSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    payment_method_details = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'amount', 'status',
            'payment_method', 'customer_name', 'payment_method_details',
            'timestamp', 'description'
        ]

    def get_customer_name(self, obj):
        full_name = obj.user.get_full_name()
        return full_name if full_name else obj.user.email

    def get_payment_method_details(self, obj):
        if str(obj.payment_method).upper() == 'MPESA':
            return {
                'type': 'M-Pesa',
                'phone': obj.phone_number,
            }
        return None


class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'amount', 'status',
            'payment_method', 'reference', 'phone_number', 'timestamp'
        ]
