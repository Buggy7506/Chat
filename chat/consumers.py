import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message, MessageReaction
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.friend_username = self.scope["url_route"]["kwargs"]["username"]
        self.room_name = self.get_room_name(self.user.username, self.friend_username)
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        typing = data.get("typing")
        emoji = data.get("emoji")
        message_id = data.get("message_id")
        seen = data.get("seen")

        if 'file' in data:
            await self.save_message_file(self.user.username, self.friend_username, data['file'])

        if typing is not None:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_notification",
                    "sender": self.user.username,
                }
            )

        elif message:
            await self.save_message(self.user.username, self.friend_username, message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": self.user.username,
                }
            )

        elif emoji and message_id:
            await self.add_reaction(message_id, emoji)

        elif seen and message_id:
            await self.mark_message_as_seen(message_id)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
            "sender": event["sender"],
        }))

    async def typing_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "sender": event["sender"],
        }))

    async def send_reaction(self, event):
        await self.send(text_data=json.dumps({
            "type": "reaction",
            "message_id": event["message_id"],
            "emoji": event["emoji"],
            "user": event["user"],
        }))

    async def message_seen(self, event):
        await self.send(text_data=json.dumps({
            "type": "seen",
            "message_id": event["message_id"],
        }))

    @database_sync_to_async
    def save_message(self, sender, receiver, message):
        sender_user = User.objects.get(username=sender)
        receiver_user = User.objects.get(username=receiver)
        Message.objects.create(sender=sender_user, receiver=receiver_user, content=message)

    @database_sync_to_async
    def add_reaction(self, message_id, emoji):
        message = Message.objects.get(id=message_id)
        reaction = MessageReaction.objects.create(message=message, user=self.user, emoji=emoji)
        # send reaction after saving
        from asgiref.sync import async_to_sync
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "send_reaction",
                "message_id": message.id,
                "emoji": emoji,
                "user": self.user.username,
            }
        )

    @database_sync_to_async
    def mark_message_as_seen(self, message_id):
        message = Message.objects.get(id=message_id)
        message.seen = True
        message.save()
        # send seen notification after saving
        from asgiref.sync import async_to_sync
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "message_seen",
                "message_id": message.id,
            }
        )

    def get_room_name(self, user1, user2):
        return "_".join(sorted([user1, user2]))

    @database_sync_to_async
    def save_message_file(self, sender, receiver, file_data):
        # You need to define how you store file_data
        # This is just a placeholder
        sender_user = User.objects.get(username=sender)
        receiver_user = User.objects.get(username=receiver)
        Message.objects.create(sender=sender_user, receiver=receiver_user, file=file_data)
