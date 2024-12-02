from django.http import JsonResponse
from django.urls import resolve
from .models import Student

class TwoFactorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Routes that require 2FA when enabled
        self.protected_paths = [
            '/api/orders/',
            '/api/payment/',
            '/api/profile/',
            '/api/settings/',
        ]

    def __call__(self, request):
        # Skip middleware for non-authenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Skip middleware for 2FA-related endpoints to avoid circular dependencies
        current_path = resolve(request.path_info).route
        if current_path.startswith('api/auth/2fa'):
            return self.get_response(request)

        # Check if path requires 2FA
        if any(request.path.startswith(path) for path in self.protected_paths):
            try:
                student = Student.objects.get(user=request.user)
                # If 2FA is enabled but not verified, block access
                if student.two_factor_enabled and not student.two_factor_verified:
                    return JsonResponse({
                        'error': 'Two-factor authentication required',
                        'code': '2FA_REQUIRED'
                    }, status=403)
            except Student.DoesNotExist:
                return JsonResponse({
                    'error': 'Student profile not found',
                    'code': 'PROFILE_NOT_FOUND'
                }, status=404)

        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Additional view-specific checks can be added here
        return None
