import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

class BaseConsumer(AsyncWebsocketConsumer):
    """Base consumer with common functionality"""
    
    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser())
        await self.accept()
    
    async def disconnect(self, close_code):
        # Clean up logic here
        pass
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            await self.process_message(data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
    
    async def process_message(self, data):
        """Override this method in child classes"""
        pass
    
    async def send_json(self, data):
        await self.send(text_data=json.dumps(data))


class MarketplaceConsumer(BaseConsumer):
    """Consumer for marketplace real-time updates"""
    
    async def connect(self):
        await super().connect()
        self.room_group_name = 'marketplace_updates'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def process_message(self, data):
        message_type = data.get('type')
        
        if message_type == 'product_update':
            # Handle product update
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'product_update',
                    'product_id': data.get('product_id'),
                    'action': data.get('action'),
                    'data': data.get('data')
                }
            )
    
    async def product_update(self, event):
        """Send product update to WebSocket"""
        await self.send_json({
            'type': 'product_update',
            'product_id': event['product_id'],
            'action': event['action'],
            'data': event['data']
        })


class ChatConsumer(BaseConsumer):
    """Consumer for chat functionality"""
    
    async def connect(self):
        await super().connect()
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def process_message(self, data):
        message = data.get('message', '')
        
        # Store message in database
        if self.user.is_authenticated:
            await self.save_message(message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username if self.user.is_authenticated else 'Anonymous'
            }
        )
    
    async def chat_message(self, event):
        """Send message to WebSocket"""
        await self.send_json({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username']
        })
    
    @database_sync_to_async
    def save_message(self, message):
        # TODO: Implement message saving logic here
        pass

