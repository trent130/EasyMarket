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
     # Router URLs
     path('api/', include(router.urls)),

     # Authentication endpoints
     path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('signin/', views.signin, name='signin'),
     path('signup/', views.signup, name='signup'),
     path('logout/', views.signout, name='logout'),
     
     # User profile endpoints
     path('me/', views.get_current_user, name='get_current_user'),
     path('student-profile/', views.update_student_profile, name='update_student_profile'),
     
     # Two-factor authentication endpoints
     path('enable-2fa/', views.enable_2fa, name='enable_2fa'),
     path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
     path('2fa-status/', views.get_2fa_status, name='get_2fa_status'),
     path('disable-2fa/', views.disable_2fa, name='disable_2fa'),
     path('validate-2fa/', views.validate_backup_code, name='validate_backup_code'),
     path('regenerate-2-fa/', views.regenerate_backup_codes, name='regenerate_backup_codes'),
     
     # Password reset endpoints
     path('forgot_password/', views.forgot_password, name='forgot_password'),
     path('reset_password/', views.reset_password, name="reset_password"),

    # user profile
    path('api/profile/<int:pk>/',
        views.UserProfileViewSet.as_view({'get': 'view profile'}),
        name='user_profile'),
]

