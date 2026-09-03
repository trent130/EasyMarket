from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Transaction
from .serializers import (
    MpesaPaymentSerializer,
    # CardPaymentSerializer,
    TransactionSerializer,
    PaymentVerificationSerializer,
    RefundSerializer,
    PaymentReceiptSerializer,
    PaymentHistorySerializer
)
from .mpesa import MpesaClient
from orders.models import Order
import logging

logger = logging.getLogger(__name__)


def _normalise_payment_status(value):
    """Map provider and model status values to the public API contract."""
    normalised = str(value or '').strip().lower()
    if normalised in {'completed', 'success', 'succeeded'}:
        return 'completed'
    if normalised in {'failed', 'timeout', 'timed_out', 'cancelled', 'canceled'}:
        return 'failed'
    return 'pending'


def _mark_payment_completed(transaction, order, user):
    """Persist payment and order completion as one database transaction."""
    completed_at = timezone.now()
    with db_transaction.atomic():
        locked_transaction = Transaction.objects.select_for_update().get(
            id=transaction.id,
            user=user,
        )
        locked_order = Order.objects.select_for_update().get(
            id=order.id,
            user=user,
        )

        locked_transaction.status = 'completed'
        locked_transaction.save(update_fields=['status', 'updated_at'])

        order_updates = []
        if not locked_order.payment_status:
            locked_order.payment_status = True
            order_updates.append('payment_status')
        if locked_order.payment_date is None:
            locked_order.payment_date = completed_at
            order_updates.append('payment_date')
        if order_updates:
            order_updates.append('updated_at')
            locked_order.save(update_fields=order_updates)


