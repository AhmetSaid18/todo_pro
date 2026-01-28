import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Kullanıcı login olmuş mu? (Channels Auth Middleware ile gelecek)
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
        else:
            # Kullanıcıya özel oda: user_ID
            self.room_group_name = f'user_{self.user.id}'
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
             await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        # Redis'ten gelen mesajı WebSocket'e ilet
        message = event['message']
        await self.send(text_data=json.dumps(message))
