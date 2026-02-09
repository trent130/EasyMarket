from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Q
from products.models import Product
from products.serializers import ProductListSerializer
from users.permissions import IsStudentOrAdmin


class TextbookViewSet(viewsets.ModelViewSet):
    """ViewSet for textbook-specific operations"""
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'isbn', 'course_code', 'subject']
    ordering_fields = ['created_at', 'price', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get textbooks (products with ISBN)"""
        queryset = Product.objects.filter(
            is_active=True,
            isbn__isnull=False
        ).exclude(isbn='')
        
        # Filter by parameters
        title = self.request.query_params.get('title')
        subject = self.request.query_params.get('subject')
        condition = self.request.query_params.get('condition')
        exchange_option = self.request.query_params.get('exchangeOption')
        course_code = self.request.query_params.get('course_code')
        
        if title:
            queryset = queryset.filter(title__icontains=title)
        if subject:
            queryset = queryset.filter(subject__icontains=subject)
        if condition:
            queryset = queryset.filter(condition=condition)
        if exchange_option:
            queryset = queryset.filter(exchange_option=exchange_option)
        if course_code:
            queryset = queryset.filter(course_code__icontains=course_code)
            
        return queryset

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsStudentOrAdmin()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search textbooks with filters"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'total': queryset.count(),
            'page': 1
        })

    @action(detail=False, methods=['get'])
    def course_codes(self, request):
        """Get list of unique course codes"""
        codes = Product.objects.filter(
            is_active=True,
            course_code__isnull=False
        ).exclude(
            course_code=''
        ).values_list('course_code', flat=True).distinct()
        
        return Response(list(codes))

    @action(detail=True, methods=['get'])
    def lookup(self, request, pk=None):
        """Lookup textbook by ISBN"""
        try:
            textbook = Product.objects.get(isbn=pk, is_active=True)
            serializer = self.get_serializer(textbook)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Textbook not found'},
                status=status.HTTP_404_NOT_FOUND
            )
