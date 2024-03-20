from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from products.views import add_category

app_name = 'marketplace'

urlpatterns = [
    # path('', views.index, name='home'),
    # path('chat_room/<int:room_id>/', views.chat_room, name='chat_room'),
    # path('typing_status/', views.typing_status, name='typing_status'),
    path('checkout', views.checkout, name='checkout' ),
    path('clear_cart', views.clear_cart, name='clear_cart'),
    path('cart/', views.cart, name='cart'),
    path('cart_cleared/', views.cart_cleared, name='cart_cleared'),
]