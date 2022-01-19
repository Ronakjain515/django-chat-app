from django.urls import re_path
from .consumers import SyncChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/$', SyncChatConsumer.as_asgi()),
]
