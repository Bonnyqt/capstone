import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_id = data.get('user_id')
        is_online = data.get('is_online')

        # Broadcast status update to all connected clients
        await self.channel_layer.group_send(
            "online_status", {
                'type': 'status_update',
                'user_id': user_id,
                'is_online': is_online
            }
        )

    async def status_update(self, event):
        user_id = event['user_id']
        is_online = event['is_online']

        # Send real-time status update to WebSocket client
        await self.send(text_data=json.dumps({
            'user_id': user_id,
            'is_online': is_online,
        }))
