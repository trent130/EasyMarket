from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404
from .models import Product, Category
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
    ProductSearchSerializer,
    ProductBulkActionSerializer,
    CategorySerializer
)
from marketplace.models import Student
import logging

logger = logging.getLogger(__name__)

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.select_related(
            'category', 'student', 'student__user'
        ).prefetch_related('reviews')

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Filter by student
        student = self.request.query_params.get('student')
        if student:
            queryset = queryset.filter(student_id=student)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        return ProductDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['post'])
    def search(self, request):
        serializer = ProductSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        queryset = self.get_queryset()
        data = serializer.validated_data

        # Apply search query
        if query := data.get('query'):
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

        # Apply sorting
        sort_by = data.get('sort_by')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'rating':
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating')

        # Serialize results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        serializer = ProductBulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        products = Product.objects.filter(
            id__in=serializer.validated_data['product_ids'],
            student__user=request.user
        )

        action = serializer.validated_data['action']
        if action == 'delete':
            products.delete()
        elif action == 'activate':
            products.update(is_active=True)
        elif action == 'deactivate':
            products.update(is_active=False)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        product = self.get_object()
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(
            id=product.id
        ).order_by('-created_at')[:4]

        serializer = ProductListSerializer(
            related_products,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_products(self, request):
        queryset = self.get_queryset().filter(student__user=request.user)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = ProductListSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.annotate(
        products_count=Count('product')
    )
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        category = self.get_object()
        products = Product.objects.filter(category=category)
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(
            products,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
