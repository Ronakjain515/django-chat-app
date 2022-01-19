from .models import (
					 Message,
					 Chats
					 )
from rest_framework import serializers


class MessageSerializer(serializers.ModelSerializer):
	"""
	Serializer class for message.
	"""
	class Meta:
		model = Message
		fields = "__all__"


class ChatsListSerializer(serializers.ModelSerializer):
	"""
	Serializer class for Chats list.
	"""
	receiver_id = serializers.CharField(source="receiver.id")
	display_name = serializers.CharField(source="receiver.display_name")
	profile_image = serializers.CharField(source="receiver.profile_image")
	message = serializers.SerializerMethodField()

	def get_message(self, obj):
		return 1

	class Meta:
		model = Chats
		fields = ("id", "receiver_id", "display_name", "profile_image", "message")
