from django.urls import path, include
from rest_framework.routers import DefaultRouter

from marketplace.consumers import MarketplaceConsumer
from . import views_marketplace


# Create a router and register our viewset with it.
router = DefaultRouter()
router.register(r'cart', views_marketplace.CartViewSet, basename='cart')
router.register(r'wishlist', views_marketplace.WishListViewSet, basename='wishlist')
router.register(r'reviews', views_marketplace.ReviewViewSet, basename='review')

# WebSocket URL patterns
websocket_urlpatterns = [
    path('ws/marketplace/', MarketplaceConsumer.as_asgi()),
]

urlpatterns = [
     # Router URLs
     path('', include(router.urls)),

     # Cart operations
     path('cart/<int:cart_id>/add/',
          views_marketplace.CartViewSet.as_view({'post': 'add_item'}),
          name='cart-add-item'),
     path('cart/<int:cart_id>/remove/',
          views_marketplace.CartViewSet.as_view({'post': 'remove_item'}),
          name='cart-remove-item'),
     path('cart/<int:cart_id>/clear/',
          views_marketplace.CartViewSet.as_view({'post': 'clear'}),
          name='cart-clear'),

         
     # Wishlist operations
     path('wishlist', 
          views_marketplace.WishListViewSet.as_view({'get': 'get_queryset'}),
          name='wishlist'),
     path('wishlist/<int:wishlist_id>/add/',
          views_marketplace.WishListViewSet.as_view({'post': 'add_product'}),
          name='wishlist-add-product'),
     path('wishlist/<int:wishlist_id>/remove/',
          views_marketplace.WishListViewSet.as_view({'post': 'remove_product'}),
          name='wishlist-remove-product'),

     # Search and recommendations
     path('search/',
          views_marketplace.SearchView.as_view(),
          name='search'),
     path('recommendations/',
          views_marketplace.get_recommendations,
          name='recommendations'),

     # Reviews
     path('products/<int:product_id>/reviews/',
          views_marketplace.ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
          name='product-reviews'),
     path('reviews/<int:pk>/',
          views_marketplace.ReviewViewSet.as_view({
               'get': 'retrieve',
               'put': 'update',
               'patch': 'partial_update',
               'delete': 'destroy'
          }),
          name='review-detail'),
]

