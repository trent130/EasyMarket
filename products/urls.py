from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

app_name = 'products'

router = SimpleRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    # Explicit patterns MUST come before router URLs to avoid conflicts

    # fetch categories
    path('categories/', views.CategoryViewSet.as_view({'get': 'list'}),
         name='categories'),

     # Product conditions endpoint
    path('products/conditions/', views.ProductViewSet.as_view({'get': 'conditions'}),
         name='product-conditions'),

    # Featured and Trending products - MUST come before router patterns
    path('products/featured/', views.ProductViewSet.as_view({'get': 'featured'}),
         name='products-featured'),
    path('products/trending/', views.ProductViewSet.as_view({'get': 'trending'}),
         name='products-trending'),

    # Product Search and Filtering
    path('products/search/',
         views.ProductViewSet.as_view({'get': 'search'}),
         name='product-search'),

    # Product Management
    path('products/bulk-action/',
         views.ProductViewSet.as_view({'post': 'bulk_action'}),
         name='product-bulk-action'),

    path('products/my-products/',
         views.ProductViewSet.as_view({'get': 'my_products'}),
         name='my-products'),

    # Category Products
    path('categories/<slug:slug>/products/',
         views.CategoryViewSet.as_view({'get': 'products'}),
         name='category-products'),

    # Product Validation
    path('products/validate/',
         views.ProductViewSet.as_view({'post': 'validate_product'}),
         name='validate-product'),

    # Draft Management URLs
    path('products/my-products/validate/',
         views.ProductViewSet.as_view({'post': 'validate_product'}),
         name='my-products-validate'),
    path('products/my-products/draft/',
         views.ProductViewSet.as_view({'post': 'save_draft'}),
         name='my-products-save-draft'),
    path('products/my-products/draft/<int:pk>/',
         views.ProductViewSet.as_view({
             'get': 'manage_draft',
             'patch': 'manage_draft',
             'delete': 'manage_draft'
         }),
         name='my-products-manage-draft'),
    path('products/my-products/draft/<int:pk>/publish/',
         views.ProductViewSet.as_view({'post': 'publish_draft'}),
         name='my-products-publish-draft'),

    # Image Management URLs
    path('products/my-products/upload-image/',
         views.ProductViewSet.as_view({'post': 'upload_image'}),
         name='my-products-upload-image'),
    path('products/my-products/delete-image/',
         views.ProductViewSet.as_view({'delete': 'delete_image'}),
         name='my-products-delete-image'),

    # Product by slug (custom pattern) - MUST come before router URLs
    path('products/slug/<slug:slug>/', views.ProductViewSet.as_view({'get': 'retrieve_by_slug'}), name='product-detail-by-slug'),

    # Router URLs - placed here to handle standard CRUD operations
    path('', include(router.urls)),
]
