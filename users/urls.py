from django.urls import path
from .views import (
                        RegisterAPIView,
                        LoginAPIView,
                    )


urlpatterns = [
    path('registerUser', RegisterAPIView.as_view(), name="register-user"),
    path('loginUser', LoginAPIView.as_view(), name="login-user"),
]
