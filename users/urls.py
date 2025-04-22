from django.urls import path, include
from rest_framework.routers import DefaultRouter

# custom imports
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

# Create a router and register our viewset with it.
router = DefaultRouter()
router.register(r'profile', views.UserProfileViewSet, basename='user_profile')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/2fa/enable/', views.enable_2fa, name='enable_2fa'),
    path('auth/2fa/verify/', views.verify_2fa, name='verify_2fa'),
    path('auth/2fa/status/', views.get_2fa_status, name='get_2fa_status'),
    path('auth/2fa/disable/', views.disable_2fa, name='disable_2fa'),
    path('auth/2fa/validate/', views.validate_backup_code, name='validate_backup_code'),
    path('auth/2fa/regenerate/', views.regenerate_backup_codes, name='regenerate_backup_codes'),
    path('auth/signin/', views.signin, name='signin'),
    path('auth/signup/', views.signup, name='signup'),
    path('auth/logout/', views.signout, name='logout'),
    path('auth/forgot-password/', views.forgot_password, name='forgot_password'),
    path('auth/reset-password/', views.reset_password, name='reset_password'),
    path('auth/change-password/', views.change_password, name='change_password'),
]

