from django.db.models import Count
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderUpdateSerializer,
    OrderAdminUpdateSerializer,
    OrderCancellationSerializer,
    OrderTrackingSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .select_related('user', 'shipping_address')
            .prefetch_related('items__product')
            .order_by('-created_at')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action in ('update', 'partial_update'):
            if self.request.user.is_staff:
                return OrderAdminUpdateSerializer
            return OrderUpdateSerializer
        if self.action == 'track':
            return OrderTrackingSerializer
        return OrderDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        detail = OrderDetailSerializer(serializer.instance, context={'request': request})
        return Response(detail.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status not in ('pending', 'canceled'):
            return Response(
                {'error': 'Only pending or canceled orders can be deleted.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        serializer = OrderCancellationSerializer(
            data=request.data,
            context={'order': order},
        )
        serializer.is_valid(raise_exception=True)
        order.status = 'canceled'
        order.cancellation_reason = serializer.validated_data['reason']
        order.save(update_fields=['status', 'cancellation_reason'])
        order.send_cancellation_notification()
        return Response(OrderDetailSerializer(order, context={'request': request}).data)

    @action(detail=True, methods=['get'])
    def track(self, request, pk=None):
        order = self.get_object()
        return Response(OrderTrackingSerializer(order).data)

    @action(detail=True, methods=['post'])
    def confirm_delivery(self, request, pk=None):
        order = self.get_object()
        if order.status != 'shipped':
            return Response(
                {'error': 'Order is not in shipped status.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = 'delivered'
        order.save(update_fields=['status'])
        order.send_delivery_confirmation()
        return Response(OrderDetailSerializer(order, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        orders = self.get_queryset()
        page = self.paginate_queryset(orders)
        if page is not None:
            return self.get_paginated_response(
                OrderDetailSerializer(page, many=True, context={'request': request}).data
            )
        return Response(OrderDetailSerializer(orders, many=True, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        counts = (
            self.get_queryset()
            .values('status')
            .annotate(count=Count('id'))
        )
        result = {
            'total': 0,
            'pending': 0, 'processing': 0, 'shipped': 0,
            'delivered': 0, 'canceled': 0, 'refunded': 0, 'returned': 0,
        }
        for row in counts:
            key = row['status']
            if key in result:
                result[key] = row['count']
            result['total'] += row['count']
        return Response(result)

    @action(detail=True, methods=['get'])
    def invoice(self, request, pk=None):
        order = self.get_object()
        if not order.is_paid:
            return Response(
                {'error': 'Cannot generate invoice for unpaid order.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pdf_bytes = order.generate_invoice()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
        return response

    @action(detail=True, methods=['post'])
    def request_refund(self, request, pk=None):
        order = self.get_object()
        if not order.can_request_refund:
            return Response(
                {'error': 'Refund cannot be requested for this order.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reason = request.data.get('reason', '').strip()
        if not reason:
            return Response(
                {'error': 'Refund reason is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        refund = order.create_refund_request(reason)
        return Response({'status': 'Refund requested.', 'refund_id': refund.id})

    @action(detail=True, methods=['get'])
    def payment_status(self, request, pk=None):
        order = self.get_object()
        return Response({
            'payment_status': order.payment_status,
            'payment_method': order.payment_method,
            'is_paid': order.is_paid,
            'payment_date': order.payment_date,
        })
