from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model


class PersistentAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Get the user from the session
        scope['user'] = await self.get_user(scope)
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, scope):
        from django.contrib.sessions.backends.db import SessionStore
        
        # Retrieve session key from cookies
        session_key = scope.get('cookies', {}).get('sessionid')
        
        if not session_key:
            return AnonymousUser()
        
        # Recreate the session
        session = SessionStore(session_key)
        
        # Retrieve user ID from session
        user_id = session.get('_auth_user_id')
        
        if user_id:
            User = get_user_model()
            try:
                return User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return AnonymousUser()
        
        return AnonymousUser()

