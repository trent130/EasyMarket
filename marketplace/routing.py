# # routing.py
# from django.urls import path
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from marketplace.consumers import ChatConsumer

from django.urls import re_path
from .consumers import ChatConsumer, MarketplaceConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<product_id>\d+)/(?P<seller_id>\d+)/$',  ChatConsumer.as_asgi()),
    re_path(r'ws/marketplace/$', MarketplaceConsumer.as_asgi()),  # New WebSocket route
]

# application = ProtocolTypeRouter({
#     'websocket': AuthMiddlewareStack(
#         URLRouter(
#             websocket_urlpatterns
#         )
#     ),
# })
