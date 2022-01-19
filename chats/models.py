from django.db import models
from django.utils import timezone
from users.models import CustomUser


class Chats(models.Model):
	"""
	Class for creating model for Chats.
	"""
	sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sender_user")
	receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="receiver_user")
	is_blocked = models.BooleanField(default=False)
	group_name = models.CharField(max_length=20, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=timezone.now)
	updated_at = models.DateTimeField(auto_now=timezone.now)


class Message(models.Model):
	"""
	Class for creating model for messages.
	"""
	sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sender")
	receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="receiver")
	message = models.TextField(null=False, blank=False)
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=timezone.now)
	updated_at = models.DateTimeField(auto_now=timezone.now)
