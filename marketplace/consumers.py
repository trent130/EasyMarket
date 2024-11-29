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
        await self.send(text_data=json.dumps(event))
