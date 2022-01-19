from .models import Chats
from users.utils import (
						 IsTokenValid,
						 ResponseInfo,
						 CustomPagination,
						 )
from .serializers import ChatsListSerializer
from rest_framework.response import Response
from rest_framework.generics import (
									 ListAPIView,
									)
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class ChatListAPIView(ListAPIView):
	"""
	class for add new vitals details.
	"""
	authentication_classes = (JWTAuthentication,)
	permission_classes = (IsAuthenticated, IsTokenValid)
	serializer_class = ChatsListSerializer
	pagination_class = CustomPagination

	def __init__(self, **kwargs):
		"""
		 Constructor function for formatting the web response to return.
		"""
		self.response_format = ResponseInfo().response
		super(ChatListAPIView, self).__init__(**kwargs)

	def get_queryset(self):
		return Chats.objects.filter(sender=self.request.user.id).order_by("updated_at")

	def get(self, request, *args, **kwargs):
		user = self.get_queryset()
		page = self.paginate_queryset(user)
		user_serializer = self.get_serializer(page, many=True)
		return self.get_paginated_response(user_serializer.data)
