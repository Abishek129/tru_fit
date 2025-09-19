from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
class OrderConsumer(WebsocketConsumer):
    def connect(self):
        #user = self.scope["user"]
        self.accept()
        print("WebSocket connected  ")

    def disconnect(self, close_code):
        print("WebSocket disconnected")
    def personal_message(self, event):
        self.send(text_data=json.dumps({
            "message": event["message"]
        }))
