from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from jwt.exceptions import InvalidTokenError
from asgiref.sync import sync_to_async

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]

        if token:
            try:
                validated_token = JWTAuthentication().get_validated_token(token)
                # ✅ Run get_user in thread-safe context
                user = await sync_to_async(JWTAuthentication().get_user)(validated_token)
                scope["user"] = user
            except InvalidTokenError:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
