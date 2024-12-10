from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import models
from django.db.models import Count, Avg, Q
from .models import Cart, CartItem, WishList, Review, Student
from products.models import Product
from .serializers_marketplace import (
    CartSerializer,
    CartItemSerializer,
    WishListSerializer,
    ReviewSerializer,
    ProductSerializer,
    CategorySerializer,
    SearchResultSerializer
)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(cart=cart)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item_id')
        try:
            item = cart.cartitem_set.get(id=item_id)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        cart = self.get_object()
        cart.cartitem_set.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class WishListViewSet(viewsets.ModelViewSet):
    serializer_class = WishListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WishList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        wishlist = self.get_object()
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
            wishlist.products.add(product)
            return Response(status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_product(self, request, pk=None):
        wishlist = self.get_object()
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
            wishlist.products.remove(product)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(
            Q(reviewer=self.request.user) |
            Q(product__student__user=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

class SearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        category = request.query_params.get('category')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        sort_by = request.query_params.get('sort_by', 'relevance')

        # Base query
        products = Product.objects.all()

        # Apply filters
        if query:
            products = products.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

        if category:
            products = products.filter(category=category)

        if min_price:
            products = products.filter(price__gte=min_price)

        if max_price:
            products = products.filter(price__lte=max_price)

        # Apply sorting
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'newest':
            products = products.order_by('-created_at')

        # Get category aggregations
        categories = Product.objects.filter(
            id__in=products.values_list('id', flat=True)
        ).values('category').annotate(
            product_count=Count('id')
        )

        # Get price range
        price_range = {
            'min': products.order_by('price').first().price if products else 0,
            'max': products.order_by('-price').first().price if products else 0
        }

        serializer = SearchResultSerializer({
            'products': products,
            'total_results': products.count(),
            'categories': categories,
            'price_range': price_range
        })

        return Response(serializer.data)

@api_view(['GET'])
def get_recommendations(request):
    """Get product recommendations based on user's history"""
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Get user's purchase history and preferences
    user_categories = set(
        Product.objects.filter(
            cartitem__cart__user=request.user
        ).values_list('category', flat=True)
    )

    # Get recommended products
    recommended = Product.objects.filter(
        category__in=user_categories
    ).exclude(
        cartitem__cart__user=request.user
    ).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating')[:10]

    serializer = ProductSerializer(recommended, many=True)
    return Response(serializer.data)
