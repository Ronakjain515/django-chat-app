from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication

jwt = JWTAuthentication()


class TokenAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        token = dict(scope["headers"]).get(b"authorization")
        if token:
            raw_token = jwt.get_raw_token(token)
            validated_token = jwt.get_validated_token(raw_token)
            user = await database_sync_to_async(jwt.get_user)(validated_token)
            scope["user"] = user
        else:
            scope["user"] = AnonymousUser()
        return await self.app(scope, receive, send)
