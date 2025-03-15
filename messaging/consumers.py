import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Chat, finalMessage
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_chat(self, chat_id):
        return Chat.objects.filter(id=chat_id).first()

    @database_sync_to_async
    def get_sender(self, sender_id):
        return get_user_model().objects.filter(id=sender_id).first()

    @database_sync_to_async
    def create_message(self, chat, sender, message):
        return finalMessage.objects.create(chat=chat, sender=sender, text=message)

    async def connect(self):
        
        try:
            self.chat_id = self.scope['url_route']['kwargs']['chat_id']
            self.chat_group_name = f'chat_{self.chat_id}'

            await get_channel_layer().group_add(
                self.chat_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"Connection established for chat: {self.chat_id}")
        except Exception as e:
            logger.error(f"Error in connection: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            await get_channel_layer().group_discard(
                self.chat_group_name,
                self.channel_name
            )
            logger.info(f"Disconnected from chat: {self.chat_id}")
        except Exception as e:
            logger.error(f"Error in disconnection: {str(e)}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message')
            sender_id = text_data_json.get('sender_id')

            if not message or not sender_id:
                await self.send(text_data=json.dumps({
                    'error': 'Invalid data: "message" or "sender_id" is missing.'
                }))
                logger.warning("Invalid message received.")
                return

            chat = await self.get_chat(self.chat_id)
            if not chat:
                await self.send(text_data=json.dumps({'error': 'Chat not found.'}))
                logger.warning(f"Chat not found: {self.chat_id}")
                return

            sender = await self.get_sender(sender_id)
            if not sender:
                await self.send(text_data=json.dumps({'error': 'Sender not found.'}))
                logger.warning(f"Sender not found: {sender_id}")
                return

            message_instance = await self.create_message(chat, sender, message)

            await get_channel_layer().group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'chat_id': self.chat_id,
                    'message': message,
                    'sender': {'id': sender.id, 'username': sender.username},
                    'timestamp': message_instance.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            logger.info(f"Message sent to group {self.chat_group_name}: {message}")

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'Invalid JSON format.'}))
            logger.error("JSON decoding error.")
        except Exception as e:
            logger.error(f"Unhandled error in receive: {str(e)}")
            await self.send(text_data=json.dumps({'error': 'An internal error occurred.'}))

    async def chat_message(self, event):
        try:
            message = event['message']
            sender = event['sender']
            timestamp = event['timestamp']
            chat_id = event['chat_id']

            await self.send(text_data=json.dumps({
                'chat_id': chat_id,
                'message': message,
                'sender': sender,
                'timestamp': timestamp
            }))
        except Exception as e:
            logger.error(f"Error sending chat message: {str(e)}")
