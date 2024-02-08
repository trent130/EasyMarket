# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'chat_room'
        self.room_group_name = 'chat_room'

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
        # Receive encrypted message from WebSocket
        text_data_json = json.loads(text_data)
        encrypted_message = text_data_json['encrypted_message']
        sender_username = text_data_json['username']

        # Decrypt message using AES
        key = b'supersecretkey'  # Same key used for encryption
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted_message = unpad(cipher.decrypt(b64decode(encrypted_message)), AES.block_size).decode('utf-8')

        # Broadcast decrypted message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': sender_username,
                'message': decrypted_message
            }
        )


    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def typing_status(self, event):
        # Send typing status to WebSocket
        await self.send(text_data=json.dumps(event))


