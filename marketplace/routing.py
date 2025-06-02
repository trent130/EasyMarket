# routing.py
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from . import consumers

from django.urls import re_path
# from .consumers import SimpleConsumer

# WebSocket URL patterns
websocket_urlpatterns = [
    re_path(r'^ws/$', consumers.MarketplaceConsumer.as_asgi()),  # Default WebSocket route
    re_path(r'^ws/marketplace/$', consumers.MarketplaceConsumer.as_asgi()),
    re_path(r'^ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
