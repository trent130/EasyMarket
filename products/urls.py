from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views
from django.conf import settings

app_name = 'products'

router = SimpleRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')
# router.register(r'categories', views.CategoryViewSet, basename='category')

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
#     path('categories/', views.CategoryViewSet.as_view({'get': 'categories'}),
#          name='categories'),
    path('products/my-products/',
         views.ProductViewSet.as_view({'get': 'my_products'}),
         name='my-products'),

    # fetch categories
    path('categories/', views.CategoryViewSet.as_view({'get': 'list'}),
         name='categories'),

    # Category Products
    path('categories/<slug:slug>/products/',
         views.CategoryViewSet.as_view({'get': 'products'}),
         name='category-products'),

    # Related Products
    path('products/<slug:slug>/related/',
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
    path('products/<slug:slug>/reviews/',
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
    path('products/<slug:slug>/images/',
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
    path('products/<slug:slug>/report/',
         views.ProductViewSet.as_view({'post': 'report_product'}),
         name='report-product'),
    path('products/reports/',
         views.ProductViewSet.as_view({'get': 'product_reports'}),
         name='product-reports'),

    # Product Statistics
    path('products/stats/',
         views.ProductViewSet.as_view({'get': 'product_stats'}),
         name='product-stats'),
    path('products/<slug:slug>/stats/',
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

    # Product detail by slug
    path('products/<slug:slug>/', views.ProductViewSet.as_view({'get': 'retrieve'}), name='product-detail'),
]


# Add debug patterns if in debug mode

if settings.DEBUG:
    urlpatterns += [
        # Test endpoints
        path('products/test/create/',
             views.ProductViewSet.as_view({'post': 'test_create'}),
             name='test-create-product'),
        path('products/test/bulk-create/',
             views.ProductViewSet.as_view({'post': 'test_bulk_create'}),
             name='test-bulk-create'),
    ]

'''
#TODO:
# implement a proper categories views instead of the get_queryset or optimize it to be used as such
'''