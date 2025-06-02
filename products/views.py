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
    CategorySerializer,
    ProductDraftSerializer,
    ProductValidationSerializer,
    ImageUploadSerializer
)
from .search import search_products
from users.models import Student
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
            avg_rating=Avg('reviews__rating')
        )

        return queryset

    def increment_views(self, product, request):
        from django.core.cache import cache

        """
        Increment product view count with rate limiting
        """
        # Check if the view has been recently incremented (e.g., within the last minute)
        cache_key = f'product_view_{product.id}_{request.user.id}'
        if not cache.get(cache_key):
            Product.objects.filter(id=product.id).update(views_count=F('views_count') + 1)
            # cache to prevent frequent updates
            cache.set(cache_key, True, 3600)  # 1 hour cooldown per user

    def get_object(self):
        """Get single object with slug support"""
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]

        logger.debug(f"Looking up product with value: {lookup_value}")

        # Try to get by slug first, then by ID
        from django.http import Http404

        try:
            if lookup_value.isdigit():
                # If it's a number, try ID first
                logger.debug(f"Trying ID lookup for: {lookup_value}")
                product = get_object_or_404(Product, id=lookup_value, is_active=True)
            else:
                # If it's not a number, treat as slug
                logger.debug(f"Trying slug lookup for: {lookup_value}")
                product = get_object_or_404(Product, slug=lookup_value, is_active=True)

            logger.debug(f"Found product: {product.title} (slug: {product.slug})")
            return product

        except Http404:
            logger.error(f"Product not found for {lookup_value}")
            # If slug lookup fails and it's not a digit, try as ID anyway
            if not lookup_value.isdigit():
                try:
                    logger.debug(f"Fallback: trying ID lookup for non-digit: {lookup_value}")
                    return get_object_or_404(Product, id=int(lookup_value), is_active=True)
                except (ValueError, Http404):
                    logger.error(f"Fallback also failed for {lookup_value}")
                    pass
            raise Product.DoesNotExist(f"Product with identifier '{lookup_value}' not found")

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a product with caching and view count increment"""
        try:
            # Get the lookup value
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            lookup_value = self.kwargs.get(lookup_url_kwarg)

            logger.debug(f"retrieve() called with lookup_value: {lookup_value}")

            if not lookup_value:
                logger.error("No lookup value found in kwargs")
                return Response({
                    'detail': 'Product identifier not provided'
                }, status=status.HTTP_400_BAD_REQUEST)

            cache_key = get_cache_key('detail', lookup_value)
            cached_results = cache.get(cache_key)

            if cached_results is not None:
                logger.debug(f"Returning cached product data for: {lookup_value}")
                return Response(cached_results)

            # Get product
            product = self.get_object()

            # Increment views count
            product.increment_views()

            # Serialize the product
            serializer = self.get_serializer(product)

            # Cache the serialized data for 1 hour
            logger.debug(f"Caching product data for: {lookup_value}")
            cache.set(cache_key, serializer.data, timeout=3600)

            return Response(serializer.data)

        except Product.DoesNotExist:
            lookup_value = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field, 'unknown')
            logger.warning(f"Product not found for: {lookup_value}")
            return Response({
                'detail': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            lookup_value = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field, 'unknown')
            logger.error(f"Error retrieving product {lookup_value}: {str(e)}")
            return Response({
                'detail': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve_by_slug(self, request, slug=None):
        """
        Retrieve a product by its slug with caching
        This method is called directly from URL patterns, not as a DRF action
        """
        try:
            cache_key = get_cache_key('detail', slug)
            cached_results = cache.get(cache_key)

            if cached_results is not None:
                logger.debug(f"Returning cached product data for slug: {slug}")
                return Response(cached_results)

            # Get product by slug
            product = get_object_or_404(Product, slug=slug, is_active=True)

            # Increment views count
            product.increment_views()

            # Serialize the product
            serializer = ProductDetailSerializer(product, context={'request': request})

            # Cache the serialized data for 1 hour
            logger.debug(f"Caching product data for slug: {slug}")
            cache.set(cache_key, serializer.data, timeout=3600)

            return Response(serializer.data)

        except Product.DoesNotExist:
            logger.warning(f"Product not found for slug: {slug}")
            return Response({
                'detail': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Log the error
            logger.error(f"Error retrieving product by slug {slug}: {str(e)}")
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
        product.reviews.count()
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
        try:
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

        except Exception as e:
            logger.error(f"Error in featured products: {str(e)}")
            return Response({
                'detail': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending products based on views, sales and ratings"""
        try:
            cache_key = get_cache_key('trending', '')
            cached_results = cache.get(cache_key)

            if cached_results is not None:
                return Response(cached_results)

            # Simple approach: get products with high view counts and sales
            # Order by a combination of views and sales
            queryset = self.get_queryset().filter(
                stock__gt=F('reserved_stock')
            ).order_by('-views_count', '-total_sales')[:8]

            serializer = ProductListSerializer(
                queryset,
                many=True,
                context={'request': request}
            )
            response_data = serializer.data
            cache.set(cache_key, response_data, CACHE_TTL)
            return Response(response_data)

        except Exception as e:
            logger.error(f"Error in trending products: {str(e)}")
            return Response({
                'detail': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    @action(detail=False, methods=['get'])
    def my_products(self, request):
        """Get current user's products including drafts"""
        try:
            student = Student.objects.get(user=request.user)
            queryset = self.get_queryset().filter(student=student)

            # Filter by draft status if specified
            is_draft = request.query_params.get('is_draft')
            if is_draft is not None:
                queryset = queryset.filter(is_draft=is_draft.lower() == 'true')

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
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def validate_product(self, request):
        """Validate product data before saving"""
        serializer = ProductValidationSerializer(data=request.data)
        if serializer.is_valid():
            validation_result = serializer.validated_data
            return Response(validation_result)
        else:
            return Response({
                'is_valid': False,
                'errors': serializer.errors,
                'warnings': [],
                'data': request.data
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='draft')
    def save_draft(self, request):
        """Save product as draft"""
        serializer = ProductDraftSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                ProductDraftSerializer(product, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'patch', 'delete'], url_path='draft')
    def manage_draft(self, request, pk=None):
        """Get, update, or delete a draft"""
        try:
            student = Student.objects.get(user=request.user)
            product = get_object_or_404(
                Product,
                id=pk,
                student=student,
                is_draft=True
            )

            if request.method == 'GET':
                serializer = ProductDraftSerializer(
                    product,
                    context={'request': request}
                )
                return Response(serializer.data)

            elif request.method == 'PATCH':
                serializer = ProductDraftSerializer(
                    product,
                    data=request.data,
                    partial=True,
                    context={'request': request}
                )
                if serializer.is_valid():
                    product = serializer.save()
                    return Response(
                        ProductDraftSerializer(product, context={'request': request}).data
                    )
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            elif request.method == 'DELETE':
                product.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='draft/publish')
    def publish_draft(self, request, pk=None):
        """Publish a draft product"""
        try:
            student = Student.objects.get(user=request.user)
            product = get_object_or_404(
                Product,
                id=pk,
                student=student,
                is_draft=True
            )

            # Validate that the product has all required fields for publishing
            validation_data = {
                'title': product.title,
                'description': product.description,
                'price': product.price,
                'category': product.category.id if product.category else None,
                'condition': product.condition,
                'stock': product.stock
            }

            validator = ProductValidationSerializer(data=validation_data)
            if validator.is_valid():
                validation_result = validator.validated_data
                if validation_result['is_valid']:
                    # Publish the product
                    product.is_draft = False
                    product.save()

                    # Clear caches
                    cache.delete_pattern(f'{CACHE_PREFIX}list:*')

                    return Response(
                        ProductDetailSerializer(product, context={'request': request}).data,
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response({
                        'error': 'Product validation failed',
                        'validation_errors': validation_result['errors']
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'error': 'Product validation failed',
                    'validation_errors': validator.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'], url_path='upload-image')
    def upload_image(self, request):
        """Upload product image"""
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']

            # Create a temporary product to save the image
            # In a real implementation, you might want to save images separately
            # and associate them with products later
            try:
                student = Student.objects.get(user=request.user)

                # Save the image to media directory
                import os
                from django.core.files.storage import default_storage
                from django.core.files.base import ContentFile
                import uuid

                # Generate unique filename
                file_extension = os.path.splitext(image.name)[1]
                unique_filename = f"product_images/{uuid.uuid4()}{file_extension}"

                # Save the file
                file_path = default_storage.save(unique_filename, ContentFile(image.read()))
                file_url = default_storage.url(file_path)

                # Return the URL
                return Response({
                    'url': request.build_absolute_uri(file_url)
                }, status=status.HTTP_201_CREATED)

            except Student.DoesNotExist:
                return Response(
                    {'error': 'Student profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path='delete-image')
    def delete_image(self, request):
        """Delete product image"""
        image_url = request.data.get('image_url')
        if not image_url:
            return Response(
                {'error': 'image_url is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from django.core.files.storage import default_storage
            from urllib.parse import urlparse
            import os

            # Extract file path from URL
            parsed_url = urlparse(image_url)
            file_path = parsed_url.path

            # Remove leading slash and media prefix if present
            if file_path.startswith('/'):
                file_path = file_path[1:]
            if file_path.startswith('media/'):
                file_path = file_path[6:]

            # Delete the file if it exists
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': 'Image not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            logger.error(f"Error deleting image: {str(e)}")
            return Response(
                {'error': 'Failed to delete image'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
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
