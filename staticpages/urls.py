from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('help/', views.help, name='help'),
    path('signin/', auth_views.LoginView.as_view(template_name='staticpages/account/login.html'), name='signin'),
    path('signout/', auth_views.LogoutView.as_view(template_name='staticpages/account/logout.html'), name='signout'),
    path('register/', views.register, name='register'),
    path('search/', views.search, name='search'),
    path('chat/', views.chat, name='chat'),
    # path('chat/<str:room_name>/', views.room, name='room'),
    path('categories/', views.categories, name='categories'),
    path('products/', views.products, name='products'),
    path('orders/', views.orders, name='orders'),
]
