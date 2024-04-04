from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'marketplace'

urlpatterns = [
    # path('', views.index, name='home'),
    # path('chat_room/<int:room_id>/', views.chat_room, name='chat_room'),
    # path('typing_status/', views.typing_status, name='typing_status'),
    path('checkout', views.checkout, name='checkout' ),
    path('clear_cart', views.clear_cart, name='clear_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart_cleared/', views.cart_cleared, name='cart_cleared'),
    path('search/', views.search, name='search')
]