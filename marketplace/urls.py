from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views_marketplace
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views_auth
from . import consumers

# Create a router and register our viewset with it.
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

     path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('enable-2fa/', views_auth.enable_2fa, name='enable_2fa'),
     path('verify-2fa/', views_auth.verify_2fa, name='verify_2fa'),
     path('2fa-status/', views_auth.get_2fa_status, name='get_2fa_status'),
     path('disable-2fa/', views_auth.disable_2fa, name='disable_2fa'),
     path('validate-2fa/', views_auth.validate_backup_code, name='validate_backup_code'),
     path('regenerate-2-fa/', views_auth.regenerate_backup_codes, name='regenerate_backup_codes'),
     # path('2fa-setup/', views.setup_2fa, name='setup_2fa'),
     path('signin/', views_auth.signin, name='signin'),
     path('signup/', views_auth.signup, name='signup'),
     path('logout/', views_auth.logout, name='logout'),
     path('forgot_password/', views_auth.forgot_password, name='forgot_password'),
    
]

# URL patterns for authentication views are in urls.py
# URL patterns for product views are in products/urls.py
# urlpatterns = [
#     # JWT Authentication endpoints

#     # API endpoints
#     path('', include(router.urls)),
# ]

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/marketplace/$', consumers.MarketplaceConsumer.as_asgi()),  # New WebSocket route
]
