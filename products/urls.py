from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings

app_name = 'products'

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Product Search and Filtering
    path('products/search/',
         views.ProductViewSet.as_view({'get': 'search'}),
         name='product-search'),

    # Product Management
    path('products/bulk-action/',
         views.ProductViewSet.as_view({'post': 'bulk_action'}),
         name='product-bulk-action'),

    # fetch categories
    path('categories/', views.CategoryViewSet.as_view({'get': 'categories'}),
         name='categories'),
    path('products/my-products/',
         views.ProductViewSet.as_view({'get': 'my_products'}),
         name='my-products'),

    # Category Products
    path('categories/<slug:slug>/products/',
         views.CategoryViewSet.as_view({'get': 'products'}),
         name='category-products'),

    # Related Products
    path('products/<int:pk>/related/',
         views.ProductViewSet.as_view({'get': 'related'}),
         name='related-products'),

    # Product Analytics
    path('products/analytics/',
         views.ProductViewSet.as_view({'get': 'analytics'}),
         name='product-analytics'),
    path('products/analytics/export/',
         views.ProductViewSet.as_view({'get': 'export_analytics'}),
         name='export-product-analytics'),

    # Product Reviews
    path('products/<int:pk>/reviews/',
         views.ProductViewSet.as_view({
             'get': 'reviews',
             'post': 'add_review'
         }),
         name='product-reviews'),
    path('products/reviews/<int:review_id>/',
         views.ProductViewSet.as_view({
             'put': 'update_review',
             'delete': 'delete_review'
         }),
         name='review-detail'),

    # Product Images
    path('products/<int:pk>/images/',
         views.ProductViewSet.as_view({
             'post': 'upload_images',
             'delete': 'delete_images'
         }),
         name='product-images'),

    # Product Categories
    path('categories/tree/',
         views.CategoryViewSet.as_view({'get': 'tree'}),
         name='category-tree'),
    path('categories/featured/',
         views.CategoryViewSet.as_view({'get': 'featured'}),
         name='featured-categories'),

    # Product Reports
    path('products/<int:pk>/report/',
         views.ProductViewSet.as_view({'post': 'report_product'}),
         name='report-product'),
    path('products/reports/',
         views.ProductViewSet.as_view({'get': 'product_reports'}),
         name='product-reports'),

    # Product Statistics
    path('products/stats/',
         views.ProductViewSet.as_view({'get': 'product_stats'}),
         name='product-stats'),
    path('products/<int:pk>/stats/',
         views.ProductViewSet.as_view({'get': 'single_product_stats'}),
         name='single-product-stats'),

    # Product Export/Import
    path('products/export/',
         views.ProductViewSet.as_view({'get': 'export_products'}),
         name='export-products'),
    path('products/import/',
         views.ProductViewSet.as_view({'post': 'import_products'}),
         name='import-products'),

    # Product Validation
    path('products/validate/',
         views.ProductViewSet.as_view({'post': 'validate_product'}),
         name='validate-product'),

    # New URL for retrieving product by slug
    path('products/<slug:slug>/', views.ProductViewSet.as_view({'get': 'retrieve'}), name='product-detail'),
]


# Add debug patterns if in debug mode

if settings.DEBUG:
    urlpatterns += [
        # Test endpoints
        path('api/products/test/create/',
             views.ProductViewSet.as_view({'post': 'test_create'}),
             name='test-create-product'),
        path('api/products/test/bulk-create/',
             views.ProductViewSet.as_view({'post': 'test_bulk_create'}),
             name='test-bulk-create'),
    ]
