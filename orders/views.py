from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderUpdateSerializer,
    OrderCancellationSerializer,
    OrderTrackingSerializer
)
from marketplace.middleware import TwoFactorMiddleware

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        elif self.action == 'track':
            return OrderTrackingSerializer
        return OrderDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        serializer = OrderCancellationSerializer(
            data=request.data,
            context={'order': order}
        )
        
        if serializer.is_valid():
            order.status = 'cancelled'
            order.cancellation_reason = serializer.validated_data['reason']
            order.save()
            
            # Send cancellation notification
            order.send_cancellation_notification()
            
            return Response({'status': 'Order cancelled'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def track(self, request, pk=None):
        order = self.get_object()
        serializer = OrderTrackingSerializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirm_delivery(self, request, pk=None):
        order = self.get_object()
        if order.status != 'shipped':
            return Response(
                {'error': 'Order is not in shipped status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'delivered'
        order.save()
        
        # Send delivery confirmation
        order.send_delivery_confirmation()
        
        return Response({'status': 'Delivery confirmed'})

    @action(detail=False, methods=['get'])
    def history(self, request):
        orders = self.get_queryset().order_by('-created_at')
        page = self.paginate_queryset(orders)
        
        if page is not None:
            serializer = OrderDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderDetailSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def invoice(self, request, pk=None):
        order = self.get_object()
        if not order.is_paid:
            return Response(
                {'error': 'Cannot generate invoice for unpaid order'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate invoice (implement your invoice generation logic)
        invoice_file = order.generate_invoice()
        
        response = Response(invoice_file)
        response['Content-Type'] = 'application/pdf'
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
        return response

    @action(detail=True, methods=['post'])
    def request_refund(self, request, pk=None):
        order = self.get_object()
        if not order.can_request_refund:
            return Response(
                {'error': 'Refund cannot be requested for this order'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason')
        if not reason:
            return Response(
                {'error': 'Refund reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create refund request
        refund = order.create_refund_request(reason)
        
        return Response({
            'status': 'Refund requested',
            'refund_id': refund.id
        })

    @action(detail=True, methods=['get'])
    def payment_status(self, request, pk=None):
        order = self.get_object()
        return Response({
            'status': order.payment_status,
            'payment_method': order.payment_method,
            'is_paid': order.is_paid,
            'payment_date': order.payment_date
        })

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status not in ['pending', 'cancelled']:
            return Response(
                {'error': 'Only pending or cancelled orders can be deleted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
