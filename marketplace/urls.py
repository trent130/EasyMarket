from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('search/', views.search, name='search'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('clear_cart', views.clear_cart, name="clear_cart"),
    path('update_cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
]