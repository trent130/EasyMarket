from django.urls import path, include
from rest_framework.routers import SimpleRouter

from marketplace.consumers import MarketplaceConsumer
from . import views_marketplace
from . import views_textbooks


# Create a router and register our viewset with it.
router = SimpleRouter()
router.register(r'cart', views_marketplace.CartViewSet, basename='cart')
router.register(r'reviews', views_marketplace.ReviewViewSet, basename='review')
router.register(r'textbooks', views_textbooks.TextbookViewSet, basename='textbook')

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

         
     # Wishlist CRUD operations (replacing router functionality)
     path('wishlist/',
          views_marketplace.WishListViewSet.as_view({
              'get': 'list',
              'post': 'create'
          }),
          name='wishlist-list'),
     path('wishlist/<int:pk>/',
          views_marketplace.WishListViewSet.as_view({
              'get': 'retrieve',
              'put': 'update',
              'patch': 'partial_update',
              'delete': 'destroy'
          }),
          name='wishlist-detail'),

     # Simple wishlist operations (no wishlist ID required)
     path('wishlist/add/',
          views_marketplace.WishListViewSet.as_view({'post': 'add_product'}),
          name='wishlist-add'),
     path('wishlist/remove/',
          views_marketplace.WishListViewSet.as_view({'post': 'remove_product'}),
          name='wishlist-remove'),
     path('wishlist/by-seller/',
          views_marketplace.WishListViewSet.as_view({'get': 'by_seller'}),
          name='wishlist-by-seller'),


     # Legacy wishlist operations (with wishlist ID)
     path('wishlist/<int:wishlist_id>/add/',
          views_marketplace.WishListViewSet.as_view({'post': 'add_product'}),
          name='wishlist-add-product'),
     path('wishlist/<int:wishlist_id>/remove/',
          views_marketplace.WishListViewSet.as_view({'post': 'remove_product'}),
          name='wishlist-remove-product'),

     # Wishlist operations by product slug (for frontend convenience)
     path('wishlist/<slug:product_slug>/add/',
          views_marketplace.WishListViewSet.as_view({'post': 'add_product_by_slug'}),
          name='wishlist-add-product-by-slug'),
     path('wishlist/<slug:product_slug>/remove/',
          views_marketplace.WishListViewSet.as_view({'post': 'remove_product_by_slug'}),
          name='wishlist-remove-product-by-slug'),
     path('wishlist/<slug:product_slug>/check/',
          views_marketplace.WishListViewSet.as_view({'get': 'check_product'}),
          name='wishlist-check-product'),

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

