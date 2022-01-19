from .utils import (
                    ResponseInfo,
                    get_tokens_for_user,
                    )
from utility import messages
from rest_framework import status
from rest_framework.response import Response
from .serializers import (
                            RegisterUserSerializer,
                            LoginSerializer,
                            )
from django.http import HttpResponse
from rest_framework.generics import (
                                        CreateAPIView
                                    )
from rest_framework_simplejwt.authentication import JWTAuthentication


class RegisterAPIView(CreateAPIView):
    """
    Register User.
    """
    permission_classes = ()
    authentication_classes = ()
    serializer_class = RegisterUserSerializer

    def __init__(self, **kwargs):
        """
         Constructor function for formatting the web response to return.
        """
        self.response_format = ResponseInfo().response
        super(RegisterAPIView, self).__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        user_serializer = self.get_serializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user_serializer.save()
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["error"] = None
            self.response_format["data"] = user_serializer.data
            self.response_format["message"] = [messages.SUCCESS]
        return Response(data=self.response_format, status=status.HTTP_200_OK)


class LoginAPIView(CreateAPIView):
    """
    Login user.
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = LoginSerializer

    def __init__(self, **kwargs):
        """
         Constructor function for formatting the web response to return.
        """
        self.response_format = ResponseInfo().response
        super(LoginAPIView, self).__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        login_serializer = self.get_serializer(data=request.data)
        if login_serializer.is_valid(raise_exception=True):
            user = login_serializer.user
            jwt_token = get_tokens_for_user(user)
            data = {
                "id": user.id,
                "token": jwt_token
            }
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["error"] = None
            self.response_format["data"] = data
            self.response_format["message"] = [messages.LOGIN_SUCCESS]
        return Response(self.response_format)
