from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views.auth import UserViewSet, CustomUserViewSet
from .views.marketplace import (
    StudentViewSet, UserProfileViewSet, MessageViewSet,
    ReactionViewSet, ReviewViewSet, CartViewSet, WishListViewSet
)
from .views.products import CategoryViewSet, ProductViewSet
from .views.orders import OrderViewSet, OrderItemViewSet, ShippingAddressViewSet

# Create a router and register our viewsets
router = DefaultRouter()

# Auth routes
router.register(r'users', UserViewSet)
router.register(r'custom-users', CustomUserViewSet)

# Marketplace routes
router.register(r'students', StudentViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'reactions', ReactionViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'wishlists', WishListViewSet, basename='wishlist')

# Product routes
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

# Order routes
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='orderitem')
router.register(r'shipping-addresses', ShippingAddressViewSet, basename='shippingaddress')

urlpatterns = [
    # JWT Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints
    path('', include(router.urls)),
]
