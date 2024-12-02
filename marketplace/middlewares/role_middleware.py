from django.http import HttpResponseForbidden

class RoleMiddleware:
    def __init__(self, get_responsse):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.path.startswith('/admin/') and not request.user.is_admin:
                return HttpResponseForbidden("You don't have permission to access this page.")

        """ response = self.get_response(request) """

