"""
ASGI config for trufit_backend project.
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

# 1. Configure Django first
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trufit_backend.settings")
django.setup()

# 2. Now safe to import Django-dependent code
from channels.auth import AuthMiddlewareStack
from trufit_backend.custom_middleware.jwt_middleware import JWTAuthMiddleware
import admin_functions.routing

# 3. Build the application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(   # <-- now your custom middleware is applied
        AuthMiddlewareStack(
            URLRouter(admin_functions.routing.websocket_urlpatterns)
        )
    ),
})
