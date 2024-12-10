from channels.generic.websocket import AsyncWebsocketConsumer
import json


class MarketplaceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handle WebSocket connection establishment.

        This method is called when a WebSocket connection is initiated.
        It adds the WebSocket to the 'marketplace' group and accepts the connection.

        Attributes:
        - `marketplace_group_name`: The group name for the marketplace WebSocket channel.
        """
        self.marketplace_group_name = 'marketplace'

        # Join marketplace group
        await self.channel_layer.group_add(
            self.marketplace_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.

        This method is called when the WebSocket is closed. It removes
        the WebSocket from the 'marketplace' group.
        
        Args:
        - close_code: The code indicating the reason for the WebSocket disconnection.
        """
        await self.channel_layer.group_discard(
            self.marketplace_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Handle messages received from the WebSocket.

        Parses incoming JSON messages, extracts the 'message' field, and
        broadcasts it to the 'marketplace' group.

        Args:
        - text_data: A JSON string containing the message to broadcast.

        Expected Message Format:
        {
            "message": "Your message here"
        }
        """
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
        """
        Handle messages broadcast to the 'marketplace' group.

        Sends the received message from the group to the WebSocket.

        Args:
        - event: A dictionary containing the 'message' field.

        Example Event Format:
        {
            "message": "Broadcasted message"
        }
        """
        await self.send(text_data=json.dumps(event))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handle WebSocket connection establishment.

        This method is called when a WebSocket connection is initiated.
        It extracts the room and group details from the URL and adds the
        WebSocket to the appropriate room group.

        Attributes:
        - `room_name`: The unique name of the chat room.
        - `room_group_name`: The group name for the chat WebSocket channel.
        - `seller_id`: The ID of the seller associated with the chat room.
        - `product_id`: The ID of the product associated with the chat room.
        """
        self.seller_id = self.scope['url_route']['kwargs']['seller_id']
        self.product_id = self.scope['url_route']['kwargs']['product_id']

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.

        This method is called when the WebSocket is closed. It removes
        the WebSocket from the chat room group.

        Args:
        - close_code: The code indicating the reason for the WebSocket disconnection.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Handle messages received from the WebSocket.

        Parses incoming JSON messages, extracts the 'message' field, and
        broadcasts it to the room group.

        Args:
        - text_data: A JSON string containing the message to broadcast.

        Expected Message Format:
        {
            "message": "Your message here"
        }
        """
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
        """
        Handle messages broadcast to the chat room group.

        Sends the received message from the group to the WebSocket.

        Args:
        - event: A dictionary containing the 'message' field.

        Example Event Format:
        {
            "message": "Broadcasted message"
        }
        """
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
