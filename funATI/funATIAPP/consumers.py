import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["user"].id
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

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
        message = text_data_json["message"]
        receiver_id = text_data_json["receiver_id"]

        # Save message to database
        saved_message = await self.save_message(
            sender_id=self.user_id,
            receiver_id=receiver_id,
            content=message
        )

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender_id": self.user_id,
                "sender_username": self.scope["user"].username,
                "timestamp": saved_message["timestamp"],
                "message_id": saved_message["id"],
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        sender_id = event["sender_id"]
        sender_username = event["sender_username"]
        timestamp = event["timestamp"]
        message_id = event["message_id"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "sender_id": sender_id,
            "sender_username": sender_username,
            "timestamp": timestamp,
            "message_id": message_id,
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=content
        )
        return {
            "id": message.id,
            "timestamp": message.timestamp.isoformat()
        } 