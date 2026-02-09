from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'admin'


class IsStudent(permissions.BasePermission):
    """Allow access only to student users"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'student'


class IsCustomer(permissions.BasePermission):
    """Allow access only to customer users"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'customer'


class IsStudentOrAdmin(permissions.BasePermission):
    """Allow access to students and admins (sellers)"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type in ['student', 'admin']


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access to object owner or admin"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'admin':
            return True
        # Check if object has user or student field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'student') and hasattr(request.user, 'student'):
            return obj.student == request.user.student
        return False
