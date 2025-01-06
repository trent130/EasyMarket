from marketplace.consumers import ChatConsumer, MarketplaceConsumer
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views_marketplace

router = DefaultRouter()
router.register(r'cart', views_marketplace.CartViewSet, basename='cart')
router.register(r'wishlist', views_marketplace.WishListViewSet, basename='wishlist')
router.register(r'reviews', views_marketplace.ReviewViewSet, basename='review')

urlpatterns = [
    # Router URLs
    path('api/', include(router.urls)),

    # Cart operations
    path('api/cart/<int:cart_id>/add/', 
         views_marketplace.CartViewSet.as_view({'post': 'add_item'}),
         name='cart-add-item'),
    path('api/cart/<int:cart_id>/remove/',
         views_marketplace.CartViewSet.as_view({'post': 'remove_item'}),
         name='cart-remove-item'),
    path('api/cart/<int:cart_id>/clear/',
         views_marketplace.CartViewSet.as_view({'post': 'clear'}),
         name='cart-clear'),

    # Wishlist operations
    path('api/wishlist/<int:wishlist_id>/add/',
         views_marketplace.WishListViewSet.as_view({'post': 'add_product'}),
         name='wishlist-add-product'),
    path('api/wishlist/<int:wishlist_id>/remove/',
         views_marketplace.WishListViewSet.as_view({'post': 'remove_product'}),
         name='wishlist-remove-product'),

    # Search and recommendations
    path('api/search/',
         views_marketplace.SearchView.as_view(),
         name='search'),
    path('api/recommendations/',
         views_marketplace.get_recommendations,
         name='recommendations'),

    # Reviews
    path('api/products/<int:product_id>/reviews/',
         views_marketplace.ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='product-reviews'),
    path('api/reviews/<int:pk>/',
         views_marketplace.ReviewViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         }),
         name='review-detail'),
]

# to be rremoved all because it is not being needed anymore
websocket_urlpatterns = [
    path('ws/chat/', ChatConsumer.as_asgi()),
    path('ws/marketplace/', MarketplaceConsumer.as_asgi()),  # New WebSocket route
]
