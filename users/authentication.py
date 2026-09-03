from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

CustomUser = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to fetch the user using either username or email
            user = CustomUser.objects.get(
                Q(username=username) | Q(email=username)
            )
            if self.user_can_authenticate(user) and user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = CustomUser.objects.get(pk=user_id)
            return user if self.user_can_authenticate(user) else None
        except CustomUser.DoesNotExist:
            return None
