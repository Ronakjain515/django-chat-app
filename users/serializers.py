from .models import CustomUser
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _


class RegisterUserSerializer(serializers.ModelSerializer):
	"""
	serializer for register user.
	"""
	class Meta:
		model = CustomUser
		fields = ("id", "email", "password", "display_name", "profile_image")

	def save(self, **kwargs):
		user = CustomUser.objects.create_user(
			email=self.validated_data.get("email"),
			password=self.validated_data.get("password")
		)
		user.display_name = self.validated_data.get("display_name")
		if self.validated_data.get("profile_image"):
			user.profile_image = self.validated_data.get("profile_image")
		user.save()
		return user


class LoginSerializer(serializers.Serializer):
	"""
	serializer for user login.
	"""
	email = serializers.EmailField(required=True)
	password = serializers.CharField(required=True)

	default_error_messages = {
		'inactive_account': _('User account is disabled.'),
		'invalid_credentials': _('Email address or password is invalid.'),
		'account_deleted': _("Your account has been deleted. Please contact your admin."),
	}

	def __init__(self, *args, **kwargs):
		"""
		Constructor Function for initializing UserLoginSerializer.
		"""
		super(LoginSerializer, self).__init__(*args, **kwargs)
		self.user = None

	def validate(self, attrs):
		"""
		Function for validating and returning the created instance
		 based on the validated data of the user.
		"""
		self.user = authenticate(username=attrs.pop("email"), password=attrs.pop('password'))
		if self.user:
			if self.user.status == "DELETED":
				raise serializers.ValidationError(self.error_messages['account_deleted'])
			if not self.user.is_active:
				raise serializers.ValidationError(self.error_messages['inactive_account'])
			return attrs
		else:
			raise serializers.ValidationError(self.error_messages['invalid_credentials'])

