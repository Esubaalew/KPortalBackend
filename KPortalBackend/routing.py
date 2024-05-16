from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
import chat.routing

application = ProtocolTypeRouter({
    'websocket': URLRouter(
        chat.routing.websocket_urlpatterns
    ),
})
