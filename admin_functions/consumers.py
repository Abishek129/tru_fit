from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # Join a test group so external calls can reach you
        await self.channel_layer.group_add("test_group", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("test_group", self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Echo back any message sent by client
        await self.send(text_data=json.dumps({"echo": text_data}))

    # Custom handler for test messages
    async def test_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "test_message",
            "message": event["message"]
        }))
