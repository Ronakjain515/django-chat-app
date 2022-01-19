import json
from .models import (
                     Chats,
                    )
from users.models import CustomUser
from asgiref.sync import async_to_sync
from .serializers import MessageSerializer
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer


class SyncChatConsumer(JsonWebsocketConsumer):
    def __init__(self):
        self.room_group_name = ""
        super(SyncChatConsumer, self).__init__()

    def connect(self):
        sender_obj = self.scope["user"]
        sender_id = int(sender_obj.id)
        all_chats = Chats.objects.filter(sender=sender_id)
        for chat in all_chats:
            if not chat.is_blocked:
                self.room_group_name = 'chat_%s' % chat.group_name
                # Join room group
                async_to_sync(self.channel_layer.group_add)(
                    self.room_group_name,
                    self.channel_name
                )
        self.accept()

    def receive_json(self, content, **kwargs):
        sender_obj = self.scope["user"]
        receiver_id = int(content['receiver_id'])
        sender_id = int(sender_obj.id)
        receiver_obj = CustomUser.objects.get(id=receiver_id)
        try:
            chat = Chats.objects.get(sender=sender_id, receiver=receiver_id)
        except Chats.DoesNotExist:
            group_name = str(int(((sender_id + receiver_id) * (sender_id + receiver_id + 1)) / 2))
            chat = Chats(sender=sender_obj, receiver=receiver_obj, group_name=group_name)
            chat.save()
            receiver_chat = Chats(sender=receiver_obj, receiver=sender_obj, group_name=group_name)
            receiver_chat.save()
            async_to_sync(self.channel_layer.group_add)(
                "chat_" + chat.group_name,
                self.channel_name
            )
        msg_data = {"sender": sender_id, "receiver": receiver_id, "message": content["message"]}
        msg_serializer = MessageSerializer(data=msg_data)
        msg_serializer.is_valid(raise_exception=True)
        msg_serializer.save()

        async_to_sync(self.channel_layer.group_send)(
            "chat_" + chat.group_name,
            {
                'type': 'send_message',
                'data': msg_serializer.data
            }
        )

    def disconnect(self, code):
        pass

    def send_message(self, event):
        data = event['data']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'data': data
        }))


class ChatConsumer(WebsocketConsumer):
    def __init__(self):
        self.room_group_name = ""
        super(ChatConsumer, self).__init__()

    def connect(self):
        sender_obj = self.scope["user"]
        sender = int(sender_obj.id)
        all_chats = Chats.objects.filter(sender=sender)
        for this_chats in all_chats:
            if not this_chats.is_blocked:
                self.room_group_name = 'chat_%s' % this_chats.group_name

                # Join room group
                async_to_sync(self.channel_layer.group_add)(
                    self.room_group_name,
                    self.channel_name
                )
        self.accept()
        # except CustomUser.DoesNotExist:
        #     self.close()

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )
        except TypeError:
            pass

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        receiver = int(text_data_json['receiver_id'])
        sender_obj = self.scope["user"]
        sender = int(sender_obj.id)
        try:
            receiver_obj = CustomUser.objects.get(id=receiver)
            chat = Chats.objects.get(sender=sender, receiver=receiver)
        except Chats.DoesNotExist:
            group_name = str(int(((sender + receiver) * (sender + receiver + 1)) / 2))
            chat = Chats(sender=sender_obj, receiver=receiver_obj, group_name=group_name)
            chat.save()
            oppo_chat = Chats(sender=receiver_obj, receiver=sender_obj, group_name=group_name)
            oppo_chat.save()
            async_to_sync(self.channel_layer.group_add)(
                "chat_" + chat.group_name,
                self.channel_name
            )
        except CustomUser.DoesNotExist:
            self.close()

        data = {"sender": self.scope["user"].id, "receiver": receiver, "message": message}
        serializer = MessageSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        async_to_sync(self.channel_layer.group_send)(
            "chat_" + chat.group_name,
            {
                'type': 'chat_message',
                'data': serializer.data
            }
        )

    def chat_message(self, event):
        data = event['data']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'data': data
        }))


# class ChatConsumer(WebsocketConsumer):
#     def __init__(self):
#         self.room_group_name = ""
#         self.receiver = None
#         super(ChatConsumer, self).__init__()
#
#     def connect(self):
#         receiver = self.scope['url_route']['kwargs']['receiver_id']
#         try:
#             receiver_obj = CustomUser.objects.get(id=receiver)
#             sender_obj = self.scope["user"]
#
#             sender = int(sender_obj.id)
#             try:
#                 chats = Chats.objects.get(sender=sender, receiver=receiver)
#             except Chats.DoesNotExist:
#                 group_name = str(int(((sender + receiver) * (sender + receiver + 1)) / 2))
#                 chats = Chats(sender=sender_obj, receiver=receiver_obj, group_name=group_name)
#                 chats.save()
#
#             if not chats.is_blocked:
#                 self.room_group_name = 'chat_%s' % chats.group_name
#                 self.receiver = receiver_obj
#
#                 # Join room group
#                 async_to_sync(self.channel_layer.group_add)(
#                     self.room_group_name,
#                     self.channel_name
#                 )
#                 self.accept()
#             else:
#                 self.close()
#         except CustomUser.DoesNotExist:
#             self.close()
#
#     def disconnect(self, close_code):
#         try:
#             async_to_sync(self.channel_layer.group_discard)(
#                 self.room_group_name,
#                 self.channel_name
#             )
#         except TypeError:
#             pass
#
#     def receive(self, text_data=None, bytes_data=None, **kwargs):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#
#         data = {"sender": self.scope["user"].id, "receiver": self.receiver.id, "message": message}
#         serializer = MessageSerializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'data': serializer.data
#             }
#         )
#
#     def chat_message(self, event):
#         data = event['data']
#
#         # Send message to WebSocket
#         self.send(text_data=json.dumps({
#             'data': data
#         }))
