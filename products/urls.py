from django.urls import path
from . import views

urlpatterns = [
    path('product/<int:id>/<slug:slug>/', views.product, name='product'),
    path('product-list/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('product-detail/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    # other url patterns...
]