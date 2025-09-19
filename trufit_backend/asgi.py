"""
ASGI config for trufit_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""
import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from .custom_middleware.jwt_middleware import JWTAuthMiddleware

from channels.routing import ProtocolTypeRouter, URLRouter
import admin_functions.routing


from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trufit_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(admin_functions.routing.websocket_urlpatterns)
    ),
})