def _order_for_transaction(transaction):
    """Resolve the order encoded in the payment reference without trusting the request."""
    prefix = 'Order-'
    if not transaction.reference.startswith(prefix):
        return None
    try:
        order_id = int(transaction.reference[len(prefix):])
    except (TypeError, ValueError):
        return None
    return Order.objects.filter(
        id=order_id,
        user=transaction.user,
        total_amount=transaction.amount,
    ).first()


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    lookup_field = 'transaction_id'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mpesa(self, request):
        serializer = MpesaPaymentSerializer(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            order_id = serializer.validated_data['order_id']
            order = get_object_or_404(
                Order,
                id=order_id,
                user=request.user,
                payment_status=False,
            )
            try:
                # Initialize M-Pesa client
                mpesa = MpesaClient()
                # Start STK Push
                response = mpesa.stk_push(
                    phone_number=phone_number,
                    amount=order.total_amount,
                    account_reference=f"Order-{order.id}",
                    transaction_desc=f"Payment for Order #{order.id}"
                )
                if str(response.get('ResponseCode')) == '0':
                    checkout_request_id = response.get('CheckoutRequestID')
                    if not checkout_request_id:
                        return Response({
                            'error': 'Payment provider returned an invalid response'
                        }, status=status.HTTP_502_BAD_GATEWAY)

                    # Create transaction record
                    import uuid
                    transaction = Transaction.objects.create(
                        user=request.user,
                        transaction_id=str(uuid.uuid4()),
                        amount=order.total_amount,
                        payment_method='MPESA',
                        phone_number=phone_number,
                        reference=f"Order-{order.id}",
                        description=f"Payment for Order #{order.id}",
                        status='pending',
                        merchant_request_id=response.get('MerchantRequestID'),
                        checkout_request_id=str(checkout_request_id),
                    )
                    return Response({
                        'message': 'Payment initiated',
                        'transaction_id': str(transaction.transaction_id),
                        'checkout_request_id': str(checkout_request_id),
                        'status': 'pending',
                    })
                else:
                    return Response({
                        'error': 'Failed to initiate payment',
                        'details': response.get('ResponseDescription')
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"M-Pesa payment error: {str(e)}")
                return Response({
                    'error': 'Payment processing failed'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify_payment(self, request):
        serializer = PaymentVerificationSerializer(data=request.data)
        if serializer.is_valid():
            transaction_id = serializer.validated_data['transaction_id']
            order_id = serializer.validated_data['order_id']
            order = get_object_or_404(
                Order,
                id=order_id,
                user=request.user,
            )
            try:
                transaction = Transaction.objects.get(
                    transaction_id=transaction_id,
                    user=request.user,
                    reference=f'Order-{order.id}',
                    amount=order.total_amount,
                )
            except Transaction.DoesNotExist:
                return Response({
                    'error': 'Transaction not found'
                }, status=status.HTTP_404_NOT_FOUND)

            # Check for payment timeout (2 minutes) while still pending.
            payment_timeout = 120
            if (
                transaction.status == 'pending'
                and (timezone.now() - transaction.timestamp).total_seconds() > payment_timeout
            ):
                transaction.status = 'failed'
                transaction.save(update_fields=['status', 'updated_at'])
                return Response({
                    'status': 'failed',
                    'message': 'Payment timeout. Please try again.'
                }, status=status.HTTP_408_REQUEST_TIMEOUT)

            if transaction.payment_method.upper() == 'MPESA':
                mpesa = MpesaClient()
                provider_status = mpesa.check_payment_status(
                    transaction.checkout_request_id
                )
                payment_status = _normalise_payment_status(provider_status)
                if payment_status == 'completed':
                    _mark_payment_completed(transaction, order, request.user)
                    return Response({
                        'status': 'completed',
                        'message': 'Payment completed',
                    })

                if payment_status == 'failed':
                    transaction.status = 'failed'
                    transaction.save(update_fields=['status', 'updated_at'])

                return Response({
                    'status': payment_status,
                    'message': f'Payment {payment_status}',
                })

            payment_status = _normalise_payment_status(transaction.status)
            if payment_status == 'completed':
                _mark_payment_completed(transaction, order, request.user)
            return Response({
                'status': payment_status,
                'message': f'Payment {payment_status}',
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def refund(self, request, transaction_id=None):
        transaction = self.get_object()
        serializer = RefundSerializer(
            data=request.data,
            context={'transaction': transaction},
        )
        if serializer.is_valid():
            amount = serializer.validated_data.get('amount', transaction.amount)
            reason = serializer.validated_data['reason']
            try:
                if transaction.payment_method.upper() == 'MPESA':
                    mpesa = MpesaClient()
                    refund_response = mpesa.process_refund(
                        transaction_id=transaction.transaction_id,
                        amount=amount,
                        remarks=reason
                    )
                    if refund_response.get('success'):
                        transaction.status = 'refunded'
                        transaction.save()
                        return Response({
                            'message': 'Refund processed successfully',
                            'refund_id': refund_response.get('refund_id')
                        })
                    return Response({
                        'error': 'Refund failed',
                        'details': refund_response.get('message')
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Refund processing error: {str(e)}")
                return Response({
                    'error': 'Refund processing failed'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def receipt(self, request, transaction_id=None):
        transaction = self.get_object()
        serializer = PaymentReceiptSerializer(transaction)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        transactions = self.get_queryset().order_by('-timestamp')
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = PaymentHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PaymentHistorySerializer(transactions, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def mpesa_callback(request):
    """Handle M-Pesa payment callbacks"""
    try:
        # Validate callback data
        callback_data = request.data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = callback_data.get('CheckoutRequestID')
        if not checkout_request_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # Find corresponding transaction
        transaction = get_object_or_404(
            Transaction,
            checkout_request_id=checkout_request_id
        )
        result_code = callback_data.get('ResultCode')
        if str(result_code) == '0':  # Success
            order = _order_for_transaction(transaction)
            if order is not None:
                _mark_payment_completed(transaction, order, transaction.user)
            else:
                logger.error(
                    'M-Pesa callback matched transaction %s but no matching order was found',
                    transaction.transaction_id,
                )
                transaction.status = 'completed'
                transaction.save(update_fields=['status', 'updated_at'])
        else:  # Failed
            transaction.status = 'failed'
            transaction.save(update_fields=['status', 'updated_at'])
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"M-Pesa callback error: {str(e)}")
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
