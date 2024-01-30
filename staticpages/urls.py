from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('help/', views.help, name='help'),
    path('signin/', views.signin, name='signin'),
    path('register/', views.register, name='register'),
    path('search/', views.search, name='search'),
    path('chat/', views.chat, name='chat'),
    # path('chat/<str:room_name>/', views.room, name='room'),
    path('categories/', views.categories, name='categories'),
    path('products/', views.products, name='products'),
    path('orders/', views.orders, name='orders'),
]
