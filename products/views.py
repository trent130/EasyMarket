from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Avg, F, Count, Sum, Q
from django.db import models
from django.db.models import Prefetch
from marketplace.models import Review
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.conf import settings
from django.utils.text import slugify
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
from .search import search_products
from marketplace.models import Student
import logging

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_TTL = getattr(settings, 'PRODUCT_CACHE_TTL', 3600)  # 1 hour default
CACHE_PREFIX = 'products:'


def get_cache_key(prefix, identifier):
    """Generate cache key with prefix"""
    return f'{CACHE_PREFIX}{prefix}:{identifier}'


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category__name']
    ordering_fields = ['price', 'created_at', 'title', 'stock']
    ordering = ['-created_at']
    lookup_field = 'slug'

    # ...
    def get_queryset(self):
        """
        Override get_queryset to include necessary joins and annotations.

        The included annotations are:

        - avg_rating: the average rating of the product
        - review_count: the number of reviews the product has
        - total_sales_amount: the total amount of money the product has made in sales
        """
        queryset = Product.objects.select_related(
            'category',
            'student',
            'student__user'
        ).prefetch_related(
            Prefetch(
                'reviews',
                queryset=Review.objects.select_related('reviewer').order_by('-timestamp')
            ),
            'variants'
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews'),
            total_sales_amount=Sum(F('price') * F('total_sales'), output_field=models.DecimalField())
        )

        return queryset

    def increment_views(self, product):
        from django.core.cache import cache

        """
        Increment product view count with rate limiting
        """
        # Check if the view has been recently incremented (e.g., within the last minute)
        cache_key = f'product_view_{product.id}_{request.user.id}'
        if not cache.get(cache_key):
            Product.objects.filter(id=product.id).update(views_count=F('views_count') + 1)
           
            # Set a cache to prevent frequent updates
            cache.set(cache_key, True, 3600)  # 1 hour cooldown per user

    def get_object(self):
        """Get single object with caching"""
        slug = self.kwargs.get('slug')
        cache_key = get_cache_key('detail', slug)
        obj = cache.get(cache_key)

        if obj is None:
            """ obj = super().get_object() """
            obj = get_object_or_404(Product, slug=slug, is_active=True)
            cache.set(cache_key, obj, CACHE_TTL)

        # Increment views count
        obj.increment_views()
        return obj
        
    def retrieve(self, request, slug=None):
        """
        Retrieve a product by its slug.
        
        Note the method signature uses 'slug' instead of 'pk'
        """
        try:
            cache_key = get_cache_key('detail', slug)
            cached_results = cache.get(cache_key)

            if cached_results is not None:
                return Response(cached_results)

            # Use get_object_or_404 with the slug
            product = self.get_object()
            
            # Increment views count
            product.increment_views()
            
            # Serialize and return the product
            serializer = self.get_serializer(product)

            # cache the serialized data for 1 hour
            cache.set(cache_key, serializer.data, timeout=3600)
            return Response(serializer.data)
            
        except Product.DoesNotExist:
            return Response({
                'detail': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            # Log the error
            logger.error(f"Error retrieving product: {str(e)}")
            return Response({
                'detail': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the current action.

        - For 'list' action, return ProductListSerializer.
        - For 'create' action, return ProductCreateSerializer.
        - For 'update' and 'partial_update' actions, return ProductUpdateSerializer.
        - For other actions, return ProductDetailSerializer.
        """
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        return ProductDetailSerializer

    def perform_create(self, serializer):
        """Create product with inventory tracking"""
        student = Student.objects.get(user=self.request.user)
        product = serializer.save(student=student)
        
        # Initialize statistics
        product.total_sales = 0
        product.total_revenue = 0
        product.average_rating = 0
        product.review_count = 0
        product.save()
        
        # Clear relevant caches
        cache.delete_pattern(f'{CACHE_PREFIX}list:*')
        logger.info(f'Product created: {product.id} by student {student.id}')

    def perform_update(self, serializer):
        """Update product with cache management"""
        product = serializer.save()
        
        # Clear relevant caches
        cache.delete(get_cache_key('detail', product.id))
        cache.delete_pattern(f'{CACHE_PREFIX}list:*')
        logger.info(f'Product updated: {product.id}')

    def perform_destroy(self, instance):
        """Soft delete with cache management"""
        instance.is_active = False
        instance.save()
        
        # Clear relevant caches
        cache.delete(get_cache_key('detail', instance.id))
        cache.delete_pattern(f'{CACHE_PREFIX}list:*')
        logger.info(f'Product deactivated: {instance.id}')

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced product search with caching"""
        # Validate search parameters
        serializer = ProductSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Generate cache key based on search parameters
        cache_key = get_cache_key('search', slugify(str(request.query_params)))
        cached_results = cache.get(cache_key)

        if cached_results is not None:
            return Response(cached_results)

        # Perform search using search module

        queryset = search_products(
            query=data.get('query'),
            filters={
                'category': data.get('category'),
                'min_price': data.get('min_price'),
                'max_price': data.get('max_price'),
                'condition': data.get('condition'),
                'sort_by': data.get('sort_by'),
                'in_stock': data.get('in_stock'),
            }
        )

        # Handle pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(
                page,
                many=True,
                context={'request': request}
            )
            response_data = self.get_paginated_response(serializer.data).data
        else:
            serializer = ProductListSerializer(
                queryset,
                many=True,
                context={'request': request}
            )
            response_data = serializer.data

        # Cache the results
        cache.set(cache_key, response_data, CACHE_TTL)
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products with caching"""
        cache_key = get_cache_key('featured', '')
        cached_results = cache.get(cache_key)

        if cached_results is not None:
            return Response(cached_results)

        queryset = self.get_queryset().filter(
            featured=True,
            stock__gt=F('reserved_stock')
        ).order_by('-created_at')[:8]

        serializer = ProductListSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        response_data = serializer.data
        cache.set(cache_key, response_data, CACHE_TTL)
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending products based on views, sales and ratings"""
        cache_key = get_cache_key('trending', '')
        cached_results = cache.get(cache_key)

        if cached_results is not None:
            return Response(cached_results)

        # Get products with high view counts, sales and ratings
        queryset = self.get_queryset().filter(
            stock__gt=F('reserved_stock')
        ).annotate(
            popularity_score=(
                F('views_count') * 0.3 +  # 30% weight to views
                F('total_sales') * 0.4 +  # 40% weight to sales
                F('average_rating') * 0.3  # 30% weight to ratings
            )
        ).order_by('-popularity_score')[:8]

        serializer = ProductListSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        response_data = serializer.data
        cache.set(cache_key, response_data, CACHE_TTL)
        return Response(response_data)

    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update product stock with validation"""
        product = self.get_object()
        
        try:
            new_stock = int(request.data.get('stock', 0))
            variant_id = request.data.get('variant_id')
            
            if new_stock < 0:
                raise ValueError("Stock cannot be negative")

            if variant_id:
                variant = product.variants.get(id=variant_id)
                if new_stock < variant.reserved_stock:
                    raise ValueError("New stock cannot be less than reserved stock")
                variant.stock = new_stock
                variant.save()
            else:
                product.update_stock(new_stock)
            
            # Clear caches
            cache.delete(get_cache_key('detail', product.id))
            cache.delete_pattern(f'{CACHE_PREFIX}list:*')
            
            serializer = self.get_serializer(product)
            return Response(serializer.data)
            
        except (TypeError, ValueError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Bulk actions with validation and cache management"""
        serializer = ProductBulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        products = Product.objects.filter(
            id__in=serializer.validated_data['product_ids'],
            student__user=request.user
        )

        if not products.exists():
            return Response(
                {'error': 'No valid products found'},
                status=status.HTTP_404_NOT_FOUND
            )

        action = serializer.validated_data['action']
        update_data = {'is_active': action != 'deactivate'}
        products.update(**update_data)

        # Clear caches
        cache.delete_pattern(f'{CACHE_PREFIX}list:*')
        for product in products:
            cache.delete(get_cache_key('detail', product.id))

        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        """Get categories with caching"""
        cache_key = f'{CACHE_PREFIX}categories'
        queryset = cache.get(cache_key)

        if queryset is None:
            queryset = Category.objects.annotate(
                products_count=Count('products', filter=Q(products__is_active=True))
            )
            cache.set(cache_key, queryset, CACHE_TTL)

        return queryset

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Get category products with caching"""
        category = self.get_object()
        cache_key = get_cache_key('category_products', category.id)
        cached_results = cache.get(cache_key)

        if cached_results is not None:
            return Response(cached_results)

        products = Product.objects.filter(
            category=category,
            is_active=True
        ).select_related(
            'student',
            'student__user'
        ).prefetch_related('reviews')

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(
                page,
                many=True,
                context={'request': request}
            )
            response_data = self.get_paginated_response(serializer.data).data
        else:
            serializer = ProductListSerializer(
                products,
                many=True,
                context={'request': request}
            )
            response_data = serializer.data

        cache.set(cache_key, response_data, CACHE_TTL)
        return Response(response_data)
