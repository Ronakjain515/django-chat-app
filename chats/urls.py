from django.urls import path
from .views import (
                     ChatListAPIView,
                    )


urlpatterns = [
    path('chatList', ChatListAPIView.as_view(), name="chatList"),
]
