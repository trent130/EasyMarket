from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..serializers import OrderSerializer, OrderItemSerializer, ShippingAddressSerializer
from orders.models import Order, OrderItem, ShippingAddress

class ShippingAddressViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # If this is marked as default, remove default from other addresses
        if serializer.validated_data.get('is_default', False):
            self.get_queryset().filter(is_default=True).update(is_default=False)
        serializer.save(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_payment_status(self, request, pk=None):
        order = self.get_object()
        payment_status = request.data.get('payment_status')
        
        if not isinstance(payment_status, bool):
            return Response(
                {'error': 'Invalid payment status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.payment_status = payment_status
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = self.get_queryset().filter(status=status_filter)
            serializer = self.get_serializer(orders, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Status parameter not provided'},
            status=status.HTTP_400_BAD_REQUEST
        )

class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return OrderItem.objects.all()
        return OrderItem.objects.filter(order__user=self.request.user)
