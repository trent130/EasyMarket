from channels.generic.websocket import AsyncWebsocketConsumer
import json

class MarketplaceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.marketplace_group_name = 'marketplace'

        # Join marketplace group
        await self.channel_layer.group_add(
            self.marketplace_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave marketplace group
        await self.channel_layer.group_discard(
            self.marketplace_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming messages
        # Handles incoming messages from WebSocket
        #
        # The incoming message must be a JSON string containing
        # a 'message' key. The message is then broadcast to all
        # members of the marketplace group.
        #
        # Example incoming message:
        # {
        #     'message': 'Hello, world!'
        # }
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Broadcast message to marketplace group
        await self.channel_layer.group_send(
            self.marketplace_group_name,
            {
                'type': 'marketplace_message',
                'message': message
            }
        )

    async def marketplace_message(self, event):
        # Send message to WebSocket
        # Send message to WebSocket
        # 
        # Handles incoming messages from the marketplace group and
        # sends them to the WebSocket.
        # 
        # The incoming message is expected to be a JSON string
        # containing a 'message' key. The message is then sent to
        # the WebSocket as a JSON string.
        # 
        # Example incoming message:
        # {
        #     'message': 'Hello, world!'
        # }
        await self.send(text_data=json.dumps(event))

class ChatConsumer(AsyncWebsocketConsumer): 
    async def connect(self): 
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))