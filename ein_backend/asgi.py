import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path, re_path
from messaging import consumers
import messaging.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ein_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            messaging.routing.websocket_urlpatterns,
            
        )
    ),
})
