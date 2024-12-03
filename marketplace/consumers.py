from channels.generic.websocket import AsyncWebsocketConsumer
import json

class MarketplaceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles WebSocket connections.

        When a WebSocket connection is established, this method
        is called. It extracts the room name from the URL route
        and joins the corresponding room group. Finally, it
        accepts the connection.

        See the documentation for `AsyncWebsocketConsumer` for
        more information.
        """
        self.marketplace_group_name = 'marketplace'

        # Join marketplace group
        await self.channel_layer.group_add(
            self.marketplace_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave marketplace group
        """
        Handles WebSocket disconnections.

        When a WebSocket connection is disconnected, this method
        is called. It leaves the marketplace group and discards the
        channel name from the marketplace group.

        See the documentation for `AsyncWebsocketConsumer` for
        more information.
        """
        await self.channel_layer.group_discard(
            self.marketplace_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """ 
        Handle incoming messages
        Handles incoming messages from WebSocket
        
        The incoming message must be a JSON string containing
        a 'message' key. The message is then broadcast to all
        members of the marketplace group.
        
        Example incoming message:
        {
             'message': 'Hello, world!'
         } """
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
        Send message to WebSocket
         
        Handles incoming messages from the marketplace group and
        sends them to the WebSocket.
         
        The incoming message is expected to be a JSON string
        containing a 'message' key. The message is then sent to
        the WebSocket as a JSON string.
        
        Example incoming message:
        {
             'message': 'Hello, world!'
        } """
        await self.send(text_data=json.dumps(event))

class ChatConsumer(AsyncWebsocketConsumer): 
    async def connect(self): 
        """
        Handles WebSocket connections.

        When a WebSocket connection is established, this method
        is called. It extracts the room name from the URL route
        and joins the corresponding room group. Finally, it
        accepts the connection.

        See the documentation for `AsyncWebsocketConsumer` for
        more information.
        """

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
        """
        Handles WebSocket disconnections.

        When a WebSocket connection is disconnected, this method
        is called. It leaves the room group and discards the
        channel name from the room group.

        See the documentation for `AsyncWebsocketConsumer` for
        more information.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Handles incoming messages from WebSocket.

        When a message is received from WebSocket, this method
        is called. It extracts the message from the JSON string
        and sends it to the room group.

        The incoming message is expected to be a JSON string
        containing a 'message' key. The message is then sent to
        the room group as a JSON string.

        Example incoming message:
        {
            'message': 'Hello, world!'
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
        Handles messages sent from the room group.

        When a message is sent from the room group, this method
        is called. It extracts the message from the JSON string
        and sends it to the WebSocket.

        The incoming message is expected to be a JSON string
        containing a 'message' key. The message is then sent to
        the WebSocket as a JSON string.

        Example incoming message:
        {
            'message': 'Hello, world!'
        }
        """
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))