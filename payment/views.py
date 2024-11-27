from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Transaction
from .serializers import (
    MpesaPaymentSerializer,
    CardPaymentSerializer,
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

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(order__user=self.request.user)

    @action(detail=False, methods=['post'])
    def mpesa(self, request):
        serializer = MpesaPaymentSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            order_id = serializer.validated_data['order_id']
            
            order = Order.objects.get(id=order_id)
            
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
                
                if response.get('ResponseCode') == '0':
                    # Create transaction record
                    transaction = Transaction.objects.create(
                        order=order,
                        amount=order.total_amount,
                        payment_method='mpesa',
                        status='pending',
                        checkout_request_id=response.get('CheckoutRequestID')
                    )
                    
                    return Response({
                        'message': 'Payment initiated',
                        'transaction_id': transaction.id,
                        'checkout_request_id': response.get('CheckoutRequestID')
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
            
            try:
                transaction = Transaction.objects.get(
                    transaction_id=transaction_id,
                    order_id=order_id
                )
                
                if transaction.payment_method == 'mpesa':
                    mpesa = MpesaClient()
                    status = mpesa.check_payment_status(
                        transaction.checkout_request_id
                    )
                    
                    if status == 'completed':
                        transaction.status = 'completed'
                        transaction.save()
                        
                        # Update order status
                        transaction.order.payment_status = 'paid'
                        transaction.order.save()
                        
                        return Response({'status': 'Payment completed'})
                    
                    return Response({
                        'status': status,
                        'message': 'Payment pending'
                    })
                    
            except Transaction.DoesNotExist:
                return Response({
                    'error': 'Transaction not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        transaction = self.get_object()
        serializer = RefundSerializer(data=request.data)
        
        if serializer.is_valid():
            amount = serializer.validated_data.get('amount', transaction.amount)
            reason = serializer.validated_data['reason']
            
            try:
                if transaction.payment_method == 'mpesa':
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
    def receipt(self, request, pk=None):
        transaction = self.get_object()
        serializer = PaymentReceiptSerializer(transaction)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        transactions = self.get_queryset().order_by('-created_at')
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
        
        if result_code == 0:  # Success
            transaction.status = 'completed'
            transaction.payment_details = callback_data
            transaction.save()
            
            # Update order status
            order = transaction.order
            order.payment_status = 'paid'
            order.save()
            
            # Send payment confirmation
            order.send_payment_confirmation()
            
        else:  # Failed
            transaction.status = 'failed'
            transaction.payment_details = callback_data
            transaction.save()
            
        return Response(status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"M-Pesa callback error: {str(e)}")
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
