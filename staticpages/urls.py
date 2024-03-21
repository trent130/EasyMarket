from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('help/', views.help, name='help'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signin/', auth_views.LoginView.as_view(template_name='staticpages/account/login.html'), name='signin'),
    path('signout/', auth_views.LogoutView.as_view(template_name='staticpages/account/logout.html'), name='signout'),
    path('cart/', views.cart, name='cart'),
    path('register/', views.register, name='register'),
    path('search/', views.search, name='search'),
    path('chat/', views.chat, name='chat'),
    path('orders/', views.orders, name='orders'),
    path('account/profile/', views.user_profile, name='user_profile'),
    path('password-change/', auth_views.PasswordResetView.as_view(template_name='staticpages/registration/password_change_form.html'), name='password_reset'),
    path('password-change/done', auth_views.PasswordChangeDoneView.as_view(template_name='staticpages/registration/password_change_done.html'), name='password_change_done'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name = 'password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name = 'password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name = 'password_reset_confirm'),
    path('add_category/', views.add_category, name='add_category'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name = 'password_reset_completee'), path('add_category/', views.add_category, name='add_category'),
]

    