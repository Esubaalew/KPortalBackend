from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from channels.auth import AuthMiddlewareStack
import chat.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(
        chat.routing.websocket_urlpatterns
    )),
})
