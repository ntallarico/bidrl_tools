import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OpenItemsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # Handle incoming data and send updates
        await self.send(text_data=json.dumps({
            'message': 'Data updated'
        }))