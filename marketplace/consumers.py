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
    """Consumer for per-conversation real-time chat."""

    async def connect(self):
        await super().connect()
        # room_name is expected to be the conversation ID
        self.conversation_id = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.conversation_id}'

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def process_message(self, data):
        content = data.get('message', '').strip()
        if not content or not self.user.is_authenticated:
            return

        message = await self.save_message(content)
        if not message:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': message['id'],
                'content': message['content'],
                'sender_id': message['sender_id'],
                'username': self.user.username,
                'created_at': message['created_at'],
            }
        )

    async def chat_message(self, event):
        await self.send_json({
            'type': 'chat_message',
            'id': event['message_id'],
            'content': event['content'],
            'sender_id': event['sender_id'],
            'username': event['username'],
            'created_at': event['created_at'],
        })

    @database_sync_to_async
    def save_message(self, content):
        from chat.models import Conversation, Message
        try:
            conversation = Conversation.objects.get(
                id=self.conversation_id,
                participants=self.user
            )
            msg = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                content=content,
            )
            Conversation.objects.filter(pk=conversation.pk).update(updated_at=msg.created_at)
            return {
                'id': msg.id,
                'content': msg.content,
                'sender_id': self.user.id,
                'created_at': msg.created_at.isoformat(),
            }
        except Conversation.DoesNotExist:
            return None

