from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Avg, Q
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, WishList, Review
from products.models import Product, Category
from .serializers_marketplace import (
    CartSerializer,
    CartItemSerializer,
    WishListSerializer,
    ReviewSerializer,
    CategorySerializer,
    SearchResultSerializer
)
from products.serializers import ProductSerializer
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from django.dispatch import receiver
from users.models import CustomUser

logger = logging.getLogger(__name__)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add item to cart - updates quantity if item already exists"""
        cart = self.get_object()
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response(
                {'error': 'product is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Validate quantity
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {'error': 'quantity must be greater than 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the product
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if item already exists in cart
            existing_item = cart.cartitem_set.filter(product=product).first()

            if existing_item:
                # Update existing item quantity
                existing_item.quantity += quantity

                # Check stock availability
                if existing_item.quantity > product.stock:
                    return Response(
                        {
                            'error': f'Not enough stock. Available: {product.stock}, Requested: {existing_item.quantity}',
                            'available_stock': product.stock,
                            'current_quantity': existing_item.quantity - quantity
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                existing_item.save()
                serializer = CartItemSerializer(existing_item)

                return Response({
                    'message': 'Item quantity updated successfully',
                    'item': serializer.data,
                    'action': 'updated'
                })
            else:
                # Create new cart item
                # Check stock availability
                if quantity > product.stock:
                    return Response(
                        {
                            'error': f'Not enough stock. Available: {product.stock}, Requested: {quantity}',
                            'available_stock': product.stock
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity
                )
                serializer = CartItemSerializer(cart_item)

                return Response({
                    'message': 'Item added to cart successfully',
                    'item': serializer.data,
                    'action': 'created'
                })

        except ValueError:
            return Response(
                {'error': 'Invalid quantity value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            return Response(
                {'error': 'An error occurred while adding item to cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

    @action(detail=False, methods=['post'])
    def add(self, request):
        """Add item to user's cart - updates quantity if item already exists"""
        try:
            # Get or create user's cart
            cart, created = Cart.objects.get_or_create(user=request.user)

            product_id = request.data.get('product_id')
            quantity = request.data.get('quantity', 1)

            if not product_id:
                return Response(
                    {'error': 'product_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate quantity
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    return Response(
                        {'error': 'quantity must be greater than 0'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'Invalid quantity value'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the product
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if item already exists in cart
            existing_item = cart.cartitem_set.filter(product=product).first()

            if existing_item:
                # Update existing item quantity
                new_quantity = existing_item.quantity + quantity

                # Check stock availability
                if new_quantity > product.stock:
                    return Response(
                        {
                            'error': f'Not enough stock. Available: {product.stock}, Current in cart: {existing_item.quantity}, Requested: {quantity}',
                            'available_stock': product.stock,
                            'current_quantity': existing_item.quantity,
                            'requested_quantity': quantity
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                existing_item.quantity = new_quantity
                existing_item.save()
                serializer = CartItemSerializer(existing_item)

                logger.info(f"Updated cart item quantity for user {request.user.username}: Product {product.id}, New quantity: {new_quantity}")

                return Response({
                    'message': 'Item quantity updated successfully',
                    'item': serializer.data,
                    'action': 'updated',
                    'previous_quantity': existing_item.quantity - quantity,
                    'new_quantity': new_quantity
                })
            else:
                # Create new cart item
                # Check stock availability
                if quantity > product.stock:
                    return Response(
                        {
                            'error': f'Not enough stock. Available: {product.stock}, Requested: {quantity}',
                            'available_stock': product.stock
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity
                )
                serializer = CartItemSerializer(cart_item)

                logger.info(f"Added new item to cart for user {request.user.username}: Product {product.id}, Quantity: {quantity}")

                return Response({
                    'message': 'Item added to cart successfully',
                    'item': serializer.data,
                    'action': 'created',
                    'quantity': quantity
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            return Response(
                {'error': 'An error occurred while adding item to cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """Update the quantity of an item in the cart"""
        try:
            # Get user's cart
            try:
                cart = Cart.objects.get(user=request.user)
            except Cart.DoesNotExist:
                return Response(
                    {'error': 'Cart not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            product_id = request.data.get('product_id')
            new_quantity = request.data.get('quantity')

            if not product_id:
                return Response(
                    {'error': 'product_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if new_quantity is None:
                return Response(
                    {'error': 'quantity is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate quantity
            try:
                new_quantity = int(new_quantity)
                if new_quantity < 0:
                    return Response(
                        {'error': 'quantity cannot be negative'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'Invalid quantity value'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the product
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Find the cart item
            try:
                cart_item = cart.cartitem_set.get(product=product)
            except CartItem.DoesNotExist:
                return Response(
                    {'error': 'Item not found in cart'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # If quantity is 0, remove the item
            if new_quantity == 0:
                cart_item.delete()
                return Response({
                    'message': 'Item removed from cart',
                    'action': 'removed',
                    'product_id': product_id
                })

            # Check stock availability
            if new_quantity > product.stock:
                return Response(
                    {
                        'error': f'Not enough stock. Available: {product.stock}, Requested: {new_quantity}',
                        'available_stock': product.stock,
                        'current_quantity': cart_item.quantity
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update quantity
            old_quantity = cart_item.quantity
            cart_item.quantity = new_quantity
            cart_item.save()

            serializer = CartItemSerializer(cart_item)

            logger.info(f"Updated cart item quantity for user {request.user.username}: Product {product.id}, Old: {old_quantity}, New: {new_quantity}")

            return Response({
                'message': 'Item quantity updated successfully',
                'item': serializer.data,
                'action': 'updated',
                'previous_quantity': old_quantity,
                'new_quantity': new_quantity
            })

        except Exception as e:
            logger.error(f"Error updating cart item quantity: {str(e)}")
            return Response(
                {'error': 'An error occurred while updating item quantity'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WishListViewSet(viewsets.ModelViewSet):
    serializer_class = WishListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        logger.info(f"Fetching wishlist for user: {self.request.user}")
        return WishList.objects.filter(user=self.request.user)

    def list(self, request):
        """Get user's wishlist with products and seller information"""
        try:
            wishlist, created = WishList.objects.get_or_create(user=request.user)
            serializer = self.get_serializer(wishlist, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching wishlist: {str(e)}")
            return Response(
                {'error': 'An error occurred while fetching wishlist'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

    @action(detail=False, methods=['post'])
    def add_product(self, request):
        """Add product to user's wishlist by product ID"""
        try:
            # Get or create user's wishlist
            wishlist, created = WishList.objects.get_or_create(user=request.user)

            # Get product ID from request data
            product_id = request.data.get('product_id')
            if not product_id:
                return Response(
                    {'error': 'product_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get product by ID
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if product is already in wishlist
            if wishlist.products.filter(id=product.id).exists():
                return Response(
                    {'message': 'Product already in wishlist'},
                    status=status.HTTP_200_OK
                )

            # Add product to wishlist
            wishlist.products.add(product)

            logger.info(f"Product {product.id} added to wishlist for user {request.user.username}")

            return Response(
                {'message': 'Product added to wishlist successfully'},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error adding product to wishlist: {str(e)}")
            return Response(
                {'error': 'An error occurred while adding product to wishlist'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def add_product_by_slug(self, request, product_slug=None):
        """Add product to user's wishlist by product slug"""
        try:
            # Get or create user's wishlist
            wishlist, created = WishList.objects.get_or_create(user=request.user)

            # Get product by slug
            product = get_object_or_404(Product, slug=product_slug, is_active=True)

            # Check if product is already in wishlist
            if wishlist.products.filter(id=product.id).exists():
                return Response(
                    {'message': 'Product already in wishlist'},
                    status=status.HTTP_200_OK
                )

            # Add product to wishlist
            wishlist.products.add(product)

            logger.info(f"Product {product.slug} added to wishlist for user {request.user.username}")

            return Response(
                {'message': 'Product added to wishlist successfully'},
                status=status.HTTP_200_OK
            )

        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error adding product to wishlist: {str(e)}")
            return Response(
                {'error': 'An error occurred while adding product to wishlist'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def remove_product(self, request):
        """Remove product from user's wishlist by product ID"""
        try:
            # Get user's wishlist
            try:
                wishlist = WishList.objects.get(user=request.user)
            except WishList.DoesNotExist:
                return Response(
                    {'error': 'Wishlist not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get product ID from request data
            product_id = request.data.get('product_id')
            if not product_id:
                return Response(
                    {'error': 'product_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get product by ID
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Remove product from wishlist
            wishlist.products.remove(product)

            logger.info(f"Product {product.id} removed from wishlist for user {request.user.username}")

            return Response(
                {'message': 'Product removed from wishlist successfully'},
                status=status.HTTP_204_NO_CONTENT
            )

        except Exception as e:
            logger.error(f"Error removing product from wishlist: {str(e)}")
            return Response(
                {'error': 'An error occurred while removing product from wishlist'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def remove_product_by_slug(self, request, product_slug=None):
        """Remove product from user's wishlist by product slug"""
        try:
            # Get user's wishlist
            wishlist = WishList.objects.get(user=request.user)

            # Get product by slug
            product = get_object_or_404(Product, slug=product_slug, is_active=True)

            # Remove product from wishlist
            wishlist.products.remove(product)

            logger.info(f"Product {product.slug} removed from wishlist for user {request.user.username}")

            return Response(
                {'message': 'Product removed from wishlist successfully'},
                status=status.HTTP_204_NO_CONTENT
            )

        except WishList.DoesNotExist:
            return Response(
                {'error': 'Wishlist not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error removing product from wishlist: {str(e)}")
            return Response(
                {'error': 'An error occurred while removing product from wishlist'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def check_product(self, request, product_slug=None):
        """Check if a product is in user's wishlist"""
        try:
            # Get user's wishlist
            wishlist = WishList.objects.get(user=request.user)

            # Get product by slug
            product = get_object_or_404(Product, slug=product_slug, is_active=True)

            # Check if product is in wishlist
            is_in_wishlist = wishlist.products.filter(id=product.id).exists()

            return Response({
                'in_wishlist': is_in_wishlist,
                'product_slug': product_slug
            })

        except WishList.DoesNotExist:
            return Response({
                'in_wishlist': False,
                'product_slug': product_slug
            })
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error checking product in wishlist: {str(e)}")
            return Response(
                {'error': 'An error occurred while checking wishlist'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def by_seller(self, request):
        """Get wishlist items grouped by seller"""
        try:
            wishlist, created = WishList.objects.get_or_create(user=request.user)

            # Group products by seller
            sellers_data = {}
            for product in wishlist.products.select_related('student__user').all():
                seller_id = product.student.id
                seller_username = product.student.user.username

                if seller_id not in sellers_data:
                    sellers_data[seller_id] = {
                        'seller': {
                            'id': seller_id,
                            'username': seller_username,
                            'first_name': product.student.user.first_name,
                            'last_name': product.student.user.last_name,
                            'email': product.student.user.email,
                            'date_joined': product.student.user.date_joined,
                        },
                        'products': []
                    }

                # Add product data
                product_data = {
                    'id': product.id,
                    'title': product.title,
                    'slug': product.slug,
                    'price': product.price,
                    'condition': product.condition,
                    'image_url': request.build_absolute_uri(product.image.url) if product.image else None,
                    'category_name': product.category.name,
                    'created_at': product.created_at,
                    'available_stock': product.stock - product.reserved_stock,
                }

                sellers_data[seller_id]['products'].append(product_data)

            # Convert to list format
            result = {
                'sellers': list(sellers_data.values()),
                'total_sellers': len(sellers_data),
                'total_products': wishlist.products.count()
            }

            return Response(result)

        except Exception as e:
            logger.error(f"Error fetching wishlist by seller: {str(e)}")
            return Response(
                {'error': 'An error occurred while fetching wishlist by seller'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
        category_ids = products.values_list('category', flat=True).distinct()
        categories = Category.objects.filter(
            id__in=category_ids
        ).annotate(
            product_count=Count('products', filter=Q(products__id__in=products.values_list('id', flat=True)))
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

